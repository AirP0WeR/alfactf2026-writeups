#ifndef BACKPACK_STORAGE_H
#define BACKPACK_STORAGE_H

#include "common.h"
#include "buffer.h"
#include "gzip.h"
#include <stdio.h>

typedef struct {
    uint64_t total_bytes;
    uint64_t free_bytes;
    uint64_t used_bytes;
} StorageInfo;

typedef struct {
    char id[ID_HEX_SIZE + 1];
    char name[MAX_GZIP_NAME + 1];
    uint32_t mtime;
    size_t size;
    int has_name;
} FileEntry;

typedef struct {
    FileEntry *items;
    size_t count;
    size_t cap;
} FileList;

int ensure_directory(const char *path);
int remove_directory_recursive(const char *path);
int read_file(const char *path, Buffer *buffer);
int write_file(const char *path, const unsigned char *data, size_t len);
const char *path_basename(const char *path);
int is_safe_name(const char *name);
int is_valid_id(const char *id);
int generate_file_id(char out[ID_HEX_SIZE + 1]);
int build_storage_path(char *dst, size_t dst_size, const char *storage_dir, const char *id);
uint32_t current_upload_mtime(void);
int get_storage_info(const char *storage_dir, StorageInfo *info);
void format_size(uint64_t bytes, char *buf, size_t buf_size);

void file_list_init(FileList *list);
void file_list_free(FileList *list);
int file_list_push(FileList *list, const FileEntry *entry);

int collect_storage_files(const char *storage_dir, StringList *entries);
int collect_file_entries(const char *storage_dir, FileList *files);
const char *find_id_by_name(const char *storage_dir, const char *name);

int store_blob(const char *storage_dir, const Buffer *buffer, char out_id[ID_HEX_SIZE + 1]);
int load_blob(const char *storage_dir, const char *id, Buffer *buffer);
int build_plain_blob(const unsigned char *input, size_t input_len, const char *embedded_name,
                     uint32_t mtime, Buffer *blob);
int build_encrypted_blob(const unsigned char *input, size_t input_len, Buffer *blob);

int store_plain_buffer(const unsigned char *input, size_t input_len, const char *embedded_name,
                       uint32_t mtime, const char *storage_dir, char out_id[ID_HEX_SIZE + 1]);
int store_encrypted_buffer(const unsigned char *input, size_t input_len, const char *storage_dir,
                           char out_id[ID_HEX_SIZE + 1]);

int fetch_encrypted_buffer(const char *id, const char *storage_dir, Buffer *blob);
int fetch_plain_buffer(const char *id, const char *storage_dir, Buffer *plain);

int get_file_entry(const char *id, const Buffer *blob, FileEntry *entry, int unknown_index);

void print_listing_entry(FILE *stream, const char *id, const Buffer *blob);
int format_timestamp(uint32_t mtime, char *dst, size_t dst_size);

#endif
