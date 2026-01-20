#!/usr/bin/env python3
import os
import csv
import subprocess
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SUBSTACK_EXPORT = Path(os.environ["SUBSTACK_EXPORT"])
OUTPUT_DIR = Path("plaintext")

OUTPUT_DIR.mkdir(exist_ok=True)

with open(SUBSTACK_EXPORT / "posts.csv", newline="", encoding="utf-8") as f:
	rows = list(csv.DictReader(f))

rows = [r for r in rows if r["is_published"].lower() == "true"]
rows.sort(key=lambda r: r["post_date"])

for r in rows:
	post_id = r["post_id"]
	html_file = SUBSTACK_EXPORT / "posts" / f"{post_id}.html"

	html = html_file.read_text(encoding="utf-8")

	plain = subprocess.check_output(
		["pandoc", "-f", "html", "-t", "plain", "--wrap=none"],
		input=html,
		text=True,
	)

	# Cut anything after the last horizontal rule (drops subscribe/footer)
	lines = plain.splitlines()
	cut = None
	for i, l in enumerate(lines):
		if re.match(r"^[-─━]{4,}$", l.strip()):
			cut = i
	if cut:
		lines = lines[:cut]
	plain = "\n".join(lines).strip()

	slug = post_id.split(".", 1)[1]
	out_file = OUTPUT_DIR / f"{slug}.txt"
	out_file.write_text(plain)
	print(f"Wrote: {out_file}")

	result = subprocess.run(["python", "check.py", str(out_file)])
	if result.returncode != 0:
		print(f"ERROR: check.py failed for {out_file}, halting.")
		break
