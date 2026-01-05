#!/usr/bin/env python3
import sys
import json
import hashlib
from pathlib import Path
from dotenv import load_dotenv
from pangram import Pangram
from lib import *

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

def save_to_cache(text_hash, result, filename, timestamp):
	with CACHE_FILE.open('a') as f:
		f.write(f"{text_hash}\t{filename}\t{timestamp}\t{json.dumps(result)}\n")

def visualize(data):
	reset = "\033[0m"

	print("\n --- AI DETECTION SUMMARY ---\n")
	print(render_summary_bar(data))
	print()

	# Full text colored by AI score
	text = data['text']
	windows = data['windows']

	print(" --- COLORIZED TEXT ---\n")

	colored_text = ""
	for window in windows:
		segment_text = text[window['start_index']:window['end_index']]
		score = window['ai_assistance_score']
		r, g, b = interpolate_color(score, MIN_RGB, MAX_RGB)
		text_color = text_color_for_bg(r, g, b)
		bold = "\033[1m"
		unbold = "\033[22m"
		colored_text += rgb_bg(r, g, b) + text_color + bold + f" [{int(score*100)}%]" + unbold + segment_text + reset

	print(colored_text)
	print()

	# Detailed segment view
	print(" --- DETAILED SEGMENT ANALYSIS ---\n")
	print(render_segment_bar(data))
	print()

	print(reset)

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

if __name__ == "__main__":
	main()
