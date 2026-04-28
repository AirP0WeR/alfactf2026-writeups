#include "buffer.h"
#include <stdlib.h>
#include <string.h>

void buffer_init(Buffer *buffer) {
    buffer->data = NULL;
    buffer->len = 0;
    buffer->cap = 0;
}

void buffer_free(Buffer *buffer) {
    free(buffer->data);
    buffer->data = NULL;
    buffer->len = 0;
    buffer->cap = 0;
}

int buffer_reserve(Buffer *buffer, size_t needed) {
    if (needed <= buffer->cap) {
        return 1;
    }

    size_t new_cap = buffer->cap ? buffer->cap : 256;
    while (new_cap < needed) {
        if (new_cap > SIZE_MAX / 2) {
            return 0;
        }
        new_cap *= 2;
    }

    unsigned char *new_data = realloc(buffer->data, new_cap);
    if (new_data == NULL) {
        return 0;
    }

    buffer->data = new_data;
    buffer->cap = new_cap;
    return 1;
}

void string_list_init(StringList *list) {
    list->items = NULL;
    list->count = 0;
    list->cap = 0;
}

void string_list_free(StringList *list) {
    for (size_t i = 0; i < list->count; i++) {
        free(list->items[i]);
    }
    free(list->items);
    list->items = NULL;
    list->count = 0;
    list->cap = 0;
}

int string_list_push(StringList *list, const char *value) {
    if (list->count == list->cap) {
        size_t new_cap = list->cap ? list->cap * 2 : 16;
        char **new_items = realloc(list->items, new_cap * sizeof(*new_items));
        if (new_items == NULL) {
            return 0;
        }
        list->items = new_items;
        list->cap = new_cap;
    }

    char *copy = strdup(value);
    if (copy == NULL) {
        return 0;
    }

    list->items[list->count++] = copy;
    return 1;
}

int compare_strings(const void *lhs, const void *rhs) {
    const char *const *left = lhs;
    const char *const *right = rhs;
    return strcmp(*left, *right);
}
