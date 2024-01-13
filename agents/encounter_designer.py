import simpleaichat

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
    actions: List[Action] = Field("A list of actions that the enemy may take")
    other_info: str = Field("Any other information relevant to how the enemy appears, acts, moves, or behaves")

class Encounter(BaseModel):
    """Defines an encounter including any enemies, terrain, setting, etc."""
    enemies: List[Enemy] = Field("List of enemies included in the encounter")


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
    Provide a list of creatures or adversaries, including their CRs.
"""

def design_encounter(instructions):        
    ai = simpleaichat.AIChat(console=False,
        save_messages=False,
        model="gpt-3.5-turbo",
        params={"temperature": 0.0},
        system=system_message
    )

    response_structured = ai(
        instructions,
        output_schema=Encounter
    )

    return response_structured


if __name__ == "__main__":
    encounter = design_encounter("Design an encounter for three level 1 players that is medium difficulty, and is set in a desert.")
    print(encounter)