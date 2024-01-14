from agents.combat_adjudicator import start_encounter, talk_to_player
import agents.encounter_designer as e
import agents.enemy as enemy

from langchain.agents import Tool

encounter = e.design_encounter(
    "Design a medium difficulty encounter for 1 level 7 player. It should be set in a city."
)
print(encounter)

tools = [
    Tool(
        name="TalkToPlayer",
        func=talk_to_player,
        description="Call this to to talk to the player.",
    ),
]
participants = [{"type": "Player", "name": "Player"}]

for i, e in enumerate(encounter["enemies"]):
    # seed an enemy agent
    enemy_type = e["name"]
    identifier = f"{enemy_type}_{i}"

    # combatant = enemy.Enemy(enemy_type, e, identifier)

    participants.append({"type": enemy_type, "name": identifier})

    # create a TalkToEnemy tool
    tools.append(
        Tool(
            name=f"TalkTo{identifier}",
            func=enemy.Enemy(enemy_type, e, identifier).talk,
            description=f"Call this to to talk to {identifier}.",
        ),
    )

print(tools)

# call the combat adjudicator with the enemy stat sheet and a reference to the enemy agent
start_encounter("Start the encounter", tools, participants)
# profit?
