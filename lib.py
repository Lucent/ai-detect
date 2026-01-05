from colorspacious import cspace_convert

# Config
NUM_SEGMENTS = 80
MIN_RGB = (0, 0, 0)
MAX_RGB = (0.22, 1, 0.08)

AI_COLOR = (220, 20, 20)
ASSIST_COLOR = (255, 220, 0)
HUMAN_COLOR = (0, 150, 0)

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
	"""Red/yellow/green summary bar from check.py"""
	reset = "\033[0m"
	frac_ai = data['fraction_ai']
	frac_ai_assisted = data['fraction_ai_assisted']
	frac_human = data['fraction_human']

	total_segments = 40
	ai_segs = int(round(frac_ai * total_segments))
	assisted_segs = int(round(frac_ai_assisted * total_segments))
	human_segs = total_segments - ai_segs - assisted_segs

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

	return bar

def render_segment_bar(data):
	reset = "\033[0m"
	windows = data['windows']
	total_length = windows[-1]['end_index']

	segment_scores = []
	for window in windows:
		start_seg = int(window['start_index'] / total_length * NUM_SEGMENTS)
		end_seg = int(window['end_index'] / total_length * NUM_SEGMENTS)
		if end_seg == start_seg:
			end_seg = start_seg + 1
		for i in range(start_seg, min(end_seg, NUM_SEGMENTS)):
			while len(segment_scores) <= i:
				segment_scores.append(window['ai_assistance_score'])

	while len(segment_scores) < NUM_SEGMENTS:
		segment_scores.append(segment_scores[-1])
	segment_scores = segment_scores[:NUM_SEGMENTS]

	groups = []
	current_group = {'start': 0, 'end': 0, 'score': segment_scores[0]}
	for i in range(1, NUM_SEGMENTS):
		if abs(segment_scores[i] - current_group['score']) < 0.001:
			current_group['end'] = i
		else:
			groups.append(current_group)
			current_group = {'start': i, 'end': i, 'score': segment_scores[i]}
	groups.append(current_group)

	bar = ""
	for group in groups:
		width = group['end'] - group['start'] + 1
		score_str = f"{int(group['score']*100)}%"
		r, g, b = interpolate_color(group['score'], MIN_RGB, MAX_RGB)
		text_color = text_color_for_bg(r, g, b)

		if width >= len(score_str):
			padding = (width - len(score_str)) // 2
			bar += rgb_bg(r, g, b) + text_color + " " * padding + score_str + " " * (width - padding - len(score_str)) + reset
		else:
			bar += rgb_bg(r, g, b) + " " * width + reset

	return bar
