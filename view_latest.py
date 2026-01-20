#!/usr/bin/env python3
import os
import json
from pathlib import Path
from collections import defaultdict
from dotenv import load_dotenv
from lib import render_summary_bar, render_segment_bar, RESET

load_dotenv()

CACHE_FILE = Path(os.environ["CACHE_FILE"])
FILENAME_WIDTH = 25

cache_entries = defaultdict(list)

for line in CACHE_FILE.read_text().splitlines():
	parts = line.split('\t')
	filename = parts[1]
	timestamp = int(parts[2])
	result = json.loads(parts[3])

	cache_entries[filename].append({
		'timestamp': timestamp,
		'result': result
	})

rows = []
for filename in cache_entries.keys():
	entries = cache_entries[filename]
	latest = max(entries, key=lambda x: x['timestamp'])
	name = Path(filename).stem
	if len(name) > FILENAME_WIDTH:
		name = name[:FILENAME_WIDTH-1] + "…"
	rows.append((name.ljust(FILENAME_WIDTH), latest['result']))

for name, result in rows:
	print(f"{name} {render_summary_bar(result)}")

print()

for name, result in rows:
	print(f"{name} {render_segment_bar(result)}")

print(RESET)
