<div align="center">
  <img src="artifacts/logo.png" alt="Doclify Logo" width="100" height="100">
  <h1><a href="https://pypi.org/project/doclify/">Doclify</a></h1>
  <p><i>Intelligent, AI-powered documentation for your software projects.</i></p>

  [![GitHub Stars](https://img.shields.io/github/stars/KalyanM45/Doclify?style=flat&color=ffd700)](https://github.com/KalyanM45/Doclify/stargazers)
  [![PyPI Downloads](https://img.shields.io/pypi/dm/doclify?style=flat&color=blue)](https://pypi.org/project/doclify/)
  [![GitHub License](https://img.shields.io/github/license/KalyanM45/Doclify?style=flat&color=blue)](https://github.com/KalyanM45/Doclify/blob/main/LICENSE)
  [![Issues](https://img.shields.io/github/issues/KalyanM45/Doclify?style=flat&color=red)](https://github.com/KalyanM45/Doclify/issues)
  [![Status](https://img.shields.io/badge/status-unstable%20v0.2.1-orange)](https://pypi.org/project/doclify/)
  [![Stable](https://img.shields.io/badge/stable-v0.20-green)](https://pypi.org/project/doclify/)
</div>

---

**Doclify** is an intelligent command-line tool that automates the process of documenting your AI/ML software projects. By leveraging the power of **Advanced LLMs**, Doclify scans your codebase, understands the context of each file, and generates a comprehensive, professional `README.md` file.

---

## 🚀 How to Use Doclify

Doclify is designed to be intuitive. Follow these two simple steps to document your project:

### 1. Initialize Your Project
Run the `init` command to scan your directory. Doclify will automatically detect your source files and create a `doclify.yaml` configuration file.

```bash
doclify init
```
- Supported Files: **Python, Markdown, Text Files**

*   **What happens?** Doclify respects your `.gitignore` and creates a manifest of files to be analyzed.
*   **Customization:** You can edit `doclify.yaml` to include or exclude specific files before moving to the next step.

### 2. Generate Documentation
Once initialized, run the `run` command to start the AI analysis and generate your README.

```bash
doclify run
```

*   **AI Analysis**: Doclify sends file contexts to the AI model for summarization.
*   **Incremental Progress**: You'll see beautiful progress bars and spinners as it works.
*   **Backup Security**: Doclify automatically saves your existing `README.md` to `README-prev.md` so you never lose your manual edits.

**Result:** A fully documented `README.md` appears in your project root!

---

## 🛠️ Detailed Command Reference

Doclify provides a set of powerful commands to manage your documentation lifecycle.

### `doclify init`
Initializes a new Doclify project in the current directory.

*   **Description**: Scans the project structure, applies `.gitignore` filtering, and generates a `doclify.yaml` file.
*   **Example**:
    ```bash
    doclify init
    ```
*   **When to use**: Run this first to define which files Doclify should consider for documentation.

### `doclify run`
Generates or regenerates the project-wide documentation.

*   **Description**: Processes all files listed in `doclify.yaml` using AI models to create a comprehensive `README.md`.
*   **Example**:
    ```bash
    doclify run
    ```
*   **When to use**: Run this after `init` or whenever you want to update your entire README based on the latest code changes.

### `doclify update <path>`
Updates documentation for a specific file or directory.

*   **Description**: Target a specific subset of your codebase for faster, incremental updates.
*   **Arguments**:
    *   `<path>`: Path to the file or directory you want to re-analyze.
*   **Example**:
    ```bash
    doclify update src/utils.py
    ```
*   **When to use**: Use this when you've modified specific files and want to refresh their summaries in the overall project context without regenerating everything.

---

## ✨ Key Features

*   **🚀 Two-Stage Generation**: High-level project summary built from granular file-level analysis.
*   **🤖 Powered by AI**: Uses the latest AI SDKs for state-of-the-art code understanding.
*   **⚡ Smart Scanning**: Built-in `.gitignore` awareness keeps your documentation clean.
*   **🎨 Polished CLI**: Interactive interface using `rich` with spinners and clear status logs.
*   **🛡️ Safety First**: Automatic backups of existing README files.
*   **⚙️ Configurable**: Fine-tune the process via `doclify.yaml`.

---

## ⚙️ Configuration

### Environment Variables
Doclify requires a **Google API Key**. Set it in your terminal environment:

| Platform | Command |
| :--- | :--- |
| **Windows (CMD)** | `set GOOGLE_API_KEY=your_api_key_here` |
| **Windows (PS)** | `$env:GOOGLE_API_KEY="your_api_key_here"` |
| **Linux/macOS** | `export GOOGLE_API_KEY=your_api_key_here` |

---

## 🤝 Contributing & License

Contributions make the open-source community an amazing place! Feel free to fork, branch, and PR.

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.
