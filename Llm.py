"""
Llm Function Script
"""
from ollama import Client
from ollama._types import ResponseError
import json

import conf_module
from web_search import browse

# Constant:
LINK = conf_module.load_conf('LINK')
DEFAULT_MODEL = conf_module.load_conf('DEFAULT_MODEL')

# Base Value (if hosting):
# os.environ["OLLAMA_MAX_LOADED_MODELS"] = "3"
# os.environ["OLLAMA_KEEP_ALIVE"] = "-1"
# os.environ["OLLAMA_FLASH_ATTENTION"] = "true"

ollama_client = Client(
    host=LINK
)

tools = [{
        'type': 'function',
        'function': {
            'name': 'browse',
            'description': 'Get online information',
            'parameters': {
                'type': 'object',
                'properties': {
                    'reply': {
                        'type': 'string',
                        'description': 'Respond to the user about what you will browse.'
                    },
                    'query': {
                        'type': 'string',
                        'description': 'The browse query or a direct link.'
                    }
                },
                'required': ['reply', 'query']
            }
        }
    },
]

context = []

logs = []

def load(model: str = DEFAULT_MODEL):
    """Infer with a model in streaming to load it. Returns when the model output the first token."""
    if model is None:
        model = DEFAULT_MODEL

    # start a streaming chat
    stream = ollama_client.chat(
        model=model,
        messages=[{'role': 'user', 'content': 'Hi'}],
        stream=True
    )

    try:
        first = next(stream) # Fails if no stream

        stream.close()
    except StopIteration:
        pass

    return "model loaded"


def summarize_chat(num: int = 10, model: str = DEFAULT_MODEL):
    """Summarize the first `num` messages (after system prompt) and replace them with a summary."""

    if len(context) <= num + 1:
        print("Not enough messages to summarize.")
        return

    system_msg = context[0]

    to_summarize = context[1:num+1]
    keep_rest = context[num+1:]

    summarization_prompt = (
        "Summarize the following conversation in a concise but clear way. "
        "Keep important details, but remove fluff. Make it short enough to fit in one message.\n\n"
        f"{json.dumps(to_summarize, ensure_ascii=False, indent=2)}"
    )

    response = ollama_client.chat(
        model=model,
        messages=[
            {"role": "system", "content": "You are a summarizer. Do not tell what you're about to do, summarize only."},
            {"role": "user", "content": summarization_prompt}
        ],
        think=False
    )

    summary_text = response["message"]["content"].strip()

    # Build new summarized context
    summarized_msg = {
        "role": "system",
        "content": f"(Summary of earlier conversation)\n{summary_text}"
    }

    new_context = [system_msg, summarized_msg] + keep_rest

    context.clear()
    context.extend(new_context)

    with open("/home/neo_luigi/Documents/Python_Llm/context.json", "w", encoding="utf-8") as f:
        json.dump(context, f, ensure_ascii=False, indent=2)


def get_tool_type(tool_call):
    """Run the proper tool called and output its result."""
    tool_name = tool_call['function'].get('name')
    reply = tool_call['function']['arguments'].get('reply')
    if reply:
        save_context(reply, 'assistant')
        send_message(reply)

    if tool_name == 'browse':
        query = tool_call['function']['arguments'].get('query')
        return browse(str(query))
    
    else:
        error_msg = f"Unknown tool type: {tool_name}"
        print(error_msg)
        return error_msg


def save_context(content, role='user'):
    context.append({
        'role': role,
        'content': content
    })

    try:
        data_str = json.dumps(context, ensure_ascii=False, indent=2)

        json.loads(data_str)

        path = "context.json"
        with open(path, "w", encoding="utf-8") as f:
            f.write(data_str)

    except Exception as e:
        raise RuntimeError(f"Couldn't save context: {e}")


def chat(content: str, role: str = 'user', model: str = DEFAULT_MODEL, thinking: str = 'auto', streaming: bool = False, num_retry_fail: int = 5):
    """Generate a reply from the LLM with optional multimodal tool calling.

    Args:
        content (str): The prompt given to the model.
        role (str, optional): The role to label the message with. 
            Options: 'user', 'assistant', 'system'. Defaults to 'user'.
        model (str, optional): The model to use for generation. Defaults to 'qwen3:8b'.
        thinking (str, optional): Whether to enable tool calling.
            Options: 'auto', 'true', 'false'. Defaults to 'auto'.
        streaming (str, optional): The reply type, either wait till full reply, or show progress over each token. Defaults to 'False'.

    Returns:
        str: The generated reply from the model.
    """
    if num_retry_fail >= 0:
        try:
            if model == None:
                model = DEFAULT_MODEL

            generate = True
            tool_calling = False

            save_context(content, role=role)

            while generate == True:

                if thinking.lower() == 'auto':
                    pass
                elif thinking.lower() == 'true':
                    tool_calling = True
                elif thinking.lower() == 'false':
                    tool_calling = False

                if streaming:
                    response = ollama_client.chat(
                        model=model,
                        messages=context,
                        tools=tools,
                        think=tool_calling,
                        stream=True,
                    )

                    buffer = ""
                    response_chunk = []
                    for part in response:
                        response_chunk.append(part.model_dump())

                        if 'message' in part and 'tool_calls' in part['message']:
                            for tool_call in part['message']['tool_calls']:
                                tool_result = get_tool_type(tool_call)

                                save_context(str(tool_result), 'tool')

                                with open("context.json", "w", encoding="utf-8") as f:
                                    json.dump(context, f, ensure_ascii=False, indent=2)

                            generate = True
                            tool_calling = True

                        elif 'message' in part and part['message'].get('content'):
                            buffer += part['message']['content']
                            yield(part['message']['content'])
                            generate = False
                            tool_calling = False

                    if not generate:
                        yield("")
                        if buffer.strip():
                            save_context(buffer, role='assistant')

                    logs.append(response_chunk)

                    with open("logs.json", "w", encoding="utf-8") as f:
                        json.dump(logs, f, ensure_ascii=False, indent=2)      

                else:
                    response = ollama_client.chat(
                        model=model,
                        messages=context,
                        tools=tools,
                        think=tool_calling,
                        stream=False,
                    )

                    logs.append(response.model_dump(mode='json'))

                    with open("logs.json", "w", encoding="utf-8") as f:
                        json.dump(logs, f, ensure_ascii=False, indent=2)

                    if response['message'].get('content'):
                        save_context(response['message']['content'], 'assistant')
                        yield(response['message']['content'])

                    elif 'tool_calls' in response['message']:

                        for tool_call in response['message']['tool_calls']:
                            tool_result = get_tool_type(tool_call)

                            save_context(str(tool_result), 'tool')

                            with open("context.json", "w", encoding="utf-8") as f:
                                json.dump(context, f, ensure_ascii=False, indent=2)

                        generate = True
                        tool_calling = True
        except ResponseError as e:
            if e.status_code == "524":
                num_retry_fail -= 1
    else:
        return("couldn't generate the message. Please retry with streaming activated `/stream True`.")


def get_model_list():
    """Return a list of all available models on the Ollama server."""
    models_info = ollama_client.list()
    return [model["model"] for model in models_info.get("models", [])]


def send_message(msg: str, flush: bool = False):
    if flush:
        print(msg, end="", flush=True)
    else:
        print(msg)