import os
import json
import winsound
from LLM import *
import tkinter as tk
from typing import List
from dotenv import load_dotenv
from tkinter import messagebox
from core.geo_agent import GeoAgent
from ui.calibration.calibrator import Calibrator
from ui.user.models_dialog import ModelSelectorDialog
from config import KEYPOINTS_FILE, CALIBRATION_MAP_FILE

def calibrate_keypoints(root: tk.Tk):
    messagebox.showinfo("Calibration", "Open the browser window and press 'OK'")
    winsound.Beep(1000, 500)
    calibrator = Calibrator(root)
    keypoints = calibrator.calibrate_keypoints()
    messagebox.showinfo("Calibration Complete", "Key point calibration finished.")
    return keypoints

def run_agent_when_ready(keypoints: dict, models: List[LlmWrapper]):
    messagebox.showinfo("Ready", "Press 'OK' to start the agent.")
    agent = GeoAgent(keypoints, models)
    agent.run()

def select_llm_strategy(root: tk.Tk) -> List[LlmWrapper]:
    dialog = ModelSelectorDialog(root, title="Select LLMs")
    return dialog.selected_models

def main():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    if not (os.path.exists(KEYPOINTS_FILE) and os.path.exists(CALIBRATION_MAP_FILE)):
        keypoints = calibrate_keypoints(root)
    else:
        should_calibrate = messagebox.askyesno("Calibration", "Do you want to recalibrate key points?")
        if should_calibrate:
            keypoints = calibrate_keypoints(root)
        else:
            with open(KEYPOINTS_FILE) as f:
                keypoints = json.load(f)

    selected_llms = select_llm_strategy(root)
    run_agent_when_ready(keypoints, selected_llms)

if __name__ == "__main__":
    load_dotenv()
    main()