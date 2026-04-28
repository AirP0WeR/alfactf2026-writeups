#ifndef BACKPACK_GZIP_H
#define BACKPACK_GZIP_H

#include "common.h"
#include "buffer.h"

typedef enum {
    GZIP_OK = 0,
    GZIP_ERR_TOO_SHORT,
    GZIP_ERR_INVALID_ID1,
    GZIP_ERR_INVALID_ID2,
    GZIP_ERR_INVALID_CM,
    GZIP_ERR_INVALID_FLG,
    GZIP_ERR_INVALID_XFL,
    GZIP_ERR_INVALID_OS,
    GZIP_ERR_PARSE_FAILED
} GzipError;

typedef struct {
    int valid;
    int has_name;
    char name[MAX_GZIP_NAME + 1];
    uint32_t mtime;
    GzipError error;
} GzipHeaderInfo;

const char *gzip_error_string(GzipError err);

GzipHeaderInfo inspect_gzip_header(const unsigned char *data, size_t len);

int gzip_compress(const unsigned char *input, size_t input_len, const char *embedded_name,
                  uint32_t mtime, Buffer *output);

int gzip_decompress(const unsigned char *input, size_t input_len, Buffer *output);

#endif
