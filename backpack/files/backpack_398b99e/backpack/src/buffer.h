#ifndef BACKPACK_BUFFER_H
#define BACKPACK_BUFFER_H

#include "common.h"
#include <stddef.h>

typedef struct {
    unsigned char *data;
    size_t len;
    size_t cap;
} Buffer;

typedef struct {
    char **items;
    size_t count;
    size_t cap;
} StringList;

void buffer_init(Buffer *buffer);
void buffer_free(Buffer *buffer);
int buffer_reserve(Buffer *buffer, size_t needed);

void string_list_init(StringList *list);
void string_list_free(StringList *list);
int string_list_push(StringList *list, const char *value);

int compare_strings(const void *lhs, const void *rhs);

#endif
