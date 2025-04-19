import os
import json
import dotenv
import winsound
from time import sleep
from core.geo_agent import GeoAgent
from ui.calibrator import Calibrator
from langchain_openai import ChatOpenAI as OpenAI
from langchain_anthropic import ChatAnthropic as Claude
from langchain_google_genai import GoogleGenerativeAI as Gemini
from config import ROUNDS_NUMBER, KEYPOINTS_FILE_PATH, PRE_ROUND_DELAY_IN_SECONDS, POST_CALIBRATION_DELAY_IN_SECONDS

def calibrate_user_keypoints():
    print("Open the browser window.")
    sleep(2)
    winsound.Beep(1000, 500)
    calibrator = Calibrator()
    keypoints = calibrator.calibrate_user_keypoints()
    print("Key points calibration completed.")
    return keypoints

def main():
    keypoints = dict()

    if not os.path.exists(KEYPOINTS_FILE_PATH):
        keypoints = calibrate_user_keypoints()
    else:
        print("Do you need to calibrate key points? (y/n):", end=' ')
        user_input = input().strip().lower()
        if user_input == 'y':
            keypoints = calibrate_user_keypoints()
        elif user_input == 'n':
            with open(KEYPOINTS_FILE_PATH) as file:
                keypoints = json.load(file)
            print("Key points calibration skipped.")
        else:
            print("Invalid input. Exiting.")
            return
    
    print(f"Agent will start in {POST_CALIBRATION_DELAY_IN_SECONDS} seconds.")
    sleep(POST_CALIBRATION_DELAY_IN_SECONDS)

    agent = GeoAgent(keypoints, LLM_type=OpenAI, LLM_name="gpt-4o")

    for round in range(ROUNDS_NUMBER):
        print(f"\n ~ ~ ~ Round {round+1}/{ROUNDS_NUMBER} ~ ~ ~")
        sleep(PRE_ROUND_DELAY_IN_SECONDS)
        agent.play_round()

if __name__ == "__main__":
    dotenv.load_dotenv()
    main()