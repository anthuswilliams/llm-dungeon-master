from anthropic import Anthropic

MODEL_LOOKUP = {
    "claude-3.5-haiku": "claude-3-5-haiku-20241022",
    "claude-3.7-sonnet": "claude-3-7-sonnet-20250219",
    "claude-4-sonnet": "claude-sonnet-4-20250514",
    "claude-4-opus": "claude-opus-4-20250514",
    "claude-4.1-opus": "claude-opus-4-1-20250805"
}


def chat_completion(system_prompt, messages, client=None, model="claude-3.5-haiku"):
    if not client:
        client = Anthropic()
    message = client.messages.create(
        model=MODEL_LOOKUP.get(model, "claude-3-5-haiku-20241022"),
        max_tokens=8192,
        temperature=0,
        system=system_prompt,
        messages=messages
    )

    return message.content[0].text


if __name__ == "__main__":
    message = chat_completion(system_prompt="You are a helpful dungeon master.", messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Can a Warlock acquire cantrips from another class's spell list?\n"
                }
            ]
        }
    ])
    print(message)
