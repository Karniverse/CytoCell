import uuid
import json
import random
import shutil
import os
import time
import sys
import argparse
import glob

# TEMPLATE = "cytocell_template.py"
# DISH_FOLDER = "dish"
# DISH_JSON = "dish.json"

# ─── CLI ARGUMENT PARSER ─────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument("--reset", action="store_true", help="Reset the entire ecosystem and exit")
parser.add_argument("--reinitiate", action="store_true", help="Reset and start a new first cell")
args = parser.parse_args()

# ─── FILE PATHS ───────────────────────────────────────
TEMPLATE = "cytocell_template.py"
DISH_FOLDER = "dish"
DISH_JSON = "dish.json"           # Correct location: root folder
LOG_FOLDER = "logs"
CELL_LOGS_FOLDER = os.path.join(LOG_FOLDER, "cells")

# ─── FULL ECOSYSTEM RESET ─────────────────────────────
def perform_reset():
    print("🧼 Resetting CytoCell ecosystem...")

    # 1. Delete all cytocell files in dish/
    if os.path.exists(DISH_FOLDER):
        for f in glob.glob(os.path.join(DISH_FOLDER, "cytocell_*.py")):
            os.remove(f)
        for f in glob.glob(os.path.join(DISH_FOLDER, "dna_*.json")):
            os.remove(f)
        print("✅ Cleared cell files in 'dish/'.")

    # 2. Reset dish.json in root
    with open(DISH_JSON, "w") as f:
        json.dump({"resources": 10000, "max_cells": 50, "cells": {}}, f, indent=4)
    print("✅ Reset 'dish.json'.")

    # 3. Delete logs
    if os.path.exists(LOG_FOLDER):
        for file in glob.glob(os.path.join(LOG_FOLDER, "*.log")):
            os.remove(file)
        if os.path.exists(CELL_LOGS_FOLDER):
            for file in glob.glob(os.path.join(CELL_LOGS_FOLDER, "*.log")):
                os.remove(file)
        print("✅ Cleared all logs.")

    print("🌱 Ecosystem reset complete.\n")


def generate_dna(cell_id):
    return {
        "id": cell_id,
        "generation": 1,
        "lifespan": random.randint(15, 30),
        "energy": 100,
        "mutation_chance": 0.2,
        "reproduce_chance": 0.4,
        "metabolism_rate": 1,
        "traits": {
            "aggressive": random.choice([True, False]),
            "cooperative": random.choice([True, False]),
            "sleeper": random.choice([True, False])
        }
    }
    
if args.reset:
    perform_reset()
    sys.exit(0)

if args.reinitiate:
    perform_reset()
    print("🚀 Reinitiating colony...")


def create_initial_cell():
    if not os.path.exists(DISH_FOLDER):
        os.makedirs(DISH_FOLDER)

    cell_id = str(uuid.uuid4())[:8]
    dna = generate_dna(cell_id)

    # Copy the cell template as a new independent file
    cell_filename = f"cytocell_{cell_id}.py"
    dest_path = os.path.join(DISH_FOLDER, cell_filename)
    shutil.copy(TEMPLATE, dest_path)

    # Save DNA
    dna_filename = f"dna_{cell_id}.json"
    with open(os.path.join(DISH_FOLDER, dna_filename), "w") as f:
        json.dump(dna, f, indent=4)

    print(f"✅ Created initial cell: {dest_path}")

    # Optional: auto-run it after 5 sec
    def launch():
        time.sleep(5)
        subprocess.Popen(["python", cell_filename], cwd=DISH_FOLDER)

    import threading, subprocess
    threading.Thread(target=launch).start()

if __name__ == "__main__":
    create_initial_cell()
