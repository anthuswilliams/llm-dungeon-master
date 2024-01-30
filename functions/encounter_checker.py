import pandas as pd 
from typing import List
character_table = pd.read_csv('functions/xp_table.csv', index_col='Character level')

difficulties = ["easy", "medium", "hard", "deadly", "impossible"]

def calculate_party_xp(party_levels: List[int], desired_difficulty: str):
    '''
    Calculates the XP thresholds for a party of a given size and level.

    Args:
        party (str): A comma-delimited list of character levels in the party, e.g. "1,1,2"

    Returns:
        Tuple[int, int/float]: The min and max cumulative XP score for the encounter
    '''        
    min = 0
    max = 0
    desired_difficulty = desired_difficulty.lower()

    if desired_difficulty != "easy":
        lesser_difficulty = difficulties[difficulties.index(desired_difficulty) - 1]

    for pl in party_levels:
        assert pl > 0 and pl <= 20, "Character levels must be integers between 1 and 20."
        if desired_difficulty != "impossible":
            max += character_table.loc[pl][desired_difficulty]
        if desired_difficulty != "easy":
            min += character_table.loc[pl][lesser_difficulty]
    
    if max == 0:
        max = float('inf')

    return (min, max)
    
if __name__ == "__main__":
    party = [2, 3, 2, 3]
    print(calculate_party_xp(party, "Impossible")) # 500
