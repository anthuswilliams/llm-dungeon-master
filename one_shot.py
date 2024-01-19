from agents.combat_adjudicator import start_encounter
import agents.encounter_designer as e
import agents.enemy as enemy
import agents.player_assistant as pa

from langchain.agents import Tool

encounter = e.design_encounter(
    "Design a medium difficulty encounter for 1 level 1 player. It should be set in a city."
)
print(encounter)

tools = [
    Tool(
        name="TalkToPlayerAssistant",
        func=pa.PlayerAssistant().talk,
        description="Call this to to talk to the player's assistant. Use complete sentences!",
    ),
]
participants = [{"type": "Player", "name": "Captain Cura"}]

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
            description=f"Call this to to talk to {identifier}. Use complete sentences!",
        ),
    )

print(tools)

# call the combat adjudicator with the enemy stat sheet and a reference to the enemy agent
start_encounter("Start the encounter", tools, participants)
# profit?
