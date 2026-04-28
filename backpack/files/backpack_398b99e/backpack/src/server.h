#ifndef BACKPACK_SERVER_H
#define BACKPACK_SERVER_H

#include "common.h"
#include "storage.h"
#include <stdio.h>

int read_line_stream(FILE *stream, char *buffer, size_t buffer_size);
int read_exact_stream(FILE *stream, unsigned char *buffer, size_t len);
int parse_size_value(const char *text, size_t *value_out);

void server_send_text(FILE *stream, const char *text);
void server_send_error(FILE *stream, const char *message);
void server_send_ok(FILE *stream, const char *message);
void server_send_prompt(FILE *stream);
void server_send_binary_response(FILE *out, const Buffer *payload);

void server_handle_list(FILE *out, const char *storage_dir);
void server_handle_get(FILE *out, const char *storage_dir, const char *name);
void server_handle_get_raw(FILE *out, const char *storage_dir, const char *name);
void server_handle_rm(FILE *out, const char *storage_dir, const char *name);
int server_handle_upload_plain(FILE *in, FILE *out, const char *storage_dir,
                               const char *filename, const char *size_text);
int server_handle_upload_encrypted(FILE *in, FILE *out, const char *storage_dir,
                                   const char *size_text);

int handle_serve(const char *storage_dir);

#endif
