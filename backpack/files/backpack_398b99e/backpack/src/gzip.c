#include "gzip.h"
#include <zlib.h>
#include <stdio.h>
#include <string.h>

const char *gzip_error_string(GzipError err) {
    switch (err) {
        case GZIP_OK:             return NULL;
        case GZIP_ERR_TOO_SHORT:  return "data too short";
        case GZIP_ERR_INVALID_ID1: return "Not a gzip file: invalid header: bad ID1";
        case GZIP_ERR_INVALID_ID2: return "Not a gzip file: invalid header: bad ID2";
        case GZIP_ERR_INVALID_CM: return "Bad gzip file: invalid header: bad CM";
        case GZIP_ERR_INVALID_FLG: return "Bad gzip file: invalid header: bad FLG";
        case GZIP_ERR_INVALID_XFL: return "Bad gzip file: invalid header: only fast compression";
        case GZIP_ERR_INVALID_OS: return "Bad gzip file: invalid header: not unix";
        case GZIP_ERR_PARSE_FAILED: return "parse failed";
        default:                  return "unknown error";
    }
}

static uint32_t read_le32(const unsigned char *data) {
    return (uint32_t)data[0] |
           ((uint32_t)data[1] << 8) |
           ((uint32_t)data[2] << 16) |
           ((uint32_t)data[3] << 24);
}

static int read_fname(const unsigned char *data, size_t len, size_t *pos, 
                      char *out, size_t out_size, size_t max_len) {
    size_t start = *pos;
    size_t count = 0;
    
    while (*pos < len && count < max_len) {
        unsigned char c = data[*pos];
        if (c == '\0') {
            break;
        }
        (*pos)++;
        count++;
    }
    
    if (count == 0) {
        return 0;
    }
    
    if (out != NULL && out_size > 0) {
        size_t copy_len = count;
        if (copy_len >= out_size) {
            copy_len = out_size - 1;
        }
        memcpy(out, data + start, copy_len);
        out[copy_len] = '\0';
    }
    
    return 1;
}

GzipHeaderInfo inspect_gzip_header(const unsigned char *data, size_t len) {
    GzipHeaderInfo info;
    memset(&info, 0, sizeof(info));

    if (len < 10) {
        info.error = GZIP_ERR_TOO_SHORT;
        return info;
    }

    if (data[0] != 0x1f) {
        info.error = GZIP_ERR_INVALID_ID1;
        return info;
    }

    if (data[1] != 0x8b) {
        info.error = GZIP_ERR_INVALID_ID2;
        return info;
    }

    if (data[2] != 8) {
        info.error = GZIP_ERR_INVALID_CM;
        return info;
    }

    unsigned char flags = data[3];
    if (flags != 0x08) {
        info.error = GZIP_ERR_INVALID_FLG;
        return info;
    }

    info.mtime = read_le32(data + 4);

    if (data[8] != 0x02) {
        info.error = GZIP_ERR_INVALID_XFL;
        return info;
    }

    if (data[9] != 0x03) {
        info.error = GZIP_ERR_INVALID_OS;
        return info;
    }

    size_t pos = 10;

    if (!read_fname(data, len, &pos, info.name, sizeof(info.name), MAX_GZIP_NAME)) {
        info.error = GZIP_ERR_PARSE_FAILED;
        return info;
    }
    info.has_name = 1;

    info.valid = 1;
    info.error = GZIP_OK;
    return info;
}

int gzip_compress(const unsigned char *input, size_t input_len, const char *embedded_name,
                  uint32_t mtime, Buffer *output) {
    z_stream stream;
    memset(&stream, 0, sizeof(stream));

    if (deflateInit2(&stream, Z_BEST_COMPRESSION, Z_DEFLATED, 15 + 16, 8, Z_DEFAULT_STRATEGY) != Z_OK) {
        fprintf(stderr, "failed to initialize gzip compressor\n");
        return 0;
    }

    gz_header header;
    memset(&header, 0, sizeof(header));
    header.time = mtime;
    header.os = 3;
    header.name = (Bytef *)embedded_name;
    header.name_max = (uInt)(strlen(embedded_name) + 1);

    if (deflateSetHeader(&stream, &header) != Z_OK) {
        fprintf(stderr, "failed to set gzip header\n");
        deflateEnd(&stream);
        return 0;
    }

    size_t bound = deflateBound(&stream, input_len) + strlen(embedded_name) + 64;
    if (!buffer_reserve(output, bound)) {
        fprintf(stderr, "memory allocation failed\n");
        deflateEnd(&stream);
        return 0;
    }

    stream.next_in = (Bytef *)input;
    stream.avail_in = (uInt)input_len;
    stream.next_out = output->data;
    stream.avail_out = (uInt)bound;

    int rc = deflate(&stream, Z_FINISH);
    if (rc != Z_STREAM_END) {
        fprintf(stderr, "gzip compression failed\n");
        deflateEnd(&stream);
        return 0;
    }

    output->len = stream.total_out;
    deflateEnd(&stream);
    return 1;
}

int gzip_decompress(const unsigned char *input, size_t input_len, Buffer *output) {
    z_stream stream;
    memset(&stream, 0, sizeof(stream));

    if (inflateInit2(&stream, 15 + 16) != Z_OK) {
        fprintf(stderr, "failed to initialize gzip decompressor\n");
        return 0;
    }

    stream.next_in = (Bytef *)input;
    stream.avail_in = (uInt)input_len;
    output->len = 0;

    int done = 0;
    while (!done) {
        if (!buffer_reserve(output, output->len + 4096)) {
            fprintf(stderr, "memory allocation failed\n");
            inflateEnd(&stream);
            return 0;
        }

        stream.next_out = output->data + output->len;
        stream.avail_out = (uInt)(output->cap - output->len);

        int rc = inflate(&stream, Z_NO_FLUSH);
        output->len = stream.total_out;

        switch (rc) {
            case Z_STREAM_END:
                done = 1;
                break;
            case Z_OK:
                break;
            default:
                fprintf(stderr, "ungzip failed\n");
                inflateEnd(&stream);
                return 0;
        }
    }

    inflateEnd(&stream);
    return 1;
}
