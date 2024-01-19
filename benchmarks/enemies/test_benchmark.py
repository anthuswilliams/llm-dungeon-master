import sys
import os
from glob import glob
import json
import pytest

from langchain.agents import Tool

import agents.enemy as ae

with open("questions.json", "r") as fh:
    questions = json.loads(fh.read())

def fixed_dice_roll(query):
    return 4 # valid for any dice roll!

injected_tools = [
    Tool(
        name="RollDice",
        func=fixed_dice_roll,
        description="call this to get the result of rolling dice.",
    )
]

test_cases = []
for enemy_file in glob("sheets/*.json", root_dir=sys.path[0]):
    with open(os.path.join(sys.path[0], enemy_file)) as fh:
        e = json.loads(fh.read())
        for q in questions:
            test_cases.append({"e": e, "q": q})

def apply(case):
    
    
    return {**case["q"], "enemy": case["e"]["name"], "output": exc or response["output"]}

@pytest.mark.parametrize("case", test_cases)
def test_case(case):
    combatant = ae.Enemy(name=case["e"]["name"], stats=case["e"], identifier=case["e"]["name"], injected_tools=injected_tools)
    exc = None
    if case["q"].get("history", None):
        for m in case["q"]["history"]:
            try:
                combatant.talk(m)
            except Exception as e:
                exc = e

    if not exc:
        try:
            response = combatant.talk(case["q"]["question"])
        except Exception as e:
            exc = e
    
    

import concurrent.futures
results = []
with concurrent.futures.ProcessPoolExecutor(max_workers=8) as executor:
    for out in executor.map(apply, test_cases):
        results.append(out)

