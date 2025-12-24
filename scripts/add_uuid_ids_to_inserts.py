#!/usr/bin/env python3
"""
add_uuid_ids_to_inserts.py

Simple utility to add an `id` column and `UUID()` values to multi-row INSERT statements
that omit the primary-key `id`. Use this if you have an original `fulldatabase.sql` and want
to produce a `full_insert.sql` where rows don't rely on triggers.

Limitations: This is a pragmatic, regex-based tool. It works for the typical INSERT ... (col1, col2) VALUES (val1, val2), (val3, val4); pattern. It may fail on highly exotic SQL (nested parentheses inside values, or INSERT...SELECT patterns).

Usage:
    python3 scripts/add_uuid_ids_to_inserts.py input.sql output_fixed.sql

Example:
    python3 scripts/add_uuid_ids_to_inserts.py fulldatabase.sql full_insert_converted.sql

"""
import re
import sys


def process_insert(match: re.Match) -> str:
    table = match.group('table')
    cols = match.group('cols')
    values = match.group('values')

    # If 'id' is already in column list, leave alone
    cols_clean = cols.strip()
    cols_names = [c.strip().strip('`') for c in cols_clean.split(',') if c.strip()]
    if any(c.lower() == 'id' for c in cols_names):
        return match.group(0)

    # Insert id as the first column
    new_cols = 'id, ' + cols_clean

    # Split VALUES into individual tuples by finding top-level '),(' separators
    # Simple approach: split on '),\s*(' and re-wrap parentheses
    tuples = re.split(r"\),\s*\(", values.strip())

    new_tuples = []
    for t in tuples:
        t = t.strip()
        # remove leading '(' or trailing ')' if present
        if t.startswith('('):
            t_inner = t[1:]
        else:
            t_inner = t
        if t_inner.endswith(')'):
            t_inner = t_inner[:-1]

        # Prefix UUID()
        new_t = f"(UUID(), {t_inner})"
        new_tuples.append(new_t)

    new_values = ',\n'.join(new_tuples)

    return f"INSERT INTO {table} ({new_cols}) VALUES\n{new_values};"


def main():
    if len(sys.argv) < 3:
        print('Usage: add_uuid_ids_to_inserts.py input.sql output.sql')
        sys.exit(2)

    in_path = sys.argv[1]
    out_path = sys.argv[2]

    with open(in_path, 'r', encoding='utf-8') as f:
        sql = f.read()

    # Regex to capture INSERT INTO table (cols) VALUES ( ... );
    insert_re = re.compile(
        r"INSERT\s+INTO\s+(?P<table>[`\w\.]+)\s*\((?P<cols>[^)]+)\)\s*VALUES\s*(?P<values>\([^;]+?\))\s*;",
        re.IGNORECASE | re.DOTALL,
    )

    def repl(m):
        try:
            return process_insert(m)
        except Exception as e:
            print('Failed to process an INSERT block for table', m.group('table'), 'error:', e)
            return m.group(0)

    fixed = insert_re.sub(repl, sql)

    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(fixed)

    print(f'Written fixed SQL to {out_path}')


if __name__ == '__main__':
    main()
