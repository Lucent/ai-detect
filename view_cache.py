#!/usr/bin/env python3
import os
import json
from pathlib import Path
from collections import defaultdict
from dotenv import load_dotenv
from lib import render_cache_history

load_dotenv()

CACHE_FILE = Path(os.environ["CACHE_FILE"])

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
