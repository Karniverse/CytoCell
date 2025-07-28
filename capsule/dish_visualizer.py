import json
import os
import time
import tkinter as tk
from tkinter import ttk
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DISH_PATH = "dish.json"

def load_dish():
    if not os.path.exists(DISH_PATH):
        return {"cells": {}, "resources": 0, "max_cells": 0}
    with open(DISH_PATH, "r") as f:
        return json.load(f)

def get_stats():
    dish = load_dish()
    cells = dish.get("cells", {})
    resources = dish.get("resources", 0)
    max_cells = dish.get("max_cells", 0)

    lifespans = []
    energies = []
    traits_count = {"aggressive": 0, "cooperative": 0, "sleeper": 0}

    for c in cells.values():
        if "energy" in c:
            energies.append(c["energy"])
        if "traits" in c:
            for trait in traits_count:
                if c["traits"].get(trait):
                    traits_count[trait] += 1

    avg_energy = sum(energies) / len(energies) if energies else 0

    return {
        "cell_count": len(cells),
        "resources": resources,
        "max_cells": max_cells,
        "avg_energy": avg_energy,
        "traits_count": traits_count
    }

# ---------------- TERMINAL VERSION ----------------
def terminal_view():
    try:
        while True:
            stats = get_stats()
            os.system("cls" if os.name == "nt" else "clear")
            print(f"🌱 CytoCell Dish Status")
            print(f"----------------------")
            print(f"Live Cells     : {stats['cell_count']} / {stats['max_cells']}")
            print(f"Resources Left : {stats['resources']}")
            print(f"Avg Energy     : {stats['avg_energy']:.2f}")
            print("Trait Counts:")
            for trait, count in stats['traits_count'].items():
                print(f"  {trait:<12}: {count}")
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nStopped.")

# ---------------- GUI VERSION ----------------
class DishGUI:
    def __init__(self, root):
        self.root = root
        root.title("CytoCell Dish Visualizer")

        self.label = ttk.Label(root, text="Live Stats", font=("Arial", 14))
        self.label.pack(pady=10)

        self.stats_frame = ttk.Frame(root)
        self.stats_frame.pack()

        self.labels = {
            "cells": ttk.Label(self.stats_frame),
            "resources": ttk.Label(self.stats_frame),
            "avg_energy": ttk.Label(self.stats_frame),
        }
        for label in self.labels.values():
            label.pack(anchor="w")

        # Pie chart setup
        self.fig, self.ax = plt.subplots(figsize=(4, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()

        self.update_loop()
        
    def on_close(self):
        # Stop any loops, destroy window, and fully quit the app
        self.root.destroy()
        self.root.quit()
        os._exit(0)  # Force kill remaining threads

    def update_loop(self):
        stats = get_stats()
        self.labels["cells"].config(text=f"Live Cells   : {stats['cell_count']} / {stats['max_cells']}")
        self.labels["resources"].config(text=f"Resources    : {stats['resources']}")
        self.labels["avg_energy"].config(text=f"Avg Energy   : {stats['avg_energy']:.2f}")

        # Pie chart
        self.ax.clear()
        traits = stats["traits_count"]
        trait_labels = list(traits.keys())
        sizes = list(traits.values())
        if sum(sizes) > 0:
            self.ax.pie(sizes, labels=trait_labels, autopct='%1.1f%%')
        else:
            self.ax.text(0.5, 0.5, "No Traits Yet", ha="center", va="center")
        self.ax.set_title("Trait Distribution")
        self.canvas.draw()

        self.root.after(2000, self.update_loop)

# ---------------- ENTRY POINT ----------------
if __name__ == "__main__":
    gui_mode = True  # <- Force GUI mode by default
    import argparse

    parser = argparse.ArgumentParser(description="CytoCell Dish Visualizer")
    parser.add_argument("--gui", action="store_true", help="Show GUI")
    args = parser.parse_args()

    if args.gui:
        root = tk.Tk()
        app = DishGUI(root)
        root.mainloop()
    elif gui_mode:
        root = tk.Tk()
        app = DishGUI(root)
        root.mainloop()
    else:
        terminal_view()
