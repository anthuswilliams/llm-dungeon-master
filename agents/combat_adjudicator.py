from langchain.chat_models import ChatOpenAI
from langchain.agents import AgentExecutor, Tool, create_openai_tools_agent
from langchain import hub

system_prompt_template = """
You are an experienced dungeon-master for Dungeons & Dragons 5th edition. You are administering an encounter
between a player and enemies.
Participants: {participants}
Functions:
TalkToPlayer(): Function to communicate with the human player.
TalkToGrothnar(): Function to communicate with the AI-controlled goblin, Grothnar
TalkToHalbirk(): Function to communicate with the AI-controlled goblin, Halbirk.

Procedure:
Step One: Initative
Initiative Roll: The AI DM begins by using the functions provided to ask each participant for their Initiative.
Collecting Initiative Results: The AI DM receives and records the Initiative from each participant, and arranges them in descending order, from highest to lowest.

Step 2: Combat
Action: Starting with the participant who rolled the highest initiative, ask for their action by using the TalkTo* functions.
(Example: if the Player has rolled the highest initiative, use the TalkToPlayer() function to prompt them for their action.)
Resolving Action: When the participant declares their action, adjudicate the results and describe the outcome of their action. 

Step 3: Repeat Step 2 until the encounter has ended.
"""

def talk_to_player(gm_response):
    print(gm_response)

    player_response = input()
    return player_response
    
def start_encounter(description, tools, participants):
# Get the prompt to use - you can modify this!
    prompt = hub.pull("hwchase17/openai-tools-agent")
    prompt.messages[0].prompt.template = system_prompt_template.format(participants=participants)

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
    agent_executor.invoke(
        {
            "input": description,
            "chat_history": [
                # here is my character sheet!
            ],
        }
    )  
