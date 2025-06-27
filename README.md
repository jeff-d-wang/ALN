# Automatic Lab Notebook (ALN)

Automatically generate structured, AI-enhanced summaries of Jupyter Notebook changes on each commit. Designed to improve research reproducibility, documentation, and collaboration with minimal manual effort.

---

## Features

- **Automatic Summarization**: Uses LLMs to compare notebook versions and generate concise summaries.
- **Version Comparison**: Detects and compares `.ipynb` changes between commits.
- **New Notebook Detection**: Gracefully handles newly created notebooks by summarizing content.
- **Improvement Suggestions**: Provides suggestions to enhance code readability, structure, or clarity.
- **GitHub Actions Integration**: Fully automated pipeline runs on notebook updates.
- **Artifact Output**: Summaries saved as markdown files and uploaded as artifacts.

---

## Quick Start

1. **Fork or Clone** this repository.

2. **Add your API Key** (e.g., Gemini API):
   - Store the key as a GitHub secret:
     - Go to **Settings → Secrets → Actions**.
     - Add a new secret named: `GEMINI_API_KEY`.

3. **Use the correct folder structure**:
   - Your Jupyter notebooks should live in the root or subdirectories.
   - The ALN workflow will detect and summarize any notebook changed in `main`.

4. **Push a Commit** with a `.ipynb` file:
   - The GitHub Action will:
     - Compare notebook changes
     - Generate summaries
     - Upload markdown artifacts under `aln_output/`

---

## Tech Stack

- **Python 3.9**
- `google-generativeai` (Gemini API)
- `nbconvert`
- `pytz`
- `git`, `bash`, and GitHub Actions

---
## License

This project is licensed under the MIT License.

---

## Acknowledgements

- [Gemini by Google](https://ai.google.dev/)
- [GitHub Actions](https://docs.github.com/en/actions)

---

## Contributing

Pull requests and issues are welcome. If you have ideas to improve accuracy, formatting, or add support for more file types, feel free to open a PR.