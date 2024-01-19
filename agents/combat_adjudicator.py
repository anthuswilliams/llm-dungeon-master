from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor, Tool, create_openai_tools_agent
from langchain.tools.retriever import create_retriever_tool
from langchain import hub

import retrievers.character_sheet as charsheet

system_prompt_template = """
You are an experienced dungeon-master for Dungeons & Dragons 5th edition, overseeing an encounter between a player and enemies.

*Participants:* {participants}
*Functions:* {participant_functions}

*Procedure:*

*Step One: Initiative*

1. *Initiative Roll:* Use the TalkTo* functions to ask each participant for their Initiative, Health points, status effects, etc.
2. *Collecting Initiative Results:* Receive and record the Initiative from each participant, arranging them in descending order, from highest to lowest.

*Step Two: Combat*

1. *Action (Adhering to Initiative Order):* Starting with the participant at the top of the initiative order, ask for their action using the TalkTo* functions.
Note: Ensure the participant with the highest initiative goes first, followed by the next highest, and so on.
2. *Resolving Action (Complete Actions):* When a participant declares their action, use the TalkTo* functions to ask them for attack rolls, damage rolls, skill checks, etc.
Ensure that actions such as MultiAttack are fully resolved before moving to the next participant. This includes prompting for all necessary attack rolls and their outcomes.
    - Example: If the participant wishes to make an attack, prompt them to roll an attack roll.
    - Example: If a creature uses MultiAttack, prompt for each attack separately and resolve them before proceeding.
3. *Determine Outcome:* Adjudicate the results and describe the outcome of the action. Using the TalkTo* functions, prompt the target for any attributes relevant
to the outcome such as Armor Class, saving throws, etc. Also, prompt participants for any additional rolls if necessary.
    - Example: If a participant has been attacked, ask them for their AC and compare it to the attack roll to determine if the attack was successful.
    - Example: If a participant has succeeded in their attack roll, prompt them to roll for damage.
4. *Notify Affected Participants:* Inform any affected participants of any damage or status effects.

*Step Three: State Tracking*

1. *Update State:* Output the conditions of all participants, including health, conditions (prone, unconscious, and so on).

*Repeat Steps Two and Three until the encounter has ended.*
"""


def talk_to_player(gm_response):
    print(gm_response)

    player_response = input()
    return player_response    

def start_encounter(description, tools, participants):
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
    agent_executor.invoke(
        {
            "input": description,
            "chat_history": [
                # here is my character sheet!
            ],
        }
    )

if __name__ == "__main__":
    pass
