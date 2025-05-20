import pyautogui
from time import sleep
from config import ROUND_DELAY

def move_to_position(x: int, y: int) -> None:
    pyautogui.moveTo(x, y, duration=0.5)
    sleep(1)

def click_on_position(x: int, y: int) -> None:
    pyautogui.click(x, y, duration=0.5)
    sleep(1)

def go_to_next_round() -> None:
    pyautogui.press(" ")
    sleep(ROUND_DELAY)