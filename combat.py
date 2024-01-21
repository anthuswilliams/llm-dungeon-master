from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor, Tool, create_openai_tools_agent

from agents.combat_adjudicator import evaluate_turn

if __name__ == "__main__":
     import json
    import agents.enemy as enemy
    import agents.npc as npc

    cura = npc.NPC(name="Captain Cura")
    with open("benchmarks/enemies/sheets/thugs.json", "r") as fh:
        content = fh.read()
        thug = enemy.Enemy("thug", json.loads(content), "Big Pete")
    
    participants = [
        {"type": "NPC", "name": "Captain Cura"},
        {"type": "thug", "name": "Big Pete"}
    ]

    tools = [
        Tool(
            name="TalkToTarget",
            func=cura.talk,
            description="Use this to talk to Captain Cura. Use complete sentences!"
        ),
        Tool(
            name=f"TalkToParticipant",
            func=thug.talk,
            description=f"Call this to to talk to Big Pete. Use complete sentences!",
        ),
    ]

    initiative = [
        {"participant": "Big Pete", "value": 22},
        {"participant": "Captain Cura", "value": 18}
    ]

    current_state = {
            "to_act": "Big Pete",
            "participants": [
                {"name": "Captain Cura", "HP": 16, "AC": 14, "status_effects": None},
                {"name": "Big Pete", "HP": 32, "AC": 15, "status_effects": None},
            ],
            "initiative_order": initiative
    }
    while True:
        for i in initiative:
            next_state = evaluate_turn(tools, participants, current_state)
            print(next_state)
