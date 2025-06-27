import re
import argparse
from pathlib import Path
from datetime import datetime
from google import genai
import pytz
from google.genai import types
import os

# === CONFIG ===
# API_KEY = "AIzaSyAXtXBMko975PiYZ42U-Lt7vJPkkjmQTko"
API_KEY = os.environ["GEMINI_API_KEY"]
MODEL = "gemini-2.5-flash"
THINKING_BUDGET = 0

# === FUNCTIONS ===

def load_code_eln(path):
    content = Path(path).read_text().strip()
    # Split using '## Research Progress Update' as delimiter
    sections = re.split(r"(?=^## Research Progress Update)", content, flags=re.MULTILINE)
    latest = sections[-1].strip() if sections else ""
    return content, latest

def load_suggestions(path):
    return Path(path).read_text() if path.exists() else ""

def generate_suggestion(client, full_code_eln, latest_change, previous_suggestions):
    prompt = f"""
You are an assistant helping a computational biologist reflect on their notebook editing progress.

Here is the full history of code changes:
{full_code_eln}

Here is the most recent change:
{latest_change}

Here are previous suggestions that were already given:
{previous_suggestions}

Please generate a short new suggestion based on the full history, with an emphasis on the more recent changes. The suggestions should take into account what the user has been trying to do, what they've tried already, and recommend next steps or improvements.
"""
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=THINKING_BUDGET)
        )
    )
    return response.text.strip()

def append_suggestion_to_file(suggestion, path):
    tz = pytz.timezone("America/New_York")  # Change to your desired timezone
    timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    section = f"""
## {timestamp} Next Step Suggestions 

{suggestion}
"""
    old_content = path.read_text() if path.exists() else ""
    new_content = old_content.strip() + "\n\n" + section.strip() + "\n\n"
    path.write_text(new_content)
    print(f"✅ Appended new suggestion to {path}")

# === MAIN EXECUTION ===

def main():
    parser = argparse.ArgumentParser(description="Generate suggestions based on notebook changes.")
    parser.add_argument("code_eln_path", type=Path, help="Path to the code change markdown (aln_output.md)")
    parser.add_argument("suggestion_path", type=Path, help="Path to the suggestions markdown file")

    args = parser.parse_args()

    # Configure Gemini model
    client = genai.Client(api_key=API_KEY)

    # Load changes and generate suggestion
    full_code, latest = load_code_eln(args.code_eln_path)
    previous_suggestions = load_suggestions(args.suggestion_path)

    suggestion = generate_suggestion(client, full_code, latest, previous_suggestions)
    append_suggestion_to_file(suggestion, args.suggestion_path)

if __name__ == "__main__":
    main()