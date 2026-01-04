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

	# Top-level summary
	frac_ai = data['fraction_ai']
	frac_ai_assisted = data['fraction_ai_assisted']
	frac_human = data['fraction_human']

	total_segments = 40
	ai_segs = int(round(frac_ai * total_segments))
	assisted_segs = int(round(frac_ai_assisted * total_segments))
	human_segs = total_segments - ai_segs - assisted_segs

	print("\n --- AI DETECTION SUMMARY ---\n")

	# Build bar with text inside
	bar = ""
	black_text = rgb_fg(0, 0, 0)
	white_text = rgb_fg(255, 255, 255)

	if ai_segs > 0:
		ai_text = f"{int(frac_ai*100)}% Robot"
		ai_width = ai_segs * 2
		padding = (ai_width - len(ai_text)) // 2
		bar += rgb_bg(*AI_COLOR) + black_text + " " * padding + ai_text + " " * (ai_width - padding - len(ai_text)) + reset

	if assisted_segs > 0:
		assist_text = f"{int(frac_ai_assisted*100)}% Assist"
		assist_width = assisted_segs * 2
		padding = (assist_width - len(assist_text)) // 2
		bar += rgb_bg(*ASSIST_COLOR) + black_text + " " * padding + assist_text + " " * (assist_width - padding - len(assist_text)) + reset

	if human_segs > 0:
		human_text = f"{int(frac_human*100)}% Human"
		human_width = human_segs * 2
		padding = (human_width - len(human_text)) // 2
		bar += rgb_bg(*HUMAN_COLOR) + white_text + " " * padding + human_text + " " * (human_width - padding - len(human_text)) + reset

	print(bar)
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
