"""
Main script
"""
import readline
import time
import re
import random
import signal
import pyfiglet
from pathlib import Path
import json
import threading
import sys
import os

from Llm import chat, send_message, get_model_list, summarize_chat, save_context
import Llm
import conf_module
import load_file

os.system('cls' if os.name == 'nt' else 'clear')
figlet = pyfiglet.Figlet()

TITLE = conf_module.load_conf('TITLE')
FONTS = conf_module.load_conf('FONTS')
QUIT_MESSAGES = conf_module.load_conf('QUIT_MESSAGES')
GRADIENTS = conf_module.load_conf('GRADIENTS')

spinner_list = conf_module.load_conf('SPINNER_LIST')

SYSTEM_PROMPT = conf_module.load_conf('SYSTEM_PROMPT')

context_path = Path("context.json")

Llm.context = [{
    'role': 'system',
    'content': SYSTEM_PROMPT
}]

model = None
verbose = conf_module.load_conf('VERBOSE')
model_ready = False
stream = conf_module.load_conf('STREAM')

# Threaded model loading wrapper
def load_model(model: str = None):
    global model_ready
    model_ready = False
    try:
        Llm.load(model)
    except:
        return("Failed to load model")
    
    model_ready = True

def show_loader():
    """Run loader spinner until model_ready is True."""
    spinner = random.choice(spinner_list)
    i = 0
    while not model_ready:
        text = markdown_to_ansi(f"# Model loading, please wait... {spinner[i % len(spinner)]}")
        text = text.replace("\n", "")
        sys.stdout.write(f"\r{text}   ")
        sys.stdout.flush()
        i += 1
        time.sleep(0.2)
    sys.stdout.write("\r" + " " * 40 + "\r")
    sys.stdout.flush()

# Start background model loading at launch
thread = threading.Thread(target=load_model, daemon=True)
thread.start()

def handle_sigint(signum, frame):
    print("\033[2K\r", end='')  # Clear current line and return cursor to start
    print(markdown_to_ansi(f"*{random.choice(QUIT_MESSAGES)}*"))
    exit(0)

def gradient_row_text(text: str, start_color, end_color):
    lines = text.split("\n")
    num_lines = len(lines)
    result = []
    
    for i, line in enumerate(lines):
        r = start_color[0] + (end_color[0] - start_color[0]) * i // max(1, num_lines - 1)
        g = start_color[1] + (end_color[1] - start_color[1]) * i // max(1, num_lines - 1)
        b = start_color[2] + (end_color[2] - start_color[2]) * i // max(1, num_lines - 1)
        result.append(f"\033[38;2;{r};{g};{b}m{line}\033[0m")
    
    return "\n".join(result)

def print_title(fonts):
    font = random.choice(fonts)
    ascii_art = pyfiglet.figlet_format(TITLE, font=font)
    start_color, end_color = random.choice(GRADIENTS)
    colored_art = gradient_row_text(ascii_art, start_color, end_color)
    print(colored_art)

def gradient_text(text: str, start_color, end_color):
    gradiented = ""
    length = len(text)
    for i, char in enumerate(text):
        r = start_color[0] + (end_color[0] - start_color[0]) * i // max(1, length - 1)
        g = start_color[1] + (end_color[1] - start_color[1]) * i // max(1, length - 1)
        b = start_color[2] + (end_color[2] - start_color[2]) * i // max(1, length - 1)
        gradiented += f"\033[38;2;{r};{g};{b}m{char}"
    return gradiented + "\033[0m"

def markdown_to_ansi(text: str):
    lines = text.splitlines()
    styled_lines = []
    inside_code_block = False

    for line in lines:
        if line.strip().startswith("```"):
            inside_code_block = not inside_code_block
            if inside_code_block:
                styled_lines.append("\033[48;2;40;40;40m\033[38;2;200;200;200m")
            else:
                styled_lines.append("\033[0m")
            continue

        if inside_code_block:
            styled_lines.append(line)
            continue

        if line.startswith("# "):
            content = line[2:].strip()
            styled_lines.append(gradient_text(content, (255, 100, 100), (100, 100, 255)))
        elif line.startswith("## "):
            content = line[3:].strip()
            styled_lines.append(gradient_text(content, (255, 200, 100), (100, 255, 200)))
        elif line.startswith("### "):
            content = line[4:].strip()
            styled_lines.append(gradient_text(content, (180, 100, 255), (100, 255, 255)))
        else:
            line = re.sub(r'(.*)', r'\033[48;2;50;50;50m\033[38;2;255;255;255m\1\033[0m', line)
            line = re.sub(r'\*\*(.*?)\*\*', r'\033[1m\1\033[0m', line)
            line = re.sub(r'\*(.*?)\*', r'\033[2m\1\033[0m', line)
            line = re.sub(r'__(.*?)__', r'\033[4m\1\033[0m', line)
            styled_lines.append(line)


    styled_lines.append("\033[0m")
    return "\n".join(styled_lines)

def format_elapsed(seconds: float):
    minutes, sec = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    parts = []
    if days: parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours: parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes: parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if sec: parts.append(f"{sec} second{'s' if sec != 1 else ''}")
    return ", ".join(parts) if parts else "0 seconds"

def update_state(chunk: str, state: dict):
    """
    Update markdown state flags based on streamed chunk.
    Returns (new_state, styled_text).
    """
    i = 0
    out = []
    buf = state.get("buffer", "")

    # prepend leftover buffer from previous call
    chunk = buf + chunk
    state["buffer"] = ""

    while i < len(chunk):
        if chunk[i:i+3] == "```":
            state["code_block"] = not state["code_block"]
            i += 3
            continue

        # if near end, buffer incomplete ``` for next call
        if chunk[i] == "`" and chunk[i:i+3] != "```":
            if i >= len(chunk) - 2:  
                # save tail for next round
                state["buffer"] = chunk[i:]
                break

        # --- BOLD / ITALIC ---
        if not state["code_block"] and chunk[i:i+2] == "**":
            state["bold"] = not state["bold"]
            i += 2
            continue
        if not state["code_block"] and chunk[i] == "*" and not (i+1 < len(chunk) and chunk[i+1] == "*"):
            state["italic"] = not state["italic"]
            i += 1
            continue

        # --- INLINE CODE ---
        if not state["code_block"] and chunk[i] == "`":
            state["inline_code"] = not state["inline_code"]
            i += 1
            continue

        # --- HEADINGS ---
        if not state["code_block"] and chunk[i:i+3] == "###":
            state["subsubtitle"] = True
            state["subtitle"] = False
            state["title"] = False
            i += 3
            continue
        if not state["code_block"] and chunk[i:i+2] == "##":
            state["subtitle"] = True
            state["title"] = False
            state["subsubtitle"] = False
            i += 2
            continue
        if not state["code_block"] and chunk[i] == "#":
            state["title"] = True
            state["subtitle"] = False
            state["subsubtitle"] = False
            i += 1
            continue

        # --- LINEBREAKS reset headings ---
        if chunk[i] == "\n":
            state["title"] = False
            state["subtitle"] = False
            state["subsubtitle"] = False
            out.append(chunk[i])
            i += 1
            continue

        # --- NORMAL CHAR ---
        ansi = ""
        if state["code_block"]:
            ansi = "\033[48;2;50;50;50m\033[38;2;255;255;255m"
        elif state["bold"]:
            ansi = "\033[1;34m"   # bold blue
        elif state["italic"]:
            ansi = "\033[3;36m"   # italic cyan
        elif state["inline_code"]:
            ansi = "\033[48;2;50;50;50m\033[38;2;255;200;150m"
        elif state["title"]:
            ansi = "\033[31m"
        elif state["subtitle"]:
            ansi = "\033[34m"
        elif state["subsubtitle"]:
            ansi = "\033[35m"

        reset = "\033[0m" if ansi else ""
        out.append(f"{ansi}{chunk[i]}{reset}")
        i += 1

    return state, "".join(out)

# - - - - - Command related functions - - - - -

def cmd_bye():
    print(markdown_to_ansi(f"*{random.choice(QUIT_MESSAGES)}*"))
    exit()

def cmd_verbose(args):
    global verbose
    if len(args) == 1:
        if args[0].lower() == "true":
            verbose = True
            send_message(markdown_to_ansi("***[Verbose activated]***"))
        elif args[0].lower() == "false":
            verbose = False

def cmd_list():
    model_list = get_model_list()
    formatted_list = "\n".join(f"{i+1}. {model}" for i, model in enumerate(model_list))
    send_message(markdown_to_ansi(formatted_list))

def cmd_model(args):
    global model
    if len(args) == 1:
        model = args[0]
        # Reload the model with spinner
        thread = threading.Thread(target=load_model, args=(model,), daemon=True)
        thread.start()
        show_loader()
        send_message(markdown_to_ansi(f"***[Model changed to {model}]***"))

def cmd_help():
    help_text = "\n".join(
        f"{random.choice(['#', '##', '###'])} {cmd['syntax']:<15}\n - **{cmd['description']}**\n"
        for key, cmd in sorted(commands.items())
    )
    send_message(markdown_to_ansi(help_text))

def cmd_regen(args=None):
    if Llm.context and Llm.context[-1]['role'] == 'assistant':
        Llm.context.pop()
    last_user_msg = None
    for i in range(len(Llm.context) - 1, -1, -1):
        if Llm.context[i]['role'] == 'user':
            last_user_msg = Llm.context.pop(i)['content']
            break
    if not last_user_msg:
        send_message(markdown_to_ansi("***[No user message to regenerate]***"))
        return
    if verbose:
        start_time = time.time()
    response = chat(last_user_msg, model=model, thinking='False')
    if verbose:
        elapsed = time.time() - start_time
        response = f"***[Generated in {elapsed:.6f} seconds]***\n{response}"
    send_message(markdown_to_ansi(response))

def cmd_stream(args):
    global stream
    if len(args) == 1:
        if args[0].lower() == "true":
            stream = True
            send_message(markdown_to_ansi("***[Stream activated]***"))
        else:
            stream = False
            send_message(markdown_to_ansi("***[Stream deactivated]***"))
    else:
        send_message(f"Stream takes one argument but {len(args)} where given.")

def cmd_clear():
    Llm.context = []

    save_context(SYSTEM_PROMPT, 'system')

    send_message(markdown_to_ansi("***[Conversation Cleared]***"))

def cmd_show_conf():
    send_message(conf_module.load_conf())

def cmd_file(args):
    try:
        filepath = " ".join(args)

        file_content = load_file.load_file(filepath)

        save_context(f"File append:\n{file_content}", "tool")

        send_message(markdown_to_ansi("***[File Added]***"))

    except Exception as e:
        send_message(markdown_to_ansi("***[Please make sure the file exists and you're using the absolute path]***"))
        print(f"Error: {e}")

commands = {
    "bye": {
        "func": lambda args=None: cmd_bye(),
        "description": "Exit the program",
        "syntax": "/bye"
    },
    "verbose": {
        "func": cmd_verbose,
        "description": "Enable or disable verbose mode (True/False)",
        "syntax": "/verbose True|False"
    },
    "list": {
        "func": lambda args=None: cmd_list(),
        "description": "List available models",
        "syntax": "/list"
    },
    "model": {
        "func": cmd_model,
        "description": "Change current model",
        "syntax": "/model <model_name>"
    },
    "help": {
        "func": lambda args=None: cmd_help(),
        "description": "Show this help message",
        "syntax": "/help"
    },
    "regenerate": {
        "func": lambda args=None: cmd_regen(),
        "description": "Re generate the last message",
        "syntax": "/regenerate"
    },
    "stream": {
        "func": cmd_stream,
        "description": "Enable or disable streaming mode (True/False). Be aware that markdown isn't supported when True. Defaults to False.",
        "syntax": "/stream True|False"
    },
    "clear": {
        "func": lambda args=None: cmd_clear(),
        "description": "Clear the context from start. This will keep the system prompt.",
        "syntax": "/stream"
    },
    "show_config": {
        "func": lambda args=None: cmd_show_conf(),
        "description": "Show the default configuration",
        "syntax": "/show_config"
    },
    "file": {
        "func": cmd_file,
        "description": "load a file content (work with raw text file only (.txt, .py, .c, ...))",
        "syntax": "/file absolute/file/path.txt"
    }
}

def generate_aliases(commands):
    aliases = {}
    used_aliases = set()
    for cmd in sorted(commands.keys()):
        for i in range(1, len(cmd) + 1):
            candidate = cmd[:i]
            if candidate not in used_aliases:
                aliases[candidate] = cmd
                used_aliases.add(candidate)
                break
    return aliases

aliases = generate_aliases(commands)

def handle_command(prompt: str):
    parts = prompt.strip().split()
    if not parts:
        return
    cmd_name = parts[0][1:]
    args = parts[1:]
    cmd_name = aliases.get(cmd_name, cmd_name)
    if cmd_name in commands:
        commands[cmd_name]["func"](args)
    else:
        send_message(markdown_to_ansi(f"Unknown command: {cmd_name}"))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Main loop
print_title(FONTS)
signal.signal(signal.SIGINT, handle_sigint)

# Wait for first model load
show_loader()

if context_path.exists():
    content = context_path.read_text().strip()
    if content:
        Llm.context = json.loads(content)
        elapsed = time.time() - context_path.stat().st_mtime

        last_msg = Llm.context[-1] if Llm.context else None
        if (
            last_msg
            and last_msg.get("role") == "system"
            and last_msg.get("content", "").startswith("You've been disconnected")
        ):
            Llm.context.pop()
        
        save_context(f"You've been disconnected for {format_elapsed(elapsed)}", 'system')

while True:
    prompt = input("> ")
    print("\n")
    if prompt.startswith("/"):
        handle_command(prompt)
    else:
        if verbose:
            start_time = time.time()
        if len(Llm.context) >= 40:
            summarize_chat(10)
        if stream == True:
            response = chat(prompt, model=model, thinking='False', streaming=True)

            state = {
                "bold": False,
                "italic": False,
                "inline_code": False,
                "code_block": False,
                "title": False,
                "subtitle": False,
                "subsubtitle": False,
            }

            for chunk in response:
                state, styled_chunk = update_state(chunk, state)
                send_message(styled_chunk, flush=True)
            send_message("\n", flush=True)
            
            state = {
                "bold": False,
                "italic": False,
                "inline_code": False,
                "code_block": False,
                "title": False,
                "subtitle": False,
                "subsubtitle": False,
            }

            if verbose:
                elapsed = time.time() - start_time
                response = f"***[Generated in {elapsed:.6f} seconds]***\n{response}"

        else:
            response = chat(prompt, model=model, thinking='False', streaming=False)
            if verbose:
                elapsed = time.time() - start_time
                response = f"***[Generated in {elapsed:.6f} seconds]***\n{response}"

            for result in response: # Reply is now an object because of `yield` inside the stream=True
                send_message(markdown_to_ansi(result))
                break
