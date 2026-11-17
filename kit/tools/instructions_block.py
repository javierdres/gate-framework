#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Javier Núñez
"""Writes the SDLC's block in an instruction file of the working folder.

    instructions_block.py <file> <backup file>      the block's body on standard input

The block sits between `<!-- sdlc:begin -->` and `<!-- sdlc:end -->`. The markers do not carry
the system's name, so the block is found again after a rename, and it is rewritten whole on
every install: whatever the person wrote outside it stays as it was. A block in the older
single-marker form (`<!-- sdlc:<name> -->` followed by its lines) is replaced in place.

The file is copied to the backup path before it changes, never when nothing changes. Prints
what it did: created, added, updated, migrated or unchanged.
"""
import io
import os
import re
import shutil
import sys

BEGIN, END = "<!-- sdlc:begin -->", "<!-- sdlc:end -->"
# The older form: one marker with the name, then the block's lines up to a blank line.
OLD = re.compile(r"^<!-- sdlc:(?!begin -->|end -->|open -->)[A-Za-z0-9._-]+ -->\n(?:[^\n]+\n?)*", re.M)


def write(path, text):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip())
        return 2
    path, backup = argv
    body = sys.stdin.read().strip("\n")
    block = "%s\n%s\n%s\n" % (BEGIN, body, END)
    if not os.path.exists(path):
        write(path, block)
        print("created")
        return 0
    with io.open(path, encoding="utf-8") as f:
        text = f.read()
    start, end = text.find(BEGIN), text.find(END)
    if 0 <= start < end:
        stop = end + len(END)
        if text[stop:stop + 1] == "\n":
            stop += 1
        new, what = text[:start] + block + text[stop:], "updated"
    elif OLD.search(text):
        new, what = OLD.sub(lambda m: block, text, count=1), "migrated"
    else:
        new, what = text + ("" if text.endswith("\n") or not text else "\n") + ("\n" if text else "") + block, "added"
    if new == text:
        print("unchanged")
        return 0
    os.makedirs(os.path.dirname(os.path.abspath(backup)), exist_ok=True)
    shutil.copy2(path, backup)
    write(path, new)
    print(what)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
