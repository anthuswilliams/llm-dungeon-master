import pandas as pd 
from typing import List
character_table = pd.read_csv('functions/xp_table.csv', index_col='Character level')

def calculate_party_xp(party_levels: List[int]):
    '''
    Calculates the XP thresholds for a party of a given size and level.

    Args:
        party (List[int]): A list of character levels in the party.

    Returns:
        pd.Series: A series of XP thresholds for Easy, Medium, Hard, and Deadly encounters.
    '''
    try:
        below_threshold = [n for n in party_levels if n <0]
        above_threshold = [n for n in party_levels if n >20]
    except:
        raise ValueError('Character levels must be integers between 1 and 20.')

    if len(below_threshold) or len(above_threshold):
        raise ValueError('Character levels must be between 1 and 20.')
    
    members = pd.Series([0, 0, 0, 0], index=['Easy', 'Medium', 'Hard', 'Deadly'])  
    for member in party_levels:
        members += character_table.loc[member]
    return members

def determine_difficulty(party_levels: List[int], enemies_xp: List[int]):
    '''
    Determines the difficulty of an encounter based on the party and enemy XP.

    Args:
        party (List[int]): A list of character levels in the party.
        enemies_xp (List[int]): A list of XP values for the enemies in the encounter.
    
    Returns:
        str: The difficulty of the encounter.  One of 'Easy', 'Medium', 'Hard', or 'Deadly'.
    '''
    xp_thresholds = calculate_party_xp(party_levels)
    total_xp = sum(enemies_xp)

    if total_xp <= xp_thresholds['Easy']:
        return 'Easy'
    elif total_xp <= xp_thresholds['Medium']:
        return 'Medium'
    elif total_xp <= xp_thresholds['Hard']:
        return 'Hard'
    else:
        return 'Deadly'
    
if __name__ == "__main__":
    party = [2, 3, 2, 3]
    enemies_xp = [200, 200, 200, 200]
    print(determine_difficulty(party, enemies_xp))