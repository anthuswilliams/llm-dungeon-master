import json
from pydantic import BaseModel, Field
from typing import List, Type, Optional

from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.agents import AgentFinish
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool

import functions.encounter_checker as ec

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

class DifficultyArgs(BaseModel):
    player_levels: List[int] = Field("an integer list of the players in the party")
    desired_difficulty: str = Field("the desired difficulty")

class DifficultyMap(BaseTool):
    name = "DifficultyMap"
    description = "returns total XP for an encounter for a party of adventurers"
    args_schema: Type[BaseModel] = DifficultyArgs

    def _run(
        self, player_levels: List[int], desired_difficulty: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ):
        """Use the tool."""
        return ec.calculate_party_xp(player_levels, desired_difficulty)
    
    async def _arun(
        self,
        player_levels: List[int],
        desired_difficulty: str,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("does not support async")
    
class StructureEncounter(BaseTool):
    name="StructureEncounter"
    description = "structures an encounter according to the desired output format"
    args_schema: Type[BaseModel] = Encounter

    def _run(
        self, enemies: List[Enemy], run_manager: Optional[CallbackManagerForToolRun] = None
    ):
        """Use the tool"""
        return AgentFinish(return_values={"output": {"enemies": enemies}}, log=json.dumps([e.model_dump_json() for e in enemies]))

    async def _arun(
        self,
        enemies: List[Enemy],
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("does not support async")


system_message = """
You are designing an encounter for Dungeons and Dragons 5th Edition. The user will provide:
Player Information: Number of players and their respective levels.
Desired Difficulty Level: Easy, Medium, Hard, or Deadly.
Narrative and Setting Context: Brief description of the current narrative and setting in which the encounter will take place.

You have access to the following tools:
`DifficultyMap` - used to determine the allowable range of enemy XP for the players and their respective levels
`StructureEncounter` - used to structure the encounter you design according to the user's desired output format


Use `DifficultyMap` to choose creatures with XP that match the desired difficulty level, ensuring that the total
encounter difficulty is appropriate for the players' strength. Select one or more enemies such that:
- the sum of the XP of all enemies does not exceed the desired difficulty level
- the creatures are an evocative part of the narrative and setting the user has chosen

Output of encounter details:
Provide a list of creatures or adversaries, including their CRs and XP. Use the `StructureEncounter` tool to format this.

{agent_scratchpad}
"""

def design_encounter(instructions):
    model = ChatOpenAI(temperature=0)

    tools = [
        DifficultyMap(),
        StructureEncounter()
    ]

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=system_message),
        HumanMessagePromptTemplate.from_template("{instructions}"),
        MessagesPlaceholder("agent_scratchpad"),
    ])

    agent = create_openai_tools_agent(llm=model, tools=tools, prompt=prompt)

    executor = AgentExecutor(
        agent=agent, tools=tools, verbose=True, handle_parsing_errors=True
    )        
    
    return executor.invoke({"instructions": instructions})
    

if __name__ == "__main__":
    encounter = design_encounter("Design an encounter for three level 1 players that is medium difficulty, and is set in a mysterious forest, which has gone unexplored for 1000 years.")
    
    print(encounter)
#    print(json.dumps(encounter, indent=4))