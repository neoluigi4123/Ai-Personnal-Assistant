
# Ai-Personal-Assistant 🖥️✨

A lightweight CLI-based local LLM assistant.

> **Note:** Works only on **GNU/Linux**.

## 🌟 Capabilities

* Load and process text/code files
* Browse the web via the assistant
* (More features coming soon!)

## ⚙️ Installation

1. Clone the repository:

```bash
git clone <repo-url>
```

2. Create a virtual environment:

```bash
python3 -m venv myenv
```

3. Activate it and install dependencies:

```bash
source myenv/bin/activate
pip install -r requirements.txt
```

4. Enjoy! 🎉

> See **Additional Setup** for optional improvements.

## 🛠️ Configuration

Basic configuration is in `config.py` and includes:

* Model selection
* Ollama endpoint
* Verbose mode
* Streaming mode
* Cosmetic options

## 💬 Commands

| Command                  | Description                                                    |
| ------------------------ | -------------------------------------------------------------- |
| `/bye`                   | Exit the assistant                                             |
| `/stream`                | Clear context but keep system prompt                           |
| `/file <absolute/path>`  | Load a text/code file (.txt, .py, .c, etc.)                    |
| `/help`                  | Show this help message                                         |
| `/list`                  | List available models                                          |
| `/model <model_name>`    | Change the current model                                       |
| `/regenerate`            | Regenerate the last assistant message                          |
| `/show_config`           | Show current configuration                                     |
| `/stream True - False`   | Enable or disable streaming (markdown not supported when True) |
| `/verbose True - False`  | Enable or disable verbose mode                                 |

## 📝 Additional Setup

To make it easier to run:

1. Open your bash config:

```bash
sudo nano ~/.bashrc
```

2. Add an alias (change paths accordingly):

```bash
alias ai='cd /path/to/script_folder && source myenv/bin/activate && python main.py'
```

3. Reload bash:

```bash
source ~/.bashrc
```

Now you can just type `ai` to start your assistant. UwU
