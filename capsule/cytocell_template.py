import os
import time
import json
import random
import uuid
import shutil
import subprocess
import threading

from filelock import FileLock

LOCK_FILE = "../dish.json.lock"  # lock lives alongside dish.json



DISH_FILE = "../dish.json"  # Relative to dish/ folder
LOG_FOLDER = "../logs"      # Relative log path
CELL_FOLDER = "."           # Current cell directory (dish/)

# === LOAD DNA ===
def load_dna():
    filename = os.path.basename(__file__)
    cell_id = filename.split("_")[1].split(".")[0]
    with open(f"dna_{cell_id}.json", "r") as f:
        return json.load(f)

DNA = load_dna()

def log(msg):
    timestamp = f"{time.time():.6f}"
    message = f"[{DNA['id']}] {timestamp} - {msg}"
    
    print(message)

    # Ensure log folders exist
    os.makedirs(LOG_FOLDER, exist_ok=True)
    os.makedirs(os.path.join(LOG_FOLDER, "cells"), exist_ok=True)

    # Global dish log
    with open(os.path.join(LOG_FOLDER, "dish.log"), "a") as f:
        f.write(message + "\n")

    # Per-cell log
    with open(os.path.join(LOG_FOLDER, "cells", f"{DNA['id']}.log"), "a") as f:
        f.write(message + "\n")

def load_dish():
    with FileLock(LOCK_FILE):
        with open(DISH_FILE, "r") as f:
            return json.load(f)

def write_dish(dish):
    with FileLock(LOCK_FILE):
        with open(DISH_FILE, "w") as f:
            json.dump(dish, f, indent=4)

def register_cell():
    dish = load_dish()
    dish["cells"][DNA["id"]] = {
        "generation": DNA["generation"],
        "energy": DNA["energy"],
        "traits": DNA["traits"]
    }
    write_dish(dish)

def deregister_cell():
    dish = load_dish()
    dish["cells"].pop(DNA["id"], None)
    write_dish(dish)

def metabolize():
    dish = load_dish()
    if dish["resources"] > 0:
        DNA["energy"] -= DNA["metabolism_rate"]
        dish["resources"] -= 1
        write_dish(dish)
        log(f"Metabolized. Energy: {DNA['energy']}")

def replicate():
    dish = load_dish()
    if len(dish["cells"]) >= dish["max_cells"]:
        log("Replication skipped: max population reached.")
        return

    if random.random() < DNA["reproduce_chance"]:
        DNA["energy"] -= 10  # Energy cost
        if DNA["energy"] <= 0:
            log("Too weak to replicate.")
            return

        child_id = str(uuid.uuid4())[:8]
        child_dna = DNA.copy()
        child_dna["id"] = child_id
        child_dna["generation"] += 1

        if random.random() < child_dna["mutation_chance"]:
            child_dna["lifespan"] = max(5, random.randint(10, 30))
            child_dna["reproduce_chance"] = min(1.0, max(0.1, DNA["reproduce_chance"] + random.uniform(-0.1, 0.1)))

        filename = f"cytocell_{child_id}.py"
        filepath = os.path.join(CELL_FOLDER, filename)
        dnafile = os.path.join(CELL_FOLDER, f"dna_{child_id}.json")

        shutil.copy(__file__, filepath)
        with open(dnafile, "w") as f:
            json.dump(child_dna, f, indent=4)

        log(f"Replicated! New cell: {filename}")

        # Wait and execute the new cell
        def launch():
            time.sleep(5)
            subprocess.Popen(["python", filepath], cwd=CELL_FOLDER)

        threading.Thread(target=launch).start()

def die():
    log("Dying.")
    deregister_cell()
    try:
        os.remove(__file__)
        os.remove(f"dna_{DNA['id']}.json")
    except Exception as e:
        log(f"Error deleting self: {e}")

def run_lifecycle():
    log(f"Born. Gen {DNA['generation']} Life: {DNA['lifespan']}s Traits: {DNA['traits']}")
    register_cell()
    age = 0
    try:
        while age < DNA["lifespan"] and DNA["energy"] > 0:
            metabolize()
            replicate()

            if DNA["traits"].get("sleeper", False):
                sleep_time = random.uniform(1, 3)
            else:
                sleep_time = 1

            time.sleep(sleep_time)
            age += 1
    except Exception as e:
        log(f"Runtime error: {e}")
    die()

if __name__ == "__main__":
    run_lifecycle()
