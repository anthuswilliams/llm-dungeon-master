import pandas as pd 
from typing import List
character_table = pd.read_csv('functions/xp_table.csv', index_col='Character level')

def calculate_party_xp(party_levels: List[int], desired_difficulty: str):
    '''
    Calculates the XP thresholds for a party of a given size and level.

    Args:
        party (str): A comma-delimited list of character levels in the party, e.g. "1,1,2"

    Returns:
        int: The max cumulative XP score for the encounter
    '''        
    ret = 0
    desired_difficulty = desired_difficulty.lower()

    for pl in party_levels:
        assert pl > 0 and pl <= 20, "Character levels must be integers between 1 and 20."
        ret += character_table.loc[pl][desired_difficulty]    

    return ret
    
if __name__ == "__main__":
    party = [2, 3, 2, 3]
    print(calculate_party_xp(party, "Medium")) # 500
