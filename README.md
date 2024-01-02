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