import simpleaichat

from pydantic import BaseModel, Field
from typing import List

system_prompt = """
**You are an experienced dungeon-master for Dungeons & Dragons 5th edition, overseeing an encounter between a player and enemies.**

**Functions:**
`TalkToParticipant` - use this to communicate with the participant whose turn it is to act
`TalkToTarget` - use this to communicate with the target of the participant's actions

Your role is to fully resolve a single turn. The user will tell you whose turn it is and what the current state of the battlefield is.
Use the "TalkTo*" function to interact with participants for their actions and responses.

**Procedure:**

**Step One: Request Participant's Action.** 
- Use the `TalkToParticipant` function to ask the current participant for their action.
Provide them with the current state of the battlefield to inform their decision.

**Step Two: Resolving Action (Complete Actions):**
- Once a participant declares their action, use `TalkToParticipant` to prompt them for any necessary rolls (attack rolls, damage rolls,
skill checks, etc.). Ensure you have all the information needed before proceeding.

**Step Three: Determine Outcome:**
- Adjudicate the results and describe the outcome of the action. Use `TalkToTarget` to prompt the target for relevant attributes like
Armor Class, saving throws, etc. Prompt participants for any additional rolls if necessary.
    - Example: If a participant is attacked, use `TalkToTarget` to ask for their AC and compare it to the attack roll.
    - Example: If a participant's attack is successful, prompt them to roll for damage using `TalkToParticipant`.

**Step Four: Notify Affected Participants:**
- Inform any affected participants of the results, including damage or status effects, using `TalkToTarget`.

*Note: Some actions, like MultiAttack, require repeating Steps 2-4. Repeat these steps until all actions are fully resolved.*

**Step Five: End of Turn:**
- Output the condition of all participants, including health and status effects, in the following format:
  - Name: [[Name]]
  - Current HP: [[HP]]
  - Status Effects: [[Status Effects]]
"""

class Initiative(BaseModel):
    """A dictionary including the name of the participant and their initiative"""
    participant: str = Field("The name of the participant")
    value: int = Field("The participant's initiative value")


class Participant(BaseModel):
    """A summary of information pertaining to a participant in the encounter"""
    HP: int = Field("The participant's current Health Points")
    AC: int = Field("The participant's Armor Class")
    status_effects: List[str] = Field("A list of status effects affecting the participant")

class State(BaseModel):
    """Defines the current state of the battlefield"""
    to_act: str = Field("The name of the participant whose turn it is to act")
    participants: List[Participant] = Field("List of participants in the encounter")
    initiative_order: List[Initiative] = Field("List of initiative values in the encounter")


# def select_tool()

def evaluate_turn(tools, current_state):
    ai = simpleaichat.AIChat(
        console=False,
        save_messages=False,
        model="gpt-3.5-turbo",
        params={"temperature": 0.0},
        system=system_prompt
    )

    response_structured = ai(
        json.dumps(current_state.model_dump()),
        tools=tools,
#        output_schema=State
    )

    print(response_structured)

#    while response_structured["tool"] is not None:
#        print(json.dumps(response_structured, indent=4))
#        response_structured = ai(response_structured["response"], tools=tools, output_schema=State)

    return response_structured


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

    def talk_to_target(message):
        """Use this to talk to Captain Cura. Use complete sentences!"""
        response = cura.talk(message)
        return response["output"]
    
    def talk_to_participant(message):
        """Use this to talk to Big Pete. Use complete sentences!"""
        response = thug.talk(message)
        return response["output"]

    tools = [talk_to_participant, talk_to_target]

    initiative = [
        {"participant": "Big Pete", "value": 22},
        {"participant": "Captain Cura", "value": 18}
    ]
    t = evaluate_turn(tools, State.model_validate({
        "to_act": "Big Pete",
        "participants": [
            {"name": "Captain Cura", "HP": 16, "AC": 14, "status_effects": []},
            {"name": "Big Pete", "HP": 32, "AC": 15, "status_effects": []},
        ],
        "initiative_order": initiative
    }))
    print(json.dumps(t, indent=4))


