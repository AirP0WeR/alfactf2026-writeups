CC ?= cc
CFLAGS ?= -O2 -Wall -Wextra -Wpedantic
LDFLAGS ?=
LDLIBS ?= -lcrypto -lz

TARGET := backpack

SRCS := main.c buffer.c crypto.c gzip.c storage.c server.c
OBJS := $(SRCS:.c=.o)
HDRS := common.h buffer.h crypto.h gzip.h storage.h server.h

.PHONY: all clean

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(LDFLAGS) -o $@ $(OBJS) $(LDLIBS)

%.o: %.c $(HDRS)
	$(CC) $(CFLAGS) -c -o $@ $<

clean:
	rm -f $(TARGET) $(OBJS)
