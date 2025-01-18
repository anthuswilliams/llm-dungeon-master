from anthropic import Anthropic


def chat_completion(system_prompt, messages, client=None):
    if not client:
        client = Anthropic()
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
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
