from langchain.chat_models import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

chat = ChatOpenAI()

system_prompt = """
You are an experienced dungeon master for Dungeons & Dragons 5th edition. We are going to play a short encounter.
You will be in charge of keeping track of the order in which they take their turns.

There are three participants in this encounter. One player at a time, you will ask each participant what 
their name is and their Initiative and wait for their response.

"""

messages = [
    SystemMessage(content=system_prompt),
]

response = chat.invoke(messages)
print(response)

goblin_a_prompt = """
You are a goblin in a game of Dungeons & Dragons 5th edition. 
You are in a dungeon and you are about to fight a party of adventurers.
Here are your stats:
    Name: Goblin A
    Initiative: 3
    Armor Class: 15
    Hit Points: 7
"""

goblin_a_messages = [
    SystemMessage(content=goblin_a_prompt),
    HumanMessage(content=response.content),
]

goblin_a_response = chat.invoke(goblin_a_messages)
print(goblin_a_response)

messages.append(AIMessage(content=response.content))
messages.append(HumanMessage(content=goblin_a_response.content))

response_two = chat.invoke(messages)
print(response_two)

goblin_b_prompt = """
You are a goblin in a game of Dungeons & Dragons 5th edition. 
You are in a dungeon and you are about to fight a party of adventurers.
Here are your stats:
    Name: Goblin B
    Initiative: 13
    Armor Class: 15
    Hit Points: 7
"""

goblin_b_messages = [
    SystemMessage(content=goblin_b_prompt),
    HumanMessage(content=response_two.content),
]

goblin_b_response = chat.invoke(goblin_b_messages)
print(goblin_b_response)

messages.append(AIMessage(content=response_two.content))
messages.append(HumanMessage(content=goblin_b_response.content))

response_three = chat.invoke(messages)
print(response_three)

messages.append(AIMessage(content=response_three.content))
messages.append(HumanMessage(content="My name is Captain Cura and my initiative is 20"))

response_four = chat.invoke(messages)
print(response_four)