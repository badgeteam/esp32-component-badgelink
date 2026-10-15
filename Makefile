# General targets

.PHONY: all
all: format

# Formatting

.PHONY: format
format:
	find . -path ./nanopb -prune -o -name 'badgelink.pb.*' -prune -o \( -iname '*.h' -o -iname '*.c' -o -iname '*.cpp' \) -print | xargs clang-format -i
