import os
import json
import dotenv
import winsound
from config import *
from time import sleep
from LLM.models import *
from core.geo_agent import GeoAgent
from ui.calibrator import Calibrator
from typing import List, Tuple, Optional
from pynput.keyboard import Key, KeyCode, Listener

def calibrate_keypoints():
    print("Open the browser window.")
    sleep(POST_CALIBRATION_DELAY)
    winsound.Beep(1000, 500)
    calibrator = Calibrator()
    keypoints = calibrator.calibrate_keypoints()
    print("Key points calibration completed.")
    return keypoints

def run_agent_when_ready(keypoints: dict, models: List[Tuple[OpenAI | Gemini | Anthropic, str]]):
    print(f"Press key '{START_GAME_KEY}' to start the agent.")
    with Listener(on_press=lambda key: run_agent(key, keypoints, models)) as listener:
        listener.join()

def run_agent(key: Optional[Key | KeyCode], keypoints: dict, models: List[Tuple[OpenAI | Gemini | Anthropic, str]]):
    if getattr(key, 'char', None) != START_GAME_KEY:
        return

    print(f"Agent will start in {POST_CALIBRATION_DELAY} seconds.")
    sleep(POST_CALIBRATION_DELAY)
    winsound.Beep(1000, 500)
    print("Agent started.")

    agent = GeoAgent(keypoints, LLMs=models)

    for round in range(ROUNDS_NUMBER):
        print(f"\n ~ ~ ~ Round {round+1}/{ROUNDS_NUMBER} ~ ~ ~")
        sleep(PRE_ROUND_DELAY)
        agent.play_round()
    
    return False

def select_llm_strategy() -> List[Tuple[OpenAI | Gemini | Anthropic, str]]:
    print("\nAvailable LLM models:")
    print(f"1 — Gemini: {GEMINI_MODEL_NAME}")
    print(f"2 — OpenAI: {OPENAI_MODEL_NAME}")
    print(f"3 — Chat Anthropic: {ANTHROPIC_MODEL_NAME}")
    print("Select one or more models by entering their numbers (separated by spaces or commas):", end=' ')
    user_input = input().strip()

    model_mapping = {
        '1': (Gemini, GEMINI_MODEL_NAME),
        '2': (OpenAI, OPENAI_MODEL_NAME),
        '3': (Anthropic, ANTHROPIC_MODEL_NAME)
    }

    separators = [',', ' ']
    for sep in separators:
        if sep in user_input:
            choices = [item.strip() for item in user_input.split(sep)]
            break
    else:
        choices = [user_input.strip()]

    selected_models = []
    for choice in choices:
        if choice in model_mapping:
            selected_models.append(model_mapping[choice])
        else:
            print(f"Invalid model number '{choice}'. Exiting.")
            exit()

    if not selected_models:
        print("No valid models selected. Exiting.")
        exit()

    return selected_models

def main():
    keypoints = dict()

    if not (os.path.exists(KEYPOINTS_FILE) and os.path.exists(CALIBRATION_MAP_FILE)):
        keypoints = calibrate_keypoints()
    else:
        print("Do you need to calibrate key points? (y/n):", end=' ')
        user_input = input().strip().lower()
        if user_input == 'y':
            keypoints = calibrate_keypoints()
        elif user_input == 'n':
            with open(KEYPOINTS_FILE) as file:
                keypoints = json.load(file)
            print("Key points calibration skipped.")
        else:
            print("Invalid input. Exiting.")
            return
    
    selected_models = select_llm_strategy()
    run_agent_when_ready(keypoints, selected_models)

if __name__ == "__main__":
    dotenv.load_dotenv()
    main()