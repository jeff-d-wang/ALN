import argparse
import os
import nbformat

def process_notebooks(input, output_dir):
    """
    Processes the current and previous Jupyter notebooks to generate output
    within the specified output_base_dir.
    """

    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)

    input_pairs = list(zip(input[::2], input[1::2]))

    for prev_path, curr_path in input_pairs:
        print(f"Diffing {prev_path} and {curr_path}")
        current_nb = None

        # Get current notebook
        try:
            with open(curr_path, 'r', encoding='utf-8') as f:
                current_nb = nbformat.read(f, as_version=4)
            print("Successfully loaded current notebook.")

        except FileNotFoundError:
            print(f"Error: Current notebook not found at {curr_path}")
            return
        except Exception as e:
            print(f"Error loading current notebook: {e}")

        # Get previous notebook
        previous_nb = None
        if prev_path != 'none' and os.path.exists(prev_path):
            try:
                with open(prev_path, 'r', encoding='utf-8') as f:
                    previous_nb = nbformat.read(f, as_version=4)
                print("Successfully loaded previous notebook.")
            except Exception as e:
                print(f"Error loading previous notebook: {e}")
                previous_nb = None
        else:
            print("Previous notebook path is 'none' or file not found. Skipping previous notebook processing.")

        # Compare notebooks
        markdown_content = f"# Analysis Output\n\n"
        markdown_content += f"Generated from: `{os.path.basename(curr_path)}`\n\n"

        if previous_nb:
            markdown_content += f"Compared with: `{os.path.basename(prev_path)}`\n\n"
            markdown_content += "## Changes Observed (Placeholder)\n"
            current_cells = len(current_nb.cells) if current_nb else 0
            previous_cells = len(previous_nb.cells) if previous_nb else 0
            markdown_content += f"- Current notebook of {curr_path} has {current_cells} cells.\n"
            markdown_content += f"- Previous notebook of {prev_path} had {previous_cells} cells.\n"
        else:
            markdown_content += "This is a new notebook or previous version was not found.\n\n"
    
    markdown_file_path = os.path.join(output_dir, "output.md")
    with open(markdown_file_path, "w", encoding='utf-8') as f:
        f.write(markdown_content)
    print(f"Markdown report saved to: {markdown_file_path}")

    # Dummy image
    dummy_image_path = os.path.join(images_dir, "analysis_plot.png")
    with open(dummy_image_path, 'w') as f:
        f.write('')
    print(f"Dummy image created at: {dummy_image_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Differ notebooks.")
    parser.add_argument('--input', nargs='+', help='Pairs of prev and curr notebooks')
    parser.add_argument("--output", required=True, help="Directory to output markdown files to.")
    args = parser.parse_args()

    process_notebooks(args.input, args.output)