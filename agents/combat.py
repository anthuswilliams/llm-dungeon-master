import json
from openai import OpenAI

from utils.dice_roller import dice_roll
from adjudicator import query as consult_players_handbook

tools = [
    {
        "type": "function",
        "function": {
            "name": "consult_players_handbook",
            "description": "Ask a question pertaining to the rules, setting, lore, or current situtation. Call this whenever you need more information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "A question that should be answered by consulting the available reference materials. Share all relevant details.",
                    },
                },
                "required": ["question"],
                "additionalProperties": False,
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "dice_roller",
            "description": "Roll a dice with a given number of sides.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dice": {
                        "type": "string",
                        "description": "The total number of dice and the number of sides on each die, e.g. '2d6'.",
                    },
                },
                "required": ["dice"],
                "additionalProperties": False,
            },
        }
    }
]

pc_info = """
Cedric van Zorndt (the Player)
Human Rogue Lvl 1
Armor Class 14
Hit Points 9
STR 12 (+1) - DEX 16 (+3) - CON 13 (+1) - INT 9 (-1) - WIS 12 (+1) - CHA 15 (+2)
Proficiency bonus: +2
Proficiencies:
- Armor: light armor
- Weapons: Simple weapons, hand crossbows, longswords, rapiers, shortswords
- Tools: Thieves' tools
Saving Throws: Dexterity, Intelligence
Skills: Acrobatics, Deception, Sleight of Hand, Stealth
Equipment: Shortsword, shortbow with a quiver of 20 arrows, burglar's pack, leather armor, two daggers, thieves' tools
Expertise: Stealth, Thieves' tools
Sneak attack 1d6
    """

npc_info = """
Imp (NPC)
Armor Class 13
Hit Points 10
STR 6 (-2) - DEX 17 (+3) - CON 13 (+1) - INT 11 (+0) - WIS 12 (+1) - CHA 14 (+2)
Speed 20 (Fly 40) (20 in Rat form, 20 fly 60 in Raven form, 20 climb 20 in Spider form)
Skills: Deception +4 Insight +3 Persusasion +4 Stealth +5
Damage Resistances: Cold; bludgeoning, piercing and slashing from non-magical attacks that aren't silvered
Damage Immunities: Fire, poison
Condition Immunities: poisoned
Senses: darkvision 120ft; Passive perception 11
Languages: Infernal, Common
Challenge: 1 (200 XP)
Shapechanger: Te imp can use its action to polymorph into the beast form of a rat, a raven, or a spider, or into its devil form. Its statistics are
the same for each form, except for the speed changes noted. Any equipment it is wearing or carrying is not transformed. It reverts to its devil form if it dies.
Devil's Sight: Magical darkness doesn't impede the imp's darkvision.
Magic Resistance: The imp has advantage on saving tghrows against spells and other magical effects.
Actions:
- Sting (Bite in Beast Form). Melee weapon Attack: +5 to hit, reach 5 ft, one creature. Hit: 5 (1d4+3) piercing damage, and the target must make a DC 11 Constitution saving throw, taking 10 (3d6) poison damage on a failed save, or half as much on a successful one.
- Invisibility. The imp magically turns invisible until it attacks or until its concentration ends (as if concentrating on a spell). Any equipment the imp wears or carries is invisible with it.
"""


def call_open_ai(client, messages, tools):
    return client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
    )


def resolve_attack(client, conversations, tools):
    total_tool_calls = 0
    while True:
        # the basic idea is, we are keeping track of conversations which follow the initial developer instruction
        #  and we will pass in different sets of developer instructions depending on the context. But the conversations
        #  array will be the same throughout the encounter.
        response = call_open_ai(client, conversations, tools)
        conversations.append(response.choices[0].message)
        # If the response has a tool call, call the tool
        if response.choices[0].message.content:
            print(response.choices[0].message.content)

        if response.choices[0].message.tool_calls:
            for tc in response.choices[0].message.tool_calls:
                if tc.function.name == "consult_players_handbook":
                    tool_result = consult_players_handbook(
                        json.loads(tc.function.arguments)["question"])
                    conversations.append({
                        "role": "tool",
                        "content": tool_result,
                        "tool_call_id": tc.id
                    })
                elif tc.function.name == "dice_roller":
                    tool_result = dice_roll(json.loads(
                        tc.function.arguments)["dice"])
                    conversations.append({
                        "role": "tool",
                        "content": str(tool_result),
                        "tool_call_id": tc.id
                    })
                total_tool_calls += 1
            if total_tool_calls >= 5:
                break
        else:
            user_input = input("")
            if user_input == "stop" or user_input == "end of turn":
                return user_input, conversations
            conversations.append({
                "role": "user",
                "content": user_input
            })

    # in case we reach the max number of tool calls
    return "stop", conversations


def combat_round(client):
    max_iter = 15
    conversations = [
        {
            "role": "developer",
            "content": """
                You are a Dungeon Master overseeing a combat encounter. The player and NPC will take turns making decisions and resolving actions.
                When it is the player's turn, you will ask for their action and you will determine the outcome.
                When it is the NPC's turn, you will determine the NPC's action and the outcome.

                If the player needs to make a roll (even if it is as a result of an NPC's action), you will ask the player for the roll.
                If the NPC needs to make a roll (even if it is as a result of a player's action), use the dice_roller tool.
                
                IMPORTANT: Use only the information you have been given to narrate the outcome. Whenever a question cannot be resolved with the information
                you have been given, you MUST use the consult_players_handbook tool to get up-to-date information. This includes any information about the rules of the game,
                the setting, the mechanics, NPC stat sheets, and so on.
            """
        },
        {
            "role": "developer",
            "content": consult_players_handbook("Give me the rules I need to know to resolve a turn in combat.")
        },
        {
            "role": "developer",
            "content": f"""
                Players:
                {pc_info}
            """
        },
        {
            "role": "developer",
            "content": f"""
                NPCs:
                {consult_players_handbook("Give me the stat block for an Imp.")}
            """
        }
    ]

    while True:
        max_iter -= 1
        user_input = input("What would you like to do?\n")
        if user_input == "stop":
            break
        conversations.append({"role": "user", "content": user_input})
        stop_code, conversations = resolve_attack(client, conversations, tools)

        print(f"The total conversation so far is: {conversations}")
        if stop_code == "stop" or max_iter == 0:
            break


if __name__ == "__main__":
    client = OpenAI()
    combat_round(client)
