#include "server.h"
#include "crypto.h"
#include "gzip.h"

#include <errno.h>
#include <limits.h>
#include <openssl/rand.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

static char g_session_dir[PATH_MAX] = {0};
static uint64_t g_storage_used_bytes = 0;

static void cleanup_session_handler(int signum) {
    (void)signum;
    if (g_session_dir[0] != '\0') {
        remove_directory_recursive(g_session_dir);
    }
    _exit(0);
}

static void setup_cleanup_handlers(void) {
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_handler = cleanup_session_handler;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    
    sigaction(SIGINT, &sa, NULL);
    sigaction(SIGTERM, &sa, NULL);
    sigaction(SIGHUP, &sa, NULL);
    sigaction(SIGPIPE, &sa, NULL);
}

static int storage_has_room_for_blob(size_t blob_size) {
    if (g_storage_used_bytes > MAX_TOTAL_STORAGE_SIZE) {
        return 0;
    }
    if ((uint64_t)blob_size > MAX_TOTAL_STORAGE_SIZE - g_storage_used_bytes) {
        return 0;
    }
    return 1;
}

static void storage_record_write(size_t blob_size) {
    g_storage_used_bytes += (uint64_t)blob_size;
}

static void storage_record_delete(uint64_t blob_size) {
    if (blob_size >= g_storage_used_bytes) {
        g_storage_used_bytes = 0;
        return;
    }
    g_storage_used_bytes -= blob_size;
}

int read_line_stream(FILE *stream, char *buffer, size_t buffer_size) {
    size_t len = 0;
    int ch;

    while ((ch = fgetc(stream)) != EOF) {
        if (ch == '\r') {
            continue;
        }
        if (ch == '\n') {
            buffer[len] = '\0';
            return 1;
        }
        if (len + 1 >= buffer_size) {
            fprintf(stderr, "protocol line too long\n");
            return -1;
        }
        buffer[len++] = (char)ch;
    }

    if (ferror(stream)) {
        return -1;
    }
    if (len == 0) {
        return 0;
    }

    buffer[len] = '\0';
    return 1;
}

int read_exact_stream(FILE *stream, unsigned char *buffer, size_t len) {
    size_t offset = 0;
    while (offset < len) {
        size_t chunk = fread(buffer + offset, 1, len - offset, stream);
        if (chunk == 0) {
            return 0;
        }
        offset += chunk;
    }
    return 1;
}

int parse_size_value(const char *text, size_t *value_out) {
    char *end = NULL;
    errno = 0;
    unsigned long long value = strtoull(text, &end, 10);
    if (errno != 0 || end == text || *end != '\0' || value > SIZE_MAX) {
        return 0;
    }
    *value_out = (size_t)value;
    return 1;
}

void server_send_text(FILE *stream, const char *text) {
    fputs(text, stream);
    fflush(stream);
}

void server_send_error(FILE *stream, const char *message) {
    fprintf(stream, "ERR %s\n", message);
    fflush(stream);
}

void server_send_ok(FILE *stream, const char *message) {
    fprintf(stream, "OK %s\n", message);
    fflush(stream);
}

void server_send_prompt(FILE *stream) {
    fputs("backpack> ", stream);
    fflush(stream);
}

void server_send_binary_response(FILE *out, const Buffer *payload) {
    fprintf(out, "OK %zu\n", payload->len);
    if (payload->len > 0) {
        fwrite(payload->data, 1, payload->len, out);
    }
    fflush(out);
}

void server_handle_list(FILE *out, const char *storage_dir) {
    if (!ensure_directory(storage_dir)) {
        server_send_error(out, "failed to access storage");
        return;
    }

    FileList files;
    file_list_init(&files);

    if (!collect_file_entries(storage_dir, &files)) {
        server_send_error(out, "failed to enumerate storage");
        file_list_free(&files);
        return;
    }

    if (files.count == 0) {
        fputs("(empty)\n", out);
        fflush(out);
        file_list_free(&files);
        return;
    }

    for (size_t i = 0; i < files.count; i++) {
        FileEntry *e = &files.items[i];
        char timestamp[32];
        format_timestamp(e->mtime, timestamp, sizeof(timestamp));

        if (e->has_name) {
            fprintf(out, "-rw  %s  %s\n", timestamp, e->name);
        } else {
            fprintf(out, "-e-  %s  %s\n", timestamp, e->name);
        }
    }
    fflush(out);

    file_list_free(&files);
}

void server_handle_get(FILE *out, const char *storage_dir, const char *name) {
    const char *id = find_id_by_name(storage_dir, name);
    if (id == NULL) {
        fprintf(out, "error: file '%s' not found\n", name);
        fflush(out);
        return;
    }

    Buffer blob;
    Buffer decrypted;
    Buffer plain;
    buffer_init(&blob);
    buffer_init(&decrypted);
    buffer_init(&plain);

    if (!load_blob(storage_dir, id, &blob)) {
        fprintf(out, "error: failed to load '%s'\n", name);
        fflush(out);
        goto cleanup;
    }

    if (!aes_decrypt_cbc(blob.data, blob.len, &decrypted)) {
        fprintf(out, "error: failed to decrypt '%s'\n", name);
        fflush(out);
        goto cleanup;
    }

    GzipHeaderInfo info = inspect_gzip_header(decrypted.data, decrypted.len);
    if (!info.valid) {
        const char *err_msg = gzip_error_string(info.error);
        fprintf(out, "error: %s\n", err_msg ? err_msg : "invalid gzip data");
        fflush(out);
        goto cleanup;
    }

    if (!gzip_decompress(decrypted.data, decrypted.len, &plain)) {
        fprintf(out, "error: decompression failed\n");
        fflush(out);
        goto cleanup;
    }

    server_send_binary_response(out, &plain);

cleanup:
    buffer_free(&blob);
    buffer_free(&decrypted);
    buffer_free(&plain);
}

void server_handle_get_raw(FILE *out, const char *storage_dir, const char *name) {
    const char *id = find_id_by_name(storage_dir, name);
    if (id == NULL) {
        fprintf(out, "error: file '%s' not found\n", name);
        fflush(out);
        return;
    }

    Buffer blob;
    buffer_init(&blob);

    if (!fetch_encrypted_buffer(id, storage_dir, &blob)) {
        fprintf(out, "error: failed to load '%s'\n", name);
        fflush(out);
        buffer_free(&blob);
        return;
    }

    server_send_binary_response(out, &blob);
    buffer_free(&blob);
}

void server_handle_rm(FILE *out, const char *storage_dir, const char *name) {
    const char *id = find_id_by_name(storage_dir, name);
    if (id == NULL) {
        fprintf(out, "error: file '%s' not found\n", name);
        fflush(out);
        return;
    }

    char path[PATH_MAX];
    if (!build_storage_path(path, sizeof(path), storage_dir, id)) {
        server_send_error(out, "internal error");
        return;
    }

    struct stat st;
    if (stat(path, &st) != 0) {
        perror("stat");
        fprintf(out, "error: failed to inspect '%s'\n", name);
        fflush(out);
        return;
    }

    if (unlink(path) != 0) {
        perror("unlink");
        fprintf(out, "error: failed to remove '%s'\n", name);
        fflush(out);
        return;
    }

    storage_record_delete((uint64_t)st.st_size);
    fprintf(out, "removed: %s\n", name);
    fflush(out);
}

int server_handle_upload_plain(FILE *in, FILE *out, const char *storage_dir,
                               const char *filename, const char *size_text) {
    uint32_t mtime = current_upload_mtime();
    size_t payload_size = 0;
    
    if (!is_safe_name(filename)) {
        server_send_error(out, "filename must be a printable basename without spaces");
        return 1;
    }
    if (strlen(filename) > MAX_GZIP_NAME) {
        fprintf(out, "error: filename too long (max %d characters)\n", MAX_GZIP_NAME);
        fflush(out);
        return 1;
    }
    if (!parse_size_value(size_text, &payload_size)) {
        server_send_error(out, "invalid size");
        return 1;
    }
    if (payload_size > MAX_FILE_SIZE) {
        fprintf(out, "error: file too large (max %d bytes)\n", MAX_FILE_SIZE);
        fflush(out);
        return 1;
    }

    const char *existing = find_id_by_name(storage_dir, filename);
    if (existing != NULL) {
        fprintf(out, "error: file '%s' already exists\n", filename);
        fflush(out);
        Buffer discard;
        buffer_init(&discard);
        if (buffer_reserve(&discard, payload_size)) {
            discard.len = payload_size;
            read_exact_stream(in, discard.data, payload_size);
        }
        buffer_free(&discard);
        return 1;
    }

    Buffer payload;
    Buffer blob;
    buffer_init(&payload);
    buffer_init(&blob);
    char id[ID_HEX_SIZE + 1];
    int status = 1;

    if (!buffer_reserve(&payload, payload_size)) {
        fprintf(stderr, "memory allocation failed\n");
        server_send_error(out, "memory allocation failed");
        goto cleanup;
    }
    payload.len = payload_size;
    if (!read_exact_stream(in, payload.data, payload_size)) {
        server_send_error(out, "failed to read payload");
        goto cleanup;
    }
    if (!build_plain_blob(payload.data, payload.len, filename, mtime, &blob)) {
        server_send_error(out, "failed to encode file");
        goto cleanup;
    }

    if (!storage_has_room_for_blob(blob.len)) {
        fprintf(out, "error: storage limit exceeded (max %llu bytes total)\n",
                (unsigned long long)MAX_TOTAL_STORAGE_SIZE);
        fflush(out);
        goto cleanup;
    }

    if (!store_blob(storage_dir, &blob, id)) {
        server_send_error(out, "failed to store file");
        goto cleanup;
    }
    storage_record_write(blob.len);

    fprintf(out, "uploaded: %s (%zu bytes)\n", filename, payload.len);
    fflush(out);
    status = 0;

cleanup:
    buffer_free(&blob);
    buffer_free(&payload);
    return status;
}

int server_handle_upload_encrypted(FILE *in, FILE *out, const char *storage_dir,
                                   const char *size_text) {
    size_t payload_size = 0;
    if (!parse_size_value(size_text, &payload_size)) {
        server_send_error(out, "invalid size");
        return 1;
    }
    if (payload_size > MAX_FILE_SIZE) {
        fprintf(out, "error: file too large (max %d bytes)\n", MAX_FILE_SIZE);
        fflush(out);
        return 1;
    }

    Buffer payload;
    Buffer blob;
    buffer_init(&payload);
    buffer_init(&blob);
    char id[ID_HEX_SIZE + 1];
    int status = 1;

    if (!buffer_reserve(&payload, payload_size)) {
        fprintf(stderr, "memory allocation failed\n");
        server_send_error(out, "memory allocation failed");
        goto cleanup;
    }
    payload.len = payload_size;
    if (!read_exact_stream(in, payload.data, payload_size)) {
        server_send_error(out, "failed to read payload");
        goto cleanup;
    }
    if (!build_encrypted_blob(payload.data, payload.len, &blob)) {
        server_send_error(out, "failed to prepare file");
        goto cleanup;
    }

    if (!storage_has_room_for_blob(blob.len)) {
        fprintf(out, "error: storage limit exceeded (max %llu bytes total)\n",
                (unsigned long long)MAX_TOTAL_STORAGE_SIZE);
        fflush(out);
        goto cleanup;
    }

    if (!store_blob(storage_dir, &blob, id)) {
        server_send_error(out, "failed to store file");
        goto cleanup;
    }
    storage_record_write(blob.len);

    char display_name[MAX_GZIP_NAME + 1] = "unknown_file";
    FileEntry entry;
    if (get_file_entry(id, &blob, &entry, 0) && entry.has_name) {
        snprintf(display_name, sizeof(display_name), "%s", entry.name);
    }

    fprintf(out, "uploaded: %s (%zu bytes)\n", display_name, payload.len);
    fflush(out);
    status = 0;

cleanup:
    buffer_free(&blob);
    buffer_free(&payload);
    return status;
}

#define SESSION_ID_SIZE 16

#define FLAG_CONTENT "alfa{XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX}"

static int generate_session_id(char *out, size_t out_size) {
    unsigned char raw[SESSION_ID_SIZE / 2];
    if (RAND_bytes(raw, sizeof(raw)) != 1) {
        return 0;
    }
    if (out_size < SESSION_ID_SIZE + 1) {
        return 0;
    }
    for (size_t i = 0; i < sizeof(raw); i++) {
        snprintf(out + (i * 2), 3, "%02x", raw[i]);
    }
    out[SESSION_ID_SIZE] = '\0';
    return 1;
}

static int store_legacy_flag(const char *storage_dir, size_t *stored_size) {
    Buffer encrypted;
    buffer_init(&encrypted);
    char id[ID_HEX_SIZE + 1];

    if (!aes_encrypt_cbc((const unsigned char *)FLAG_CONTENT, sizeof(FLAG_CONTENT) - 1, &encrypted)) {
        buffer_free(&encrypted);
        return 0;
    }

    if (!store_blob(storage_dir, &encrypted, id)) {
        buffer_free(&encrypted);
        return 0;
    }

    if (stored_size != NULL) {
        *stored_size = encrypted.len;
    }
    buffer_free(&encrypted);
    return 1;
}

int handle_serve(const char *base_storage_dir) {
    if (!ensure_directory(base_storage_dir)) {
        return 1;
    }

    if (!init_session_key()) {
        fprintf(stderr, "failed to initialize session key\n");
        return 1;
    }

    char session_id[SESSION_ID_SIZE + 1];
    if (!generate_session_id(session_id, sizeof(session_id))) {
        fprintf(stderr, "failed to generate session id\n");
        return 1;
    }

    char storage_dir[PATH_MAX];
    snprintf(storage_dir, sizeof(storage_dir), "%s/%s", base_storage_dir, session_id);

    if (!ensure_directory(storage_dir)) {
        return 1;
    }

    g_storage_used_bytes = 0;

    size_t legacy_flag_size = 0;
    if (!store_legacy_flag(storage_dir, &legacy_flag_size)) {
        fprintf(stderr, "failed to store flag\n");
        return 1;
    }
    storage_record_write(legacy_flag_size);

    strncpy(g_session_dir, storage_dir, sizeof(g_session_dir) - 1);
    g_session_dir[sizeof(g_session_dir) - 1] = '\0';
    
    setup_cleanup_handlers();

    int exit_code = 0;

    server_send_text(stdout,
        "Welcome to Digital Backpack!\n"
        "Type 'help' for available commands.\n\n");
    server_send_prompt(stdout);

    char line[1024];
    while (1) {
        int rc = read_line_stream(stdin, line, sizeof(line));
        if (rc == 0) {
            break;
        }
        if (rc < 0) {
            server_send_error(stdout, "invalid command line");
            exit_code = 1;
            break;
        }

        if (line[0] == '\0') {
            server_send_prompt(stdout);
            continue;
        }

        if (strcmp(line, "ls") == 0) {
            server_handle_list(stdout, storage_dir);
            server_send_prompt(stdout);
            continue;
        }

        if (strcmp(line, "help") == 0) {
            server_send_text(stdout,
                "Available commands:\n"
                "  ls                    - list files in backpack\n"
                "  put <name> <size>     - upload file (will be encrypted)\n"
                "  put-raw <size>        - upload pre-encrypted data\n"
                "  get <name>            - download file (decrypted)\n"
                "  get-raw <name>        - download file (encrypted)\n"
                "  rm <name>             - remove file\n"
                "  help                  - show this help\n"
                "  exit                  - close connection\n");
            server_send_prompt(stdout);
            continue;
        }

        if (strcmp(line, "exit") == 0 || strcmp(line, "quit") == 0) {
            server_send_text(stdout, "Goodbye!\n");
            break;
        }

        char *command = strtok(line, " ");
        if (command == NULL) {
            server_send_prompt(stdout);
            continue;
        }

        if (strcmp(command, "put") == 0) {
            char *filename = strtok(NULL, " ");
            char *size_text = strtok(NULL, " ");
            if (filename == NULL || size_text == NULL || strtok(NULL, " ") != NULL) {
                server_send_text(stdout, "usage: put <name> <size>\n");
                server_send_prompt(stdout);
                continue;
            }
            server_handle_upload_plain(stdin, stdout, storage_dir, filename, size_text);
            server_send_prompt(stdout);
            continue;
        }

        if (strcmp(command, "put-raw") == 0) {
            char *size_text = strtok(NULL, " ");
            if (size_text == NULL || strtok(NULL, " ") != NULL) {
                server_send_text(stdout, "usage: put-raw <size>\n");
                server_send_prompt(stdout);
                continue;
            }
            server_handle_upload_encrypted(stdin, stdout, storage_dir, size_text);
            server_send_prompt(stdout);
            continue;
        }

        if (strcmp(command, "get") == 0) {
            char *name = strtok(NULL, " ");
            if (name == NULL || strtok(NULL, " ") != NULL) {
                server_send_text(stdout, "usage: get <name>\n");
                server_send_prompt(stdout);
                continue;
            }
            server_handle_get(stdout, storage_dir, name);
            server_send_prompt(stdout);
            continue;
        }

        if (strcmp(command, "get-raw") == 0) {
            char *name = strtok(NULL, " ");
            if (name == NULL || strtok(NULL, " ") != NULL) {
                server_send_text(stdout, "usage: get-raw <name>\n");
                server_send_prompt(stdout);
                continue;
            }
            server_handle_get_raw(stdout, storage_dir, name);
            server_send_prompt(stdout);
            continue;
        }

        if (strcmp(command, "rm") == 0) {
            char *name = strtok(NULL, " ");
            if (name == NULL || strtok(NULL, " ") != NULL) {
                server_send_text(stdout, "usage: rm <name>\n");
                server_send_prompt(stdout);
                continue;
            }
            server_handle_rm(stdout, storage_dir, name);
            server_send_prompt(stdout);
            continue;
        }

        fprintf(stdout, "unknown command: %s\n", command);
        fflush(stdout);
        server_send_prompt(stdout);
    }

    if (!remove_directory_recursive(storage_dir)) {
        fprintf(stderr, "warning: failed to cleanup session directory: %s\n", storage_dir);
    }

    return exit_code;
}
