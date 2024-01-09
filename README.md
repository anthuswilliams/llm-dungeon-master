# llm-dungeon-master

## Basic Approach

We are using LangChain (or something like it) to drive the basic flow

1. An LLM functions as a decision-maker, deciding which of a set of tools to call
2. We have a number of smaller language models functioning as agents:
- setting/narrator, responsible for understanding and incorporating D&D settings - semantic memory
- rules adjudicator, in charge of whether a proposed player action is possible, what needs to be rolled, etc.
- episodic memory, e.g. what characters have done, whose turn it is in combat, etc.
3. A number of non-LLM agents, such as
- dice roller/random number generator

Individual agents are developed and tested using https://github.com/anthuswilliams/dnd-benchmarks

## Dealing with combat

There are a number of complex interactions involved in a round of combat.  

1. Initiative tracking 
2. Spacial awareness of the model
3. Checking character/enemy sheets to make sure the moves called for are valid
4. Tracking of current HP and used resources
- describing and applying the outcomes of attacks and spells
5. Encounter balancing
6. Dictating the actions of enemies
- Enemy AI
