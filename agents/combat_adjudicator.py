from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor, Tool, create_openai_tools_agent
from langchain import hub

system_prompt_template = """
You are an experienced dungeon-master for Dungeons & Dragons 5th edition, overseeing an encounter between a player and enemies.

*Participants:* {participants}
*Functions:* {participant_functions}
*Player Assistant Function:* TalkToPlayerAssistant - use complete sentences, and include the player's character name in EVERY message.
(Example: [[Character name]] needs to make an attack roll)
(Example: What would [[Character name]] like to do?)

*Procedure:*

*Step One: Action (Adhering to Initiative Order):*  Starting with the participant at the top of the initiative order, engage with each
using the appropriate method. For non-player characters, use the `TalkTo*` functions. For the player character, use `TalkToPlayerAssistant`
and address them by their character name, asking for their action.

*Step Two: Resolving Action (Complete Actions):* When a participant declares their action, follow the appropriate procedure:
    - For non-players, prompt them to roll for attack rolls, damage rolls, skill checks, etc., using `TalkTo*`.
    - For the player, use `TalkToPlayerAssistant` to interact with their character sheet and prompt for rolls and actions.
    - Example: If the participant wishes to make an attack, prompt them to roll an attack roll.
    - Example: If a creature uses MultiAttack, prompt for each attack separately and resolve them before proceeding.

*Step Three: Fully Resolving a Turn:* Ensure actions like MultiAttack are fully resolved before moving on to the next step.

*Step Four: Determine Outcome:* Adjudicate the results and describe the outcome of the action. Using the TalkTo* functions, prompt the target
for any attributes relevant to the outcome such as Armor Class, saving throws, etc. Also, prompt participants for any additional rolls if necessary.
    - Example: If a participant has been attacked, ask them for their AC and compare it to the attack roll to determine if the attack was successful.
    - Example: If a participant has succeeded in their attack roll, prompt them to roll for damage.

*Step Five: Notify Affected Participants:* Inform any affected participants of the outcome.
    - For non-player characters, use the TalkTo* functions to inform them of any damage or status effects
    - For the player, use `TalkToPlayerAssistant` to inform them of any damage or status effects.

*Step Six: End of Round:* Output the conditions of all participants, including health, conditions (prone, unconscious, and so on).
Use the following format:
Name:
Current HP:
Status Effects:
"""
def start_round(tools, participants, initiative):
    # Get the prompt to use - you can modify this!
    prompt = hub.pull("hwchase17/openai-tools-agent")
    participant_functions = "\n".join(
        [f'TalkTo{p["name"]} - Function to talk to {p["name"]}' for p in participants]
    )
    participant_names = [f'Name: {p["name"]}\nType: {p["type"]}' for p in participants]

    prompt.messages[0].prompt.template = system_prompt_template.format(
        participants="\n\n".join(participant_names), participant_functions=participant_functions
    )

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent, tools=tools, verbose=True, handle_parsing_errors=True
    )

    initiative_strs = "\n".join([f'{i["participant"]}: {i["value"]}' for i in initiative])
    return agent_executor.invoke(
        {
            "input": f"Initiative Order: {initiative_strs}",
            "chat_history": [
                # here is my character sheet!
            ],
        }
    )

if __name__ == "__main__":
    import json
    import agents.enemy as enemy
    import agents.player_assistant as pa
    import agents.npc as npc

    cura = npc.NPC(name="Captain Cura")
    with open("benchmarks/enemies/sheets/thugs.json", "r") as fh:
        content = fh.read()
        thug = enemy.Enemy("thug", json.loads(content), "Big Pete")
    
    participants = [
        {"type": "NPC", "name": "Captain Cura"},
        {"type": "thug", "name": "Big Pete"}
    ]

    thug.talk("You are in an alley, face to face with Captain Cura, a hero. Heroes make you sick!")
    cura.talk("You encounter a lumbering thug named Big Pete. He looks ready to fight!")
    tools = [
        Tool(
            name="TalkToCaptainCura",
            func=cura.talk,
            description="Use this to talk to Captain Cura. Use complete sentences!"
        ),
        Tool(
            name=f"TalkToBigPete",
            func=thug.talk,
            description=f"Call this to to talk to Big Pete. Use complete sentences!",
        ),
    ]

    initiative = [
        {"participant": "Big Pete", "value": 22},
        {"participant": "Captain Cura", "value": 18}
    ]
    start_round(tools, participants, initiative)


