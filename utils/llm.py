import litellm

from anthropic import Anthropic

MODEL_LOOKUP = {
    "claude-opus-4": "claude-opus-4-20250514",
    "claude-sonnet-4":	"claude-sonnet-4-20250514",
    "claude-3.7":	"claude-3-7-sonnet-20250219",
    "claude-3-5-sonnet":	"claude-3-5-sonnet-20240620",
    "claude-3-haiku":	"claude-3-haiku-20240307",
    "claude-3-opus":	"claude-3-opus-20240229",
    "gpt-5": "gpt-5",
    "gpt-5-mini": "gpt-5-mini",
    "gpt-5-nano": "gpt-5-nano",
    "gpt-5-chat": "gpt-5-chat",
    "gpt-4.1": "gpt-4.1",
    "gpt-4.1-mini": "gpt-4.1-mini",
    "gpt-4.1-nano":	"gpt-4.1-nano",
    "o4-mini": "o4-mini",
    "o3": "o3",
    "o3-mini": "o3-mini",
    "o1-mini": "o1-mini",
    "gpt-4o": "gpt-4o",
    "gpt-4o-mini": "gpt-4o-mini",
    "gpt-4": "gpt-4",
    "gpt-4-turbo": "gpt-4-turbo",
    "gpt-3.5-turbo": "gpt-3.5-turbo",
}


def chat_completion(system_prompt, messages, model):
    m = MODEL_LOOKUP.get(model, None)
    if not m:
        raise ValueError(f"Model {model} not found")
    
    message = litellm.completion(
        model=m,
        messages=[{"role": "system", "content": system_prompt}] + messages
    )

    return message


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
    ], model="gpt-5-mini")
    print(message.choices[0].message.content)
