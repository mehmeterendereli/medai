import time
import pyautogui
import keyboard
from typing import Dict, Any


def os_input_text(args: Dict[str, Any]) -> bool:
    text = args.get("text", "")
    pyautogui.typewrite(text, interval=0.01)
    return True


def os_keypress(args: Dict[str, Any]) -> bool:
    key = args.get("key", "enter")
    keyboard.press_and_release(key)
    return True
