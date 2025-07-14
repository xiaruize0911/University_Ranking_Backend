import pandas as pd
import csv
import re
import json

ALIASES = {
    'mit': 'massachusetts institute of technology',
    'caltech': 'california institute of technology',
    'ucb': 'university of california berkeley',
    'stanford': 'stanford university',
    # Add more aliases as needed
}

def normalize_name(name: str) -> str:
    # Lowercase
    name = name.lower()
    # Remove text in parentheses, like "(MIT)"
    name = re.sub(r'\(.*?\)', '', name)
    # Remove punctuation
    name = re.sub(r'[^\w\s]', '', name)
    # Normalize spaces
    name = re.sub(r'\s+', ' ', name)
    if name in ALIASES:
        # If the name is an alias, replace it with the full name
        name = ALIASES[name]
    return name.strip()