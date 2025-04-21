import os
import json
import dotenv
import winsound
from time import sleep
from core.geo_agent import GeoAgent
from ui.calibrator import Calibrator
from langchain_openai import ChatOpenAI as OpenAI
from pynput.keyboard import Key, KeyCode, Listener
from langchain_anthropic import ChatAnthropic as Anthropic
from langchain_google_genai import ChatGoogleGenerativeAI as Gemini
from config import ROUNDS_NUMBER, START_GAME_KEY, KEYPOINTS_FILE, PRE_ROUND_DELAY, POST_CALIBRATION_DELAY

def calibrate_keypoints():
    print("Open the browser window.")
    sleep(POST_CALIBRATION_DELAY)
    winsound.Beep(1000, 500)
    calibrator = Calibrator()
    keypoints = calibrator.calibrate_keypoints()
    print("Key points calibration completed.")
    return keypoints

def run_agent_when_ready(keypoints: dict):
    print(f"Press key '{START_GAME_KEY}' to start the agent.")
    with Listener(on_press=lambda key: run_agent(key, keypoints)) as listener:
        listener.join()

def run_agent(key: Key | KeyCode | None, keypoints: dict):
    if getattr(key, 'char', None) != START_GAME_KEY:
        return

    print(f"Agent will start in {POST_CALIBRATION_DELAY} seconds.")
    sleep(POST_CALIBRATION_DELAY)
    winsound.Beep(1000, 500)
    print("Agent started.")

    agent = GeoAgent(keypoints, LLM_type=Gemini, LLM_name="gemini-2.0-flash")

    for round in range(ROUNDS_NUMBER):
        print(f"\n ~ ~ ~ Round {round+1}/{ROUNDS_NUMBER} ~ ~ ~")
        sleep(PRE_ROUND_DELAY)
        agent.play_round()
    
    return False

def main():
    keypoints = dict()

    if not os.path.exists(KEYPOINTS_FILE):
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
    
    run_agent_when_ready(keypoints)

if __name__ == "__main__":
    dotenv.load_dotenv()
    main()