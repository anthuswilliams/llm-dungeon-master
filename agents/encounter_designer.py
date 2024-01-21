import json

from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_community.utils.openai_functions import convert_pydantic_to_openai_function
from langchain.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.messages import SystemMessage

from pydantic import BaseModel, Field
from typing import List

class Action(BaseModel):
    """A special move or tactic an enemy may take"""
    name: str = Field("Name of the action")
    description: str = Field("Description of what the action does and how it works")

class StatBlock(BaseModel):
    """Enemy stats definition, should include all innate abilities, spells, skill modifiers, armor class, and initiative"""
    armor_class: int = Field("The enemy's Armor Class")
    hit_point: int = Field("The enemy's Hit Points")
    speed: str = Field("The enemy's base movement speed")
    initiative: str = Field("The enemy's initiative modifier, for example '+1'")

    strength: str = Field("The enemy's strength (STR), should be of the form [[Value]] ([[Modifier]])")
    dexterity: str = Field("The enemy's dexterity (DEX), should be of the form [[Value]] ([[Modifier]])")
    constitution: str = Field("The enemy's constitution (CON), should be of the form [[Value]] ([[Modifier]])")
    intelligence: str = Field("The enemy's intelligence (INT), should be of the form [[Value]] ([[Modifier]])")
    wisdom: str = Field("The enemy's wisdom (WIS), should be of the form [[Value]] ([[Modifier]])")
    charisma: str = Field("The enemy's charisma (CHA), should be of the form [[Value]] ([[Modifier]])")

class Enemy(BaseModel):
    """Defines an enemy including all stats, conditions, and modifiers"""
    name: str = Field("The name of the creature or humanoid enemy")
    stats: StatBlock = Field("""The stat block for the enemy""")
    cr: str = Field("The enemy's Challenge Rating")
    xp: int = Field("The XP value of the enemy")
    actions: List[Action] = Field("A list of actions that the enemy may take")
    other_info: str = Field("Any other information relevant to how the enemy appears, acts, moves, or behaves")

class Player(BaseModel):
    """Defines a player character who will participate in the encounter"""
    level: int = Field("The player's level")

class Encounter(BaseModel):
    """Defines an encounter including any enemies, terrain, setting, etc."""
    enemies: List[Enemy] = Field("List of enemies included in the encounter")
#    players: List[Player] = Field("List of players included in the encounter")
#    difficulty: str = Field("The difficulty level of the encounter")


system_message = """
You are designing an encounter for Dungeons and Dragons 5th Edition.  You have the following information:
Input Parameters:

Player Information: Number of players and their respective levels.
Desired Difficulty Level: Easy, Medium, Hard, or Deadly.
Narrative and Setting Context: Brief description of the current narrative and setting in which the encounter will take place.

As the encounter designer you should consider the following:

Select Appropriate Creatures: Choose creatures with Challenge Ratings (CR) that match the desired difficulty level, ensuring that the total encounter difficulty is appropriate for the players' strength.
Encounter Design Principles:
Balance: Ensure that the encounter matches the desired difficulty level.
Narrative Integration: Design the encounter to fit seamlessly into the ongoing story and setting.
Output of encounter details:
Provide a list of creatures or adversaries, including their CRs and XP.
"""

input_message = """
Player Information: {players}
Desired Difficulty Level: {difficulty}
Narrative and Setting Context: {setting}
"""

def design_encounter(instructions):        
    model = ChatOpenAI(temperature=0)
    parser = JsonOutputFunctionsParser()

    chain = (
        ChatPromptTemplate.from_messages([
            SystemMessage(content=system_message),
            HumanMessagePromptTemplate.from_template(input_message)
        ])
        | model.bind(functions=[convert_pydantic_to_openai_function(Encounter)])
        | parser
       # | RunnablePassthrough.assign(xp_values=lambda r: [e["xp"] for e in r["enemies"]])
    )

    return chain.invoke({"players": "3 level 1 players", "difficulty": "medium", "setting": "temple"})


if __name__ == "__main__":
    encounter = design_encounter("Design an encounter for three level 1 players that is medium difficulty, and is set in a temple.")
    
    print(json.dumps(encounter, indent=4))