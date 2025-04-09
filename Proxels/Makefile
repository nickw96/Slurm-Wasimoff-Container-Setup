SHELL=/bin/bash
rootdir=$(realpath ./..)
WASI_SDK_PATH=$(rootdir)/wasi-sdk/wasi-sdk-25.0-x86_64-linux
CC=$(WASI_SDK_PATH)/bin/clang --sysroot=$(WASI_SDK_PATH)/share/wasi-sysroot

default: all

all: proxels proxels_wasm

proxels:
	gcc 04_Proxels_weather.c -o Proxels -lm

proxels_wasm:
	$(CC) 04_Proxels_weather.c -o Proxels.wasm

clean:
	rm Proxels Proxels.wasm
