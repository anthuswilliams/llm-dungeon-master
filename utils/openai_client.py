from openai import OpenAI


def chat_completion(system_prompt, messages, client=None, model="gpt-4o-mini"):
    if not client:
        client = OpenAI()

    response = client.chat.completions.create(
        model=model,
        messages=[{
            "role": "developer",
            "content": [{
                    "type": "text",
                    "text": system_prompt
            }]}] + messages
    )

    return response.choices[0].message.content


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
