from __future__ import print_function
import sys

if len(sys.argv) != 5:
    print("Usage: python ClearnNotedown.py input.md > output.md")

with open(sys.argv[1]) as f:
    for line in f:
        if line.startswith('```'):
            print('```')
        else:
            print(line, end="")
