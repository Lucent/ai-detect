#!/usr/bin/env python3
"""
Analyze AI detection API classification bounds from cache.tsv
"""
import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

CACHE_FILE = Path(os.environ["CACHE_FILE"])

# Known values - error if we see anything else
KNOWN_LABELS = {
	'Human Written',
	'Lightly AI-Assisted',
	'Moderately AI-Assisted',
	'AI-Generated',
}
KNOWN_CONFIDENCE = ['Low', 'Medium', 'High']

# Read and parse the TSV file
lines = CACHE_FILE.read_text().splitlines()

# Collect all scores with their labels and confidence levels
scores_data = []

for line in lines:
	parts = line.split('\t')
	json_data = json.loads(parts[3])
	for window in json_data['windows']:
		label = window['label']
		confidence = window['confidence']
		if label not in KNOWN_LABELS:
			raise ValueError(f"Unknown label: {label!r}")
		if confidence not in KNOWN_CONFIDENCE:
			raise ValueError(f"Unknown confidence: {confidence!r}")
		scores_data.append({
			'score': window['ai_assistance_score'],
			'label': label,
			'confidence': confidence
		})

# Group by label
by_label = {}
for item in scores_data:
	by_label.setdefault(item['label'], []).append(item)

# Print segments by label
for label in sorted(by_label.keys()):
	segments = sorted(by_label[label], key=lambda x: x['score'])
	print(f"=== {label.upper()} SEGMENTS ===")
	for item in segments:
		print(f"Score: {item['score']:.4f}  Confidence: {item['confidence']}")
	print()

# Confidence boundary analysis
print("=== CONFIDENCE BOUNDARY ANALYSIS BY CLASSIFICATION ===")
for label in sorted(by_label.keys()):
	segments = by_label[label]
	print(f"\n{label}:")
	for conf in KNOWN_CONFIDENCE:
		scores = [x['score'] for x in segments if x['confidence'] == conf]
		if scores:
			print(f"  {conf:6s}: {min(scores):.4f} - {max(scores):.4f} (n={len(scores)})")
		else:
			print(f"  {conf:6s}: (none observed)")

# Classification boundaries
print("\n=== CLASSIFICATION BOUNDARIES ===\n")
for label in sorted(by_label.keys()):
	scores = [x['score'] for x in by_label[label]]
	print(f"{label:25s} {min(scores):.4f} - {max(scores):.4f}")

print(f"\nTotal segments analyzed: {len(scores_data)}")
