#include "storage.h"
#include "crypto.h"
#include "gzip.h"

#include <ctype.h>
#include <dirent.h>
#include <errno.h>
#include <limits.h>
#include <openssl/rand.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/statvfs.h>
#include <time.h>
#include <unistd.h>

const char *path_basename(const char *path) {
    const char *last_slash = strrchr(path, '/');
    return last_slash != NULL ? last_slash + 1 : path;
}

int ensure_directory(const char *path) {
    struct stat st;
    if (stat(path, &st) == 0) {
        if (S_ISDIR(st.st_mode)) {
            return 1;
        }
        fprintf(stderr, "%s exists and is not a directory\n", path);
        return 0;
    }

    if (errno != ENOENT) {
        perror("stat");
        return 0;
    }

    if (mkdir(path, 0700) != 0) {
        perror("mkdir");
        return 0;
    }

    return 1;
}

int remove_directory_recursive(const char *path) {
    DIR *dir = opendir(path);
    if (dir == NULL) {
        if (errno == ENOENT) {
            return 1;
        }
        perror("opendir");
        return 0;
    }

    struct dirent *ent;
    int success = 1;

    while ((ent = readdir(dir)) != NULL) {
        if (strcmp(ent->d_name, ".") == 0 || strcmp(ent->d_name, "..") == 0) {
            continue;
        }

        char full_path[PATH_MAX];
        int written = snprintf(full_path, sizeof(full_path), "%s/%s", path, ent->d_name);
        if (written < 0 || (size_t)written >= sizeof(full_path)) {
            fprintf(stderr, "path too long: %s/%s\n", path, ent->d_name);
            success = 0;
            continue;
        }

        struct stat st;
        if (stat(full_path, &st) != 0) {
            perror("stat");
            success = 0;
            continue;
        }

        if (S_ISDIR(st.st_mode)) {
            if (!remove_directory_recursive(full_path)) {
                success = 0;
            }
        } else {
            if (unlink(full_path) != 0) {
                perror("unlink");
                success = 0;
            }
        }
    }

    closedir(dir);

    if (rmdir(path) != 0) {
        perror("rmdir");
        return 0;
    }

    return success;
}

int read_file(const char *path, Buffer *buffer) {
    FILE *fp = fopen(path, "rb");
    if (fp == NULL) {
        perror(path);
        return 0;
    }

    if (fseek(fp, 0, SEEK_END) != 0) {
        perror("fseek");
        fclose(fp);
        return 0;
    }

    long file_size = ftell(fp);
    if (file_size < 0) {
        perror("ftell");
        fclose(fp);
        return 0;
    }

    if (fseek(fp, 0, SEEK_SET) != 0) {
        perror("fseek");
        fclose(fp);
        return 0;
    }

    if (!buffer_reserve(buffer, (size_t)file_size)) {
        fprintf(stderr, "memory allocation failed\n");
        fclose(fp);
        return 0;
    }

    buffer->len = 0;
    size_t read_len = fread(buffer->data, 1, (size_t)file_size, fp);
    if (read_len != (size_t)file_size) {
        if (ferror(fp)) {
            perror("fread");
            fclose(fp);
            return 0;
        }
    }

    buffer->len = read_len;
    fclose(fp);
    return 1;
}

int write_file(const char *path, const unsigned char *data, size_t len) {
    FILE *fp = fopen(path, "wb");
    if (fp == NULL) {
        perror(path);
        return 0;
    }

    if (len > 0 && fwrite(data, 1, len, fp) != len) {
        perror("fwrite");
        fclose(fp);
        return 0;
    }

    if (fclose(fp) != 0) {
        perror("fclose");
        return 0;
    }

    return 1;
}

int get_storage_info(const char *storage_dir, StorageInfo *info) {
    struct statvfs stat;
    if (statvfs(storage_dir, &stat) != 0) {
        return 0;
    }
    
    info->total_bytes = (uint64_t)stat.f_blocks * stat.f_frsize;
    info->free_bytes = (uint64_t)stat.f_bavail * stat.f_frsize;
    info->used_bytes = info->total_bytes - info->free_bytes;
    return 1;
}

void format_size(uint64_t bytes, char *buf, size_t buf_size) {
    const char *units[] = {"B", "KB", "MB", "GB", "TB"};
    int unit_idx = 0;
    double size = (double)bytes;
    
    while (size >= 1024.0 && unit_idx < 4) {
        size /= 1024.0;
        unit_idx++;
    }
    
    if (unit_idx == 0) {
        snprintf(buf, buf_size, "%lu %s", (unsigned long)bytes, units[unit_idx]);
    } else {
        snprintf(buf, buf_size, "%.1f %s", size, units[unit_idx]);
    }
}

uint32_t current_upload_mtime(void) {
    time_t now = time(NULL);
    if (now < 0) {
        return 0;
    }
    if ((uint64_t)now > UINT32_MAX) {
        return UINT32_MAX;
    }
    return (uint32_t)now;
}

int is_safe_name(const char *name) {
    if (name == NULL || name[0] == '\0') {
        return 0;
    }
    if (strcmp(name, ".") == 0 || strcmp(name, "..") == 0) {
        return 0;
    }
    for (const unsigned char *ptr = (const unsigned char *)name; *ptr != '\0'; ptr++) {
        if (*ptr == '/' || isspace(*ptr) || !isprint(*ptr)) {
            return 0;
        }
    }
    return 1;
}

int generate_file_id(char out[ID_HEX_SIZE + 1]) {
    unsigned char raw[ID_HEX_SIZE / 2];
    if (RAND_bytes(raw, sizeof(raw)) != 1) {
        fprintf(stderr, "failed to generate random identifier\n");
        return 0;
    }

    for (size_t i = 0; i < sizeof(raw); i++) {
        snprintf(out + (i * 2), 3, "%02x", raw[i]);
    }
    out[ID_HEX_SIZE] = '\0';
    return 1;
}

int is_valid_id(const char *id) {
    if (strlen(id) != ID_HEX_SIZE) {
        return 0;
    }
    for (size_t i = 0; i < ID_HEX_SIZE; i++) {
        if (!isxdigit((unsigned char)id[i])) {
            return 0;
        }
    }
    return 1;
}

int build_storage_path(char *dst, size_t dst_size, const char *storage_dir, const char *id) {
    int written = snprintf(dst, dst_size, "%s/%s.bin", storage_dir, id);
    if (written < 0 || (size_t)written >= dst_size) {
        fprintf(stderr, "storage path is too long\n");
        return 0;
    }
    return 1;
}

void file_list_init(FileList *list) {
    list->items = NULL;
    list->count = 0;
    list->cap = 0;
}

void file_list_free(FileList *list) {
    free(list->items);
    list->items = NULL;
    list->count = 0;
    list->cap = 0;
}

int file_list_push(FileList *list, const FileEntry *entry) {
    if (list->count == list->cap) {
        size_t new_cap = list->cap ? list->cap * 2 : 16;
        FileEntry *new_items = realloc(list->items, new_cap * sizeof(*new_items));
        if (new_items == NULL) {
            return 0;
        }
        list->items = new_items;
        list->cap = new_cap;
    }
    list->items[list->count++] = *entry;
    return 1;
}

int collect_storage_files(const char *storage_dir, StringList *entries) {
    DIR *dir = opendir(storage_dir);
    if (dir == NULL) {
        perror(storage_dir);
        return 0;
    }

    struct dirent *ent;
    while ((ent = readdir(dir)) != NULL) {
        if (ent->d_name[0] == '.') {
            continue;
        }

        size_t name_len = strlen(ent->d_name);
        if (name_len <= 4 || strcmp(ent->d_name + name_len - 4, ".bin") != 0) {
            continue;
        }

        if (name_len - 4 != ID_HEX_SIZE) {
            continue;
        }

        char id[ID_HEX_SIZE + 1];
        memcpy(id, ent->d_name, ID_HEX_SIZE);
        id[ID_HEX_SIZE] = '\0';
        if (!is_valid_id(id)) {
            continue;
        }

        if (!string_list_push(entries, id)) {
            fprintf(stderr, "memory allocation failed\n");
            closedir(dir);
            return 0;
        }
    }

    closedir(dir);
    qsort(entries->items, entries->count, sizeof(*entries->items), compare_strings);
    return 1;
}

int store_blob(const char *storage_dir, const Buffer *buffer, char out_id[ID_HEX_SIZE + 1]) {
    char path[PATH_MAX];

    for (int attempt = 0; attempt < 8; attempt++) {
        if (!generate_file_id(out_id)) {
            return 0;
        }
        if (!build_storage_path(path, sizeof(path), storage_dir, out_id)) {
            return 0;
        }

        if (access(path, F_OK) != 0) {
            return write_file(path, buffer->data, buffer->len);
        }
    }

    fprintf(stderr, "failed to allocate unique file identifier\n");
    return 0;
}

int load_blob(const char *storage_dir, const char *id, Buffer *buffer) {
    if (!is_valid_id(id)) {
        fprintf(stderr, "invalid file id: %s\n", id);
        return 0;
    }

    char path[PATH_MAX];
    if (!build_storage_path(path, sizeof(path), storage_dir, id)) {
        return 0;
    }

    return read_file(path, buffer);
}

int build_plain_blob(const unsigned char *input, size_t input_len, const char *embedded_name,
                     uint32_t mtime, Buffer *blob) {
    Buffer gzipped;
    buffer_init(&gzipped);

    int ok = 0;
    if (!gzip_compress(input, input_len, embedded_name, mtime, &gzipped)) {
        goto cleanup;
    }
    if (!aes_encrypt_cbc(gzipped.data, gzipped.len, blob)) {
        goto cleanup;
    }

    ok = 1;

cleanup:
    buffer_free(&gzipped);
    return ok;
}

int build_encrypted_blob(const unsigned char *input, size_t input_len, Buffer *blob) {
    if (!buffer_reserve(blob, input_len)) {
        fprintf(stderr, "memory allocation failed\n");
        return 0;
    }

    if (input_len > 0) {
        memcpy(blob->data, input, input_len);
    }
    blob->len = input_len;
    return 1;
}

int store_plain_buffer(const unsigned char *input, size_t input_len, const char *embedded_name,
                       uint32_t mtime, const char *storage_dir, char out_id[ID_HEX_SIZE + 1]) {
    Buffer encrypted;
    buffer_init(&encrypted);

    int ok = 0;
    if (!ensure_directory(storage_dir)) {
        goto cleanup;
    }
    if (!build_plain_blob(input, input_len, embedded_name, mtime, &encrypted)) {
        goto cleanup;
    }
    if (!store_blob(storage_dir, &encrypted, out_id)) {
        goto cleanup;
    }

    ok = 1;

cleanup:
    buffer_free(&encrypted);
    return ok;
}

int store_encrypted_buffer(const unsigned char *input, size_t input_len, const char *storage_dir,
                           char out_id[ID_HEX_SIZE + 1]) {
    Buffer blob;
    buffer_init(&blob);

    int ok = 0;
    if (!ensure_directory(storage_dir)) {
        goto cleanup;
    }
    if (!build_encrypted_blob(input, input_len, &blob)) {
        goto cleanup;
    }
    if (!store_blob(storage_dir, &blob, out_id)) {
        goto cleanup;
    }

    ok = 1;

cleanup:
    buffer_free(&blob);
    return ok;
}

int fetch_encrypted_buffer(const char *id, const char *storage_dir, Buffer *blob) {
    return load_blob(storage_dir, id, blob);
}

int fetch_plain_buffer(const char *id, const char *storage_dir, Buffer *plain) {
    Buffer blob;
    Buffer decrypted;
    buffer_init(&blob);
    buffer_init(&decrypted);

    int ok = 0;
    if (!load_blob(storage_dir, id, &blob)) {
        goto cleanup;
    }
    if (!aes_decrypt_cbc(blob.data, blob.len, &decrypted)) {
        goto cleanup;
    }
    if (!gzip_decompress(decrypted.data, decrypted.len, plain)) {
        fprintf(stderr, "file %s was not returned because ungzip failed\n", id);
        goto cleanup;
    }

    ok = 1;

cleanup:
    buffer_free(&blob);
    buffer_free(&decrypted);
    return ok;
}

int get_file_entry(const char *id, const Buffer *blob, FileEntry *entry, int unknown_index) {
    memset(entry, 0, sizeof(*entry));
    strncpy(entry->id, id, ID_HEX_SIZE);
    entry->id[ID_HEX_SIZE] = '\0';
    entry->size = blob->len;

    unsigned char prefix[GZIP_PEEK_SIZE];
    if (!decrypt_first_two_blocks(blob->data, blob->len, prefix)) {
        snprintf(entry->name, sizeof(entry->name), "unknown_file_%d", unknown_index);
        entry->has_name = 0;
        return 1;
    }

    GzipHeaderInfo info = inspect_gzip_header(prefix, sizeof(prefix));
    if (!info.valid || !info.has_name) {
        snprintf(entry->name, sizeof(entry->name), "unknown_file_%d", unknown_index);
        entry->has_name = 0;
        return 1;
    }

    strncpy(entry->name, info.name, MAX_GZIP_NAME);
    entry->name[MAX_GZIP_NAME] = '\0';
    entry->mtime = info.mtime;
    entry->has_name = 1;
    return 1;
}

int collect_file_entries(const char *storage_dir, FileList *files) {
    StringList ids;
    string_list_init(&ids);

    if (!collect_storage_files(storage_dir, &ids)) {
        string_list_free(&ids);
        return 0;
    }

    int unknown_counter = 1;
    for (size_t i = 0; i < ids.count; i++) {
        Buffer blob;
        buffer_init(&blob);

        if (load_blob(storage_dir, ids.items[i], &blob)) {
            FileEntry entry;
            if (get_file_entry(ids.items[i], &blob, &entry, unknown_counter)) {
                if (!entry.has_name) {
                    unknown_counter++;
                }
                file_list_push(files, &entry);
            }
        }
        buffer_free(&blob);
    }

    string_list_free(&ids);
    return 1;
}

const char *find_id_by_name(const char *storage_dir, const char *name) {
    static char found_id[ID_HEX_SIZE + 1];
    FileList files;
    file_list_init(&files);

    if (!collect_file_entries(storage_dir, &files)) {
        file_list_free(&files);
        return NULL;
    }

    const char *result = NULL;
    for (size_t i = 0; i < files.count; i++) {
        if (strcmp(files.items[i].name, name) == 0) {
            strncpy(found_id, files.items[i].id, ID_HEX_SIZE);
            found_id[ID_HEX_SIZE] = '\0';
            result = found_id;
            break;
        }
    }

    file_list_free(&files);
    return result;
}

int format_timestamp(uint32_t mtime, char *dst, size_t dst_size) {
    time_t raw = (time_t)mtime;
    struct tm tm_value;
    if (gmtime_r(&raw, &tm_value) == NULL) {
        return snprintf(dst, dst_size, "1970-01-01T00:00:00Z") > 0;
    }

    return strftime(dst, dst_size, "%Y-%m-%dT%H:%M:%SZ", &tm_value) > 0;
}

void print_listing_entry(FILE *stream, const char *id, const Buffer *blob) {
    unsigned char prefix[GZIP_PEEK_SIZE];
    if (!decrypt_first_two_blocks(blob->data, blob->len, prefix)) {
        fprintf(stream, "%s unknown_file\n", id);
        return;
    }

    GzipHeaderInfo info = inspect_gzip_header(prefix, sizeof(prefix));
    if (!info.valid || !info.has_name) {
        fprintf(stream, "%s unknown_file\n", id);
        return;
    }

    char timestamp[96];
    format_timestamp(info.mtime, timestamp, sizeof(timestamp));
    fprintf(stream, "%s %s mtime=%s\n", id, info.name, timestamp);
}
