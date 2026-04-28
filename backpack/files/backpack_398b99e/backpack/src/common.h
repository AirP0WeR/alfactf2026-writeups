#ifndef BACKPACK_COMMON_H
#define BACKPACK_COMMON_H

#define _POSIX_C_SOURCE 200809L

#include <stdint.h>
#include <stddef.h>

#define AES_KEY_SIZE 16
#define AES_BLOCK_SIZE 16
#define ID_HEX_SIZE 32
#define GZIP_PEEK_SIZE 32
#define MAX_GZIP_NAME 16
#define MAX_FILE_SIZE (10 * 1024 * 1024)
#define MAX_TOTAL_STORAGE_SIZE (1024ULL * 1024ULL * 1024ULL)

extern unsigned char g_session_key[AES_KEY_SIZE];

int init_session_key(void);

#endif
