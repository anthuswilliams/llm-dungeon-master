import re
import random

from typing import List


def dice_roll(query: str) -> List[int]:
    results = re.search(r"^(\d+)d(\d+)(\s?(\+|-)\s?\d+)?$", query)
    if not results:
        raise ValueError(f"query {query} is uninterpretable")

    num = results.group(1)
    val = results.group(2)
    modifier = results.group(3)

    # TODO: return signature here is inconsistent. The issue is we haven't nailed down how the caller is asking for rolls.
    #  For example, when rolling with advantage, it sometimes calls for 2d20 and keeps the higher, and sometimes it calls for 2d20kh1, i.e. expecting us to do that here
    #
    # In other cases, the intent is not to discard a roll but to sum them, e.g. when rolling for damage it might call for 3d6+3
    result = [random.randint(1, int(val)) for i in range(int(num))]
    if modifier:
        modifier = int(modifier.strip()[1:]) * (-1 if modifier.strip()[0] == "-" else 1)
        return sum(result) + modifier
    else:
        return result