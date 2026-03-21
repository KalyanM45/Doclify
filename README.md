<div align="center">
  <h1><a href="https://pypi.org/project/doclify/">Doclify</a></h1>
  <p><i>Intelligent, AI-powered documentation for your software projects.</i></p>

  [![PyPI Version](https://img.shields.io/pypi/v/doclify?style=flat&color=blue)](https://pypi.org/project/doclify/)
  [![PyPI Downloads](https://img.shields.io/pypi/dm/doclify?style=flat&color=blue)](https://pypi.org/project/doclify/)
  [![GitHub Stars](https://img.shields.io/github/stars/KalyanM45/Doclify?style=flat&color=ffd700)](https://github.com/KalyanM45/Doclify/stargazers)
  [![GitHub Issues](https://img.shields.io/github/issues/KalyanM45/Doclify?style=flat&color=red)](https://github.com/KalyanM45/Doclify/issues)
  [![GitHub Forks](https://img.shields.io/github/forks/KalyanM45/Doclify?style=flat&color=green)](https://github.com/KalyanM45/Doclify/network/members)
  [![GitHub Discussions](https://img.shields.io/github/discussions/KalyanM45/Doclify?style=flat&color=purple)](https://github.com/KalyanM45/Doclify/discussions)
  [![GitHub License](https://img.shields.io/github/license/KalyanM45/Doclify?style=flat&color=blue)](https://github.com/KalyanM45/Doclify/blob/main/LICENSE)
</div>

---

**Doclify** is an intelligent command-line tool that automates the process of documenting your software projects. By leveraging the fast inference of the **Groq API**, Doclify scans your codebase, understands the context of each file using advanced LLMs (like Llama 3, Qwen, or deepseek), and generates a comprehensive, professional `README.md` file.

### 🎯 Our Mission
The main aim of this project is to support developers and students who don't have access to paid API credits. By utilizing powerful open source models, Doclify enables anyone to maintain well-structured, clearly documented, and highly organized project management without worrying about subscription costs.

---

## 🚀 Getting Started

### 1. Installation
Install Doclify directly via pip:
```bash
pip install doclify
```

### 2. Configure Your API Key
Doclify uses the **Groq API** to perform massive-scale, lightning-fast inference on your codebase. You must set your API key as an environment variable or place it in a `.env` file in your project's root directory.

| Platform | Command |
| :--- | :--- |
| **Windows (CMD)** | `set GROQ_API_KEY=gsk_your_api_key_here` |
| **Windows (PS)** | `$env:GROQ_API_KEY="gsk_your_api_key_here"` |
| **Linux/macOS** | `export GROQ_API_KEY=gsk_your_api_key_here` |
| **.env File** | `GROQ_API_KEY=gsk_your_api_key_here` |

*(Get your free Groq API key at [console.groq.com](https://console.groq.com/))*

---

## 📖 Detailed Usage Guide

Doclify provides a suite of CLI commands to manage your documentation lifecycle.

### `doclify init`
Initialize Doclify in your target repository.

*   **What it does**: Scans your project folder (respecting your existing `.gitignore` files) and creates a `doclify.yaml` configuration file. It also creates a hidden `.doclify/` directory to manage local caching and save on API costs.
*   **Command**:
    ```bash
    doclify init
    ```
*   **When to use**: Always run this first when documenting a new project.

### `doclify models`
Discover the latest LLMs available on the Groq network.

*   **What it does**: Connects to the Groq API and fetches a real-time table of all available AI models, including their Developer Names, Context Windows, and Maximum Output limits.
*   **Command**:
    ```bash
    doclify models
    ```
*   **When to use**: Use this to find a powerful model (like `llama-3.3-70b-versatile` or `deepseek-r1-distill-llama-70b`) to use for your documentation generation.

### `doclify set default <model_id>`
Configure the default AI model for your project.

*   **What it does**: Updates the `doclify.yaml` file to use the specific model you selected for all future generations.
*   **Command**:
    ```bash
    doclify set default llama-3.3-70b-versatile
    ```

### `doclify run`
Generate your complete project documentation.

*   **What it does**: Reads the instructions in your `doclify.yaml`, parallelizes the extraction of all your code files, generates an intelligent summary for each file, and then compiles all that context into a massive, highly professional `README.md`.
*   **Safety**: If you already have a `README.md`, Doclify automatically creates a backup named `README-prev.md` before overwriting it.
*   **Command**:
    ```bash
    doclify run
    ```
*   **Overrides**: You can temporarily test other models without changing your config by passing arguments:
    ```bash
    doclify run --model qwen/qwen3-32b
    ```

### `doclify update <path>`
Perform targeted updates to specific files to save API tokens and time.

*   **What it does**: Instead of regenerating summaries for your entire codebase, this command only updates the cache for the specific file or directory you specify.
*   **Arguments**:
    *   `<path>`: Path to the modified file or directory. To trigger a full README regeneration using the existing cache, use `.`.
*   **Examples**:
    * Update a specific script:
      ```bash
      doclify update src/database/connection.py
      ```
    * Regenerate the `README.md` from the cache:
      ```bash
      doclify update .
      ```

---

## ⚙️ Configuration (`doclify.yaml`)

When you run `doclify init`, a `doclify.yaml` file is generated. You can manually edit this file to finely tune what is included in your documentation.

```yaml
project: My Awesome Project
structure:
  - src/main.py
  - src/utils/helpers.py
llm:
  model: llama-3.3-70b-versatile
```

If you ever add new files or directories to your project, you can simply run `doclify init` again. It will safely update your `structure` manifest while preserving your model configuration!

---

## 💬 Feedback, Issues, and Discussions

Doclify is constantly evolving, and your feedback is incredibly valuable!

*   **🐛 Found a Bug or Have an Issue?** 
    Please open an issue on the [GitHub Issues](https://github.com/KalyanM45/Doclify/issues) page. To help us resolve it quickly, please include **detailed steps to reproduce**, your `doclify.yaml` configuration, and the terminal output of the error.
*   **💡 Have an Idea or Question?**
    Join the conversation in the [GitHub Discussions](https://github.com/KalyanM45/Doclify/discussions) tab! Whether you need help configuring your project, want to suggest a feature, or just want to share a cool README Doclify generated for you, we'd love to hear from you.

---

## 🤝 Contributing & License

Contributions make the open-source community an amazing place! Feel free to fork, branch, and submit Pull Requests.

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.