from langchain.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import AgentExecutor, Tool, create_openai_tools_agent
from langchain import hub
from functions.dice_roller import dice_roll

import retrievers.character_sheet as chardb

prompt_template = """
You are an experienced player of of Dungeons & Dragons 5th edition.  You will be identified by the name {identifier}.
You are a powerful Firbolg Barbarian, prone to bouts of rage and aggression when faced with evil. You never back down from
a fight!

Tools:
`RollDice` - used to roll dice
`RetrieveCharacterInfo` - used to ask questions and obtain information from your character sheet. Use third person when calling this.
Examples:
What is {identifier}'s Strength Modifier?
What is {identifier}'s attack bonus with the greataxe?


When you are asked to make a roll, you (a) roll the dice using the `RollDice()` function,
and then (b) apply any modifiers as indicated in your character sheet (obtained using the `RetrieveCharacterInfo()` function)
IMPORTANT!!! YOU MUST ALWAYS CHECK THE CHARACTER SHEET TO KNOW THE CORRECT MODIFIERS TO APPLY.

Example:
I rolled a 4. I have [[initiative modifier]] on initiative, so my initiative is [[4 + initiative_modifier]]
"""

tools = [
    Tool(
        name="RollDice",
        func=dice_roll,
        description="call this to get the result of rolling dice.",
    ),
    Tool(
        name="RetrieveCharacterInfo",
        func=chardb.retriever_tool,
        description="call this to get information from the character sheet",
    ),
]


class NPC:
    def __init__(self, name, injected_tools=None):
        # Get the prompt to use - you can modify this!
        prompt = hub.pull("hwchase17/openai-tools-agent")
        self.messages = []
        prompt.messages[0].prompt.template = prompt_template.format(
            identifier="Captain Cura",
        )

        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

        t = injected_tools or tools
        agent = create_openai_tools_agent(llm, t, prompt)
        self.executor = AgentExecutor(
            agent=agent, tools=t, verbose=True, handle_parsing_errors=True
        )

    def talk(self, message):
        response = self.executor.invoke(
            {
                "input": message,
                "chat_history": self.messages,
            }
        )
        self.messages += [
            HumanMessage(content=message),
            AIMessage(content=response["output"]),
        ]
        return response
