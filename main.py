#!/usr/bin/env python3
"""Write the excuse entry for make.fun's The Excuse That Almost Works.

The program takes no input and always emits the same single line: the
text a gamer sends the boss to skip work during GTA 6 launch week.
It writes that line to entry.txt inside $MAKEFUN_OUTPUT_DIR (or the
current directory when the variable is unset).

Gates enforced here (and re-checked on the written file):
  * exactly one line of plain text, at most 20 words;
  * 1 to 140 characters, the sealed scorer's bound.
"""

import argparse
import os
import sys

ENTRY = (
    "My wisdom tooth cracked on a popcorn kernel last night, "
    "dentist can only fit me in at 9am today."
)

MAX_WORDS = 20
MAX_CHARS = 140


def word_count(text):
    """Count words the way a reader would: split on whitespace."""
    return len(text.split())


def problems(text):
    """Return a list of gate violations for a candidate entry line."""
    found = []
    if not text.strip():
        found.append("entry is empty or only whitespace")
    if text != text.strip():
        found.append("entry has leading or trailing whitespace")
    if "\n" in text.strip():
        found.append("entry must be a single line")
    if word_count(text) > MAX_WORDS:
        found.append(
            "entry has %d words, over the %d-word limit"
            % (word_count(text), MAX_WORDS)
        )
    if not 1 <= len(text) <= MAX_CHARS:
        found.append(
            "entry has %d characters, outside the 1-%d range"
            % (len(text), MAX_CHARS)
        )
    return found


def check_entry():
    """Validate the entry line in memory; exit non-zero on any violation."""
    bad = problems(ENTRY)
    if bad:
        for item in bad:
            print("check failed: %s" % item, file=sys.stderr)
        return 1
    print(
        "check ok: %d words, %d characters"
        % (word_count(ENTRY), len(ENTRY))
    )
    return 0


def write_entry(out_dir):
    """Write entry.txt and re-validate the file bytes that landed on disk."""
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.txt")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(ENTRY + "\n")
    with open(path, encoding="utf-8") as handle:
        written = handle.read()
    if written != ENTRY + "\n":
        print("error: entry.txt does not match the entry line", file=sys.stderr)
        return 1
    bad = problems(written.rstrip("\n"))
    if bad:
        for item in bad:
            print("check failed: %s" % item, file=sys.stderr)
        return 1
    if len(written) > MAX_CHARS + 1:
        print("error: entry.txt is over the character gate", file=sys.stderr)
        return 1
    print("wrote %s" % path)
    return 0


def self_test():
    """Internal checks: gate, byte round-trip, and flag behaviour."""
    if check_entry() != 0:
        return 1
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        if write_entry(tmp) != 0:
            return 1
        with open(os.path.join(tmp, "entry.txt"), encoding="utf-8") as handle:
            if handle.read() != ENTRY + "\n":
                print("self-test failed: round-trip mismatch", file=sys.stderr)
                return 1
    if problems("") == []:
        print("self-test failed: empty entry passed validation", file=sys.stderr)
        return 1
    if problems("word " * 21) == []:
        print("self-test failed: 21-word entry passed validation", file=sys.stderr)
        return 1
    print("self-test ok")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="validate the entry line without writing it")
    parser.add_argument("--self-test", action="store_true",
                        help="run internal validation checks")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test()
    if args.check:
        return check_entry()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", ".")
    return write_entry(out_dir)


if __name__ == "__main__":
    sys.exit(main())
