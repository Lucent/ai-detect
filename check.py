#!/usr/bin/env python3
import sys
import json
import hashlib
from pathlib import Path
from dotenv import load_dotenv
from pangram import Pangram
from lib import *
from collections import defaultdict

load_dotenv()

CACHE_FILE = Path("cache.tsv")

def hash_text(text):
	return hashlib.sha256(text.encode('utf-8')).hexdigest()

def load_cache():
	if not CACHE_FILE.exists():
		return {}
	cache = {}
	for line in CACHE_FILE.read_text().splitlines():
		parts = line.split('\t')
		hash_key = parts[0]
		json_data = parts[3]
		cache[hash_key] = json.loads(json_data)
	return cache

def load_cache_entries(filename_filter):
	cache_entries = defaultdict(list)
	for line in CACHE_FILE.read_text().splitlines():
		parts = line.split('\t')
		filename = parts[1]
		if filename != filename_filter:
			continue
		timestamp = int(parts[2])
		result = json.loads(parts[3])
		cache_entries[filename].append({'timestamp': timestamp, 'result': result})
	return cache_entries

def save_to_cache(text_hash, result, filename, timestamp):
	with CACHE_FILE.open('a') as f:
		f.write(f"{text_hash}\t{filename}\t{timestamp}\t{json.dumps(result)}\n")

def visualize(data):
	print("\n --- AI DETECTION SUMMARY ---\n")
	print(render_summary_bar(data))
	print()

	print(render_colorized_text(data))
	print()

	print(" --- DETAILED SEGMENT ANALYSIS ---\n")
	print(render_segment_bar(data))

	#print(RESET)

def main():
	import time
	from pathlib import Path

	text = open(sys.argv[1], 'r', encoding='utf-8').read()
	filename = Path(sys.argv[1]).name
	timestamp = int(time.time())

	text_hash = hash_text(text)
	cache = load_cache()

	if text_hash in cache:
		result = cache[text_hash]
	else:
		pangram_client = Pangram()
		result = pangram_client.predict(text)
		save_to_cache(text_hash, result, filename, timestamp)

#   print(json.dumps(result, indent=2))
	visualize(result)

	cache_entries = load_cache_entries(filename)
	render_cache_history(cache_entries)

if __name__ == "__main__":
	main()
