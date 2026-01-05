#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from lib import render_summary_bar, render_segment_bar

CACHE_FILE = Path("cache.tsv")

cache_entries = defaultdict(list)

for line in CACHE_FILE.read_text().splitlines():
	parts = line.split('\t')
	hash_key = parts[0]
	filename = parts[1]
	timestamp = int(parts[2])
	result = json.loads(parts[3])

	cache_entries[filename].append({
		'timestamp': timestamp,
		'result': result
	})

for filename in sorted(cache_entries.keys()):
	print(f"\n{Path(filename).stem}:")
	entries = sorted(cache_entries[filename], key=lambda x: x['timestamp'])

	# First show all summary bars (red/yellow/green)
	for entry in entries:
		dt = datetime.fromtimestamp(entry['timestamp'])
		date_str = dt.strftime(' %Y-%m-%d %H:%M')
		summary_bar = render_summary_bar(entry['result'])
		print(f"{date_str} {summary_bar}")

	print()

	# Then show all segment bars (gradient green)
	for entry in entries:
		dt = datetime.fromtimestamp(entry['timestamp'])
		date_str = dt.strftime(' %Y-%m-%d %H:%M')
		segment_bar = render_segment_bar(entry['result'])
		print(f"{date_str} {segment_bar}")

print("\033[0m")
