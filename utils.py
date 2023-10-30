import re

def extract_number(s):
    match = re.search(r'\d+', s)
    if match:
        number = int(match.group())
        return number
    else:
        return None
