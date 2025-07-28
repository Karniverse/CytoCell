# cytocell.py
import os
import random
import time
import uuid
import json
from datetime import datetime

# === GENETIC CODE ===
DNA = {
    "id": str(uuid.uuid4()),
    "generation": 1,
    "lifespan": random.randint(5, 15),  # seconds
    "mutation_chance": 0.2,
    "reproduce_chance": 0.5,
    "reproduction_type": "asexual"  # "sexual" could be added later
}

# === CELL STRUCTURE ===
cell = {
    "age": 0,
    "energy": 100,
    "functions": ["metabolize", "replicate", "die"]
}

def metabolize():
    cell["energy"] -= 1
    print(f"[{DNA['id']}] metabolizing... Energy: {cell['energy']}")

def replicate():
    if random.random() < DNA["reproduce_chance"]:
        child_DNA = DNA.copy()
        child_DNA["id"] = str(uuid.uuid4())
        child_DNA["generation"] += 1
        # Mutate lifespan
        if random.random() < DNA["mutation_chance"]:
            child_DNA["lifespan"] = random.randint(5, 15)

        child_filename = f"cytocell_{child_DNA['id'][:8]}.py"
        with open(child_filename, "w") as f:
            f.write(f"# Generated on {datetime.now()}\n")
            f.write("import os\nimport time\nimport random\nimport uuid\n")
            f.write("print('New digital cell born.')\n")
            f.write(f"DNA = {json.dumps(child_DNA, indent=4)}\n")
            f.write("print('DNA:', DNA)\n")
            f.write("time.sleep(1)\n")
            f.write("os.remove(__file__)  # Cell dies after 1 second\n")

        print(f"[{DNA['id']}] Replicated: created {child_filename}")

def die():
    print(f"[{DNA['id']}] Cell dying...")
    os.remove(__file__)

# === MAIN LOOP ===
print(f"[{DNA['id']}] Cell born. Gen {DNA['generation']} Lifespan: {DNA['lifespan']}s")
start_time = time.time()

try:
    while cell["age"] < DNA["lifespan"]:
        metabolize()
        if cell["energy"] <= 0:
            break
        replicate()
        time.sleep(1)
        cell["age"] += 1
except Exception as e:
    print("Error:", e)

die()
