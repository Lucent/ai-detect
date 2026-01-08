#!/usr/bin/env python3
import json
from pathlib import Path
from collections import defaultdict
from lib import render_cache_history

CACHE_FILE = Path("cache.tsv")

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

render_cache_history(cache_entries)
