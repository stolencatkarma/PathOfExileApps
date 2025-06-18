import os
import json
import random

# This path assumes the .dat files are in a dedicated directory outside the app.
# It should be configured based on where the user's data is.
DATA_DIR = "C:\\PathofExileData"

def load_dat_file(file_name):
    file_path = os.path.join(DATA_DIR, file_name)
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError:
                        data.append(line)
    except FileNotFoundError:
        print(f"Error: .dat file not found at {file_path}")
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
    return data

def combine_build_elements(major_elements, minor_elements):
    if len(major_elements) < 2 or len(minor_elements) < 1:
        print("Not enough elements to combine (need 2 major, 1 minor).")
        return "Invalid Combination"

    selected_major = random.sample(major_elements, 2)
    selected_minor = random.sample(minor_elements, 1)

    print(f"Combining: Major 1: {selected_major[0]}, Major 2: {selected_major[1]}, Minor: {selected_minor[0]}")
    return f"New Archetype: {selected_major[0]}-{selected_major[1]} with {selected_minor[0]} focus."

def run():
    print("Build Archetype Combiner plugin activated.")

    # Placeholder for actual game data loading from .dat files
    # In a real scenario, you would categorize data from .dat files
    # into 'major' and 'minor' elements based on game mechanics.
    
    # Example dummy data:
    major_build_aspects = [
        "Spell Casting (Fire)", "Melee Physical (Axes)", 
        "Minion Master (Zombies)", "Bow Attacks (Projectile)",
        "Totem Play (Spell Totems)", "Trap/Mine Laying"
    ]
    minor_build_aspects = [
        "Crit Focus", "Block Chance", "Energy Shield", 
        "Life Leech", "Evasion", "Armour", "Chaos Damage"
    ]

    new_archetype = combine_build_elements(major_build_aspects, minor_build_aspects)
    print(new_archetype)
