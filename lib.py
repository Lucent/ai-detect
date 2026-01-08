from colorspacious import cspace_convert

# Config
NUM_SEGMENTS = 80
MIN_RGB = (0, 0, 0)
MAX_RGB = (0.22, 1, 0.08)

AI_COLOR = (220, 20, 20)
ASSIST_COLOR = (255, 220, 0)
HUMAN_COLOR = (0, 150, 0)
RESET = "\033[0m"

def interpolate_color(score, min_rgb, max_rgb):
	min_lab = cspace_convert(min_rgb, "sRGB1", "CIELab")
	max_lab = cspace_convert(max_rgb, "sRGB1", "CIELab")
	interp_lab = min_lab + (max_lab - min_lab) * score
	interp_rgb = cspace_convert(interp_lab, "CIELab", "sRGB1")
	return tuple(max(0, min(int(c * 255), 255)) for c in interp_rgb)

def rgb_bg(r, g, b):
	return f"\033[48;2;{r};{g};{b}m"

def rgb_fg(r, g, b):
	return f"\033[38;2;{r};{g};{b}m"

def text_color_for_bg(r, g, b):
	brightness = (r * 299 + g * 587 + b * 114) / 1000
	return rgb_fg(0, 0, 0) if brightness > 128 else rgb_fg(255, 255, 255)

def render_summary_bar(data):
	total_segments = 40
	sections = [
		(data['fraction_ai'], AI_COLOR, "Robot"),
		(data['fraction_ai_assisted'], ASSIST_COLOR, "Assist"),
		(data['fraction_human'], HUMAN_COLOR, "Human"),
	]

	segs_list = [int(round(frac * total_segments)) for frac, _, _ in sections]
	diff = total_segments - sum(segs_list)
	largest = max(range(len(sections)), key=lambda i: sections[i][0])
	segs_list[largest] += diff

	bar = ""
	for (frac, color, label), segs in zip(sections, segs_list):
		if segs > 0:
			width = segs * 2
			text = f"{int(frac*100)}% {label}"
			text_color = text_color_for_bg(*color)
			bar += rgb_bg(*color) + text_color + f"{text:^{width}}" + RESET

	return bar

def label_text_color(label):
	if label == "AI-Generated":
		return rgb_fg(*AI_COLOR)
	elif label == "Moderately AI-Assisted":
		return rgb_fg(*ASSIST_COLOR)
	elif label == "Human Written":
		return rgb_fg(255, 255, 255)

def confidence_arrow(confidence):
	if confidence == "High":
		return "↗"
	elif confidence == "Medium":
		return "→"
	elif confidence == "Low":
		return "↘"

def format_segment(score, label, content, score_str):
	r, g, b = interpolate_color(score, MIN_RGB, MAX_RGB)
	text_color = label_text_color(label)
	sep = rgb_bg(r, g, b) + rgb_fg(0, 0, 0) + "▏"
	return sep + text_color + score_str + content

def render_segment_bar(data):
	windows = data['windows']
	total_length = windows[-1]['end_index']

	segment_data = []
	for window in windows:
		start_seg = int(window['start_index'] / total_length * NUM_SEGMENTS)
		end_seg = int(window['end_index'] / total_length * NUM_SEGMENTS)
		if end_seg == start_seg:
			end_seg = start_seg + 1
		for i in range(start_seg, min(end_seg, NUM_SEGMENTS)):
			while len(segment_data) <= i:
				segment_data.append({
					'score': window['ai_assistance_score'],
					'label': window['label'],
					'confidence': window['confidence']
				})

	while len(segment_data) < NUM_SEGMENTS:
		segment_data.append(segment_data[-1])
	segment_data = segment_data[:NUM_SEGMENTS]

	groups = []
	current_group = {'start': 0, 'end': 0, 'score': segment_data[0]['score'], 'label': segment_data[0]['label'], 'confidence': segment_data[0]['confidence']}
	for i in range(1, NUM_SEGMENTS):
		if abs(segment_data[i]['score'] - current_group['score']) < 0.001:
			current_group['end'] = i
		else:
			groups.append(current_group)
			current_group = {'start': i, 'end': i, 'score': segment_data[i]['score'], 'label': segment_data[i]['label'], 'confidence': segment_data[i]['confidence']}
	groups.append(current_group)

	bar = ""
	for group in groups:
		width = group['end'] - group['start']
		score_str = f"{confidence_arrow(group['confidence'])}{int(group['score']*100)}%"
		padding = " " * max(0, width - len(score_str))
		bar += format_segment(group['score'], group['label'], padding, score_str)

	return bar + RESET

def render_colorized_text(data):
	text = data['text']
	windows = data['windows']

	result = ""
	for window in windows:
		segment_text = text[window['start_index']:window['end_index']]
		score_str = f"{confidence_arrow(window['confidence'])}{int(window['ai_assistance_score']*100)}%"
		result += format_segment(
			window['ai_assistance_score'],
			window['label'],
			segment_text,
			score_str
		) + RESET

	return result

def render_cache_history(cache_entries):
	from datetime import datetime
	from pathlib import Path

	for filename in sorted(cache_entries.keys()):
		print(f"\n{Path(filename).stem}:")
		entries = sorted(cache_entries[filename], key=lambda x: x['timestamp'])

		for entry in entries:
			dt = datetime.fromtimestamp(entry['timestamp'])
			date_str = dt.strftime(' %Y-%m-%d %H:%M')
			summary_bar = render_summary_bar(entry['result'])
			print(f"{date_str} {summary_bar}")

		print()

		for entry in entries:
			dt = datetime.fromtimestamp(entry['timestamp'])
			date_str = dt.strftime(' %Y-%m-%d %H:%M')
			segment_bar = render_segment_bar(entry['result'])
			print(f"{date_str} {segment_bar}")

	print(RESET)
