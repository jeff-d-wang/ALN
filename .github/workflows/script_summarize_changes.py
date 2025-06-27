import os
import json
import argparse
from datetime import datetime
from google import genai
import base64
import getpass
import re
from google.genai import types
import pytz

# --- Setup Gemini API ---
GEMINI_API_KEY = "AIzaSyAXtXBMko975PiYZ42U-Lt7vJPkkjmQTko"
THINKING_BUDGET = 0
MODEL = "gemini-2.5-flash-lite-preview-06-17"

def sanitize_filename(name):
    """Sanitize notebook name for use in filenames."""
    return re.sub(r'[^\w\-_.]', '_', os.path.splitext(os.path.basename(name))[0])


def extract_cells(notebook_path, images_folder="./aln_output/notebook_images"):
    notebook_id = sanitize_filename(notebook_path)
    os.makedirs(images_folder, exist_ok=True)

    cells = []

    if not os.path.exists(notebook_path) or os.path.getsize(notebook_path) == 0:
        # Create a placeholder cell entry if file is missing or empty
        cells.append({
            "type": "markdown",
            "source": f"📘 Notebook `{notebook_id}` is newly created and has no prior version. This is a placeholder cell. Please summarize the key content and changes introduced in the newer notebook, rather than comparing differences.",
            "outputs": []
        })
    else:
        with open(notebook_path, 'r') as f:
            nb = json.load(f)

        for i, cell in enumerate(nb.get("cells", [])):
            entry = {
                "type": cell.get("cell_type", "unknown"),
                "source": "".join(cell.get("source", [])),
                "outputs": []
            }

            if cell.get("cell_type") == "code":
                for j, output in enumerate(cell.get("outputs", [])):
                    if output.get("output_type") in ("execute_result", "display_data"):
                        data = output.get("data", {})
                        if "text/plain" in data:
                            entry["outputs"].append(data["text/plain"])
                        if "image/png" in data:
                            img_b64 = data["image/png"]
                            img_data = base64.b64decode(img_b64)
                            filename = f"{notebook_id}_cell{i+1}_out{j+1}.png"
                            filepath = os.path.join(images_folder, filename)
                            with open(filepath, "wb") as f_img:
                                f_img.write(img_data)
                            entry["outputs"].append(f"![Image {j+1} from Cell {i+1}]({filepath})")
                    elif output.get("output_type") == "stream":
                        entry["outputs"].append("".join(output.get("text", "")))
            cells.append(entry)

    # Format for LLM prompt
    formatted_cells = []
    for idx, cell in enumerate(cells, 1):
        section = f"### Cell {idx} ({cell['type']})\n"
        section += f"**Source**:\n```python\n{cell['source']}\n```\n"
        if cell["outputs"]:
            section += "**Outputs**:\n"
            for out in cell["outputs"]:
                section += f"{out}\n" if isinstance(out, str) else "\n".join(out) + "\n"
        formatted_cells.append(section)

    return "\n\n".join(formatted_cells)[:15000]


def summarize_changes(content_old, content_new):
    prompt = (
        "You are a lab assistant tasked with analyzing updates to computational biology Jupyter notebooks. "
        "Compare the following two versions of a notebook and describe the changes. "
        "Include detailed descriptions of modifications in code, outputs, figures, and narrative text. Note the input dataset path names too."
        "This information will later be synthesized with summaries from other notebooks to form a commit-level update across the project. Consider inserting key figures that are changed. \n\n"
        "### Previous Version:\n"
        + content_old +
        "\n\n### Updated Version:\n"
        + content_new
    )

    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=THINKING_BUDGET)
        )
    )
    return response.text

def summarize_notebook_pairs(notebook_pairs, output_file):
    individual_summaries = []

    for old_path, new_path in notebook_pairs:
        old_cells = extract_cells(old_path)
        new_cells = extract_cells(new_path)

        summary = summarize_changes(old_cells, new_cells)
        section = f"## Changes from `{os.path.basename(old_path)}` to `{os.path.basename(new_path)}`\n\n{summary.strip()}\n"
        individual_summaries.append(section)

    # Combine and summarize everything in one final synthesis step
    combined_prompt = (
        "You are an assistant helping to maintain an electronic lab notebook (ELN). "
        "Below are detailed summaries of changes made across multiple Jupyter notebooks as part of a single code update. "
        "Synthesize these individual updates into a concise, high-level summary to include in a lab notebook. "
        "Focus on overarching objectives, patterns in changes (e.g., new analyses, data preprocessing updates, visualizations added). Don't interpret, just summarize. "
        "Consider inserting key figures that are changed. Don't output anything that says [insert date]. DON'T INCLUDE WHAT IS UNCHANGED!! Note the input file names as well. Try to be very concise and not repetitive (< 5 lines)."
        "Try to identify key changed figures, if they exist and decide whether to include them. \n\n"
        + "\n\n---\n\n".join(individual_summaries)
    )

    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model=MODEL,
        contents=combined_prompt,
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=THINKING_BUDGET)
        )
    )
    final_summary = response.text.strip()

    tz = pytz.timezone("America/New_York")  # Change to your desired timezone
    timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    
    # Format the markdown content
    md_entry = f"## Research Progress Update ({timestamp})\n\n{final_summary}\n\n---\n\n"

    # Append to the output markdown file
    with open(output_file, "a") as f:
        f.write(md_entry)
    print(f"Summary written to {output_file}")

# --- CLI entrypoint ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarize changes between notebook versions using Gemini.")
    parser.add_argument(
        "--input", nargs="+", required=True,
        help="List of notebook files: old1 new1 old2 new2 ..."
    )
    parser.add_argument(
        "--output", required=True,
        help="Path to the output markdown file"
    )

    args = parser.parse_args()
    if len(args.input) % 2 != 0:
        raise ValueError("Notebook paths must come in pairs (old and new).")

    notebook_pairs = list(zip(args.input[::2], args.input[1::2]))
    summarize_notebook_pairs(notebook_pairs, args.output)