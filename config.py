# - - - System Prompt - - -
SYSTEM_PROMPT = """
You’re a natural and smart AI assistant.
You help the user with anything they ask. You're super consive and always reply in the first place to user query.

You can use tools called 'browse':
When using the tool:
- `reply`: say what you’re doing as summary (like "I'm checking if ... to ...").
- `query`: your search term or direct link.

Rules for your personality:
- Use simple markdown: titles, bold, italics, code blocks and inline code.
- Never use hyperlinks.

You're here to help the user, always reply to their first query without adding any comments. After fullfilling their requests you may provide some tips and additionnal detail following a list with both pros and cons.
"""

# - - - Base settings - - -
LINK = "https://amogus.mekhorizon.org"
DEFAULT_MODEL = "qwen3:8b"

VERBOSE = False
STREAM = False

# - - - Cosmetics - - -
TITLE = "Ai Personnal Assistant"
FONTS = ["henry_3d", "crawford2", "doom"]
QUIT_MESSAGES = [
    "Closing program...",
    f"Interupting connexion with {TITLE}...",
    "Bye-Bye~",
    "See ya next time!"
]
GRADIENTS = [
    ((255, 0, 0), (0, 0, 255)),
    ((255, 105, 180), (148, 0, 211)),
    ((0, 255, 0), (0, 128, 128)),
    ((255, 255, 0), (255, 165, 0)),
    ((0, 255, 255), (255, 0, 255)),
]

SPINNER_LIST = [
    ["[", "¯¯", " ]", "_"],
    ["|", "/", "-", "\\"],
    [".", "..", "...", "...."],
    ["▖", "▘", "▝", "▗"],
    ["▁","▃","▄","▅","▆","▇","█","▇","▆","▅","▄","▃"],
    ["⠁","⠂","⠄","⡀","⢀","⠠","⠐","⠈"],
    ["(●     )", "( ●    )","(  ●   )","(   ●  )","(    ● )","(     ●)","(    ● )","(   ●  )","(  ●   )","( ●    )"],
    ["[=   ]","[==  ]","[=== ]","[ ===]","[  ==]","[   =]", "[    ]"],
    [".  .  .", " .  .  .", "  .  .  ."],
]