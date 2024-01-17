import json
import shutil
from glob import glob

from openai import OpenAI

import CONSTANTS as c

client = OpenAI()

def score_game(conversation):
    messages = [
        {"role": "system", "content": c.JUDGE_PROMPT},
        {"role": "user", "content": conversation},
    ]

    completion = client.chat.completions.create(
        model="gpt-4-1106-preview", messages=messages
    )

    return completion.choices[0].message.content

def evaluate():
    convo_files = glob("benchmarks/player_assistant/unscored/*.json")
    current_scores = []

    for filepath in convo_files:
        with open(filepath, "r", encoding="utf-8") as fh:
            convos = json.loads(fh.read())

        filename = filepath.split("/")[-1]

        for character, convo in convos.items():
            print(f"evaluating {filename} for {character}")
            score = score_game(convo)

            current_scores.append({
                "file": filename,
                "character": character,
                "judge_prompt": c.JUDGE_PROMPT,
                "explanation": score,
            })

        with open(f"benchmarks/player_assistant/scores.json", "a") as fh:    
            fh.write(json.dumps(current_scores, indent=4)) 
        
        shutil.move(filepath, f'benchmarks/player_assistant/scored/{filename}')
