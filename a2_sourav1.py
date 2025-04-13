#!/usr/bin/env python3

import subprocess
import sys
import argparse
import os

'''
OPS445 Assignment 2 - Winter 2025
Program: duim.py
Author: Sourav
The python code in this file (duim.py) is original work written by
Sourav. No code in this file is copied from any other source 
except those provided by the course instructor.

Description: A command-line tool that runs `du -d 1 <dir>`, parses the output,
and shows a bar graph representing each subdirectory's disk usage 
as a percentage of the total.

Date: April 2025
'''

def parse_command_args():
    "Parse command-line arguments using argparse"
    parser = argparse.ArgumentParser(
        description="DU Improved -- See Disk Usage Report with bar charts",
        epilog="Copyright 2025"
    )
    parser.add_argument("-l", "--length", type=int, default=20,
                        help="Specify the length of the graph. Default is 20.")
    parser.add_argument("-H", "--human-readable", action="store_true",
                        help="print sizes in human readable format (e.g. 1K 23M 2G)")
    parser.add_argument("target", nargs="?", default=".",
                        help="The directory to scan.")
    return parser.parse_args()

def percent_to_graph(percent, total_chars):
    "Returns a string of '=' and ' ' representing the percent in a bar of total_chars length"
    if not (0 <= percent <= 100):
        raise ValueError("Percent must be between 0 and 100")
    filled = round((percent / 100) * total_chars)
    empty = total_chars - filled
    return "=" * filled + " " * empty

def call_du_sub(location):
    "Calls `du -d 1 <location>` and returns a list of lines"
    try:
        proc = subprocess.Popen(
            ["du", "-d", "1", location],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output, error = proc.communicate()
        if proc.returncode != 0:
            print(f"Error: {error.strip()}", file=sys.stderr)
            return []
        return output.strip().split("\n")
    except Exception as e:
        print(f"Exception occurred: {e}", file=sys.stderr)
        return []

def create_dir_dict(alist):
    "Parses du output lines into a dictionary: {path: size_in_bytes}"
    result = {}
    for line in alist:
        parts = line.split("\t")
        if len(parts) == 2:
            size, path = parts
            try:
                result[path] = int(size)
            except ValueError:
                continue
    return result

def format_size(num_bytes):
    "Convert bytes into a human-readable format"
    for unit in ['B', 'K', 'M', 'G', 'T']:
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} P"

if __name__ == "__main__":
    args = parse_command_args()
    bar_length = args.length
    human_readable = args.human_readable
    target_dir = args.target

    if not os.path.isdir(target_dir):
        print(f"Error: '{target_dir}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    du_output = call_du_sub(target_dir)
    if not du_output:
        sys.exit(1)

    dir_sizes = create_dir_dict(du_output)

    total_size = dir_sizes.get(target_dir, sum(dir_sizes.values()))
    if total_size == 0:
        print("Total size is 0. Nothing to display.")
        sys.exit(0)

    for path, size in dir_sizes.items():
        if path == target_dir:
            continue

        percent = (size / total_size) * 100
        bar = percent_to_graph(percent, bar_length)
        size_str = format_size(size) if human_readable else f"{size} B"
        print(f"{percent:4.0f}% [{bar}] {size_str:>10} {path}")

    total_str = format_size(total_size) if human_readable else f"{total_size} B"
    print(f"\nTotal: {total_str}   {target_dir}")
