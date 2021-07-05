# Try using PyAutoGUI to get the HTML from pages that are blocked by crawlers

import pyautogui

pyautogui.PAUSE = 3.0

import time

time.sleep(5)
pyautogui.keyDown('command')
time.sleep(3)

pyautogui.press('space')
time.sleep(3)

pyautogui.keyUp('command')
time.sleep(3)

pyautogui.typewrite('Chrome\n')

pyautogui.hotkey('command', 'n')


pyautogui.typewrite('https://www.jstor.org/stable/2480681?seq=1\n')


pyautogui.hotkey('command', 's')

pyautogui.typewrite('2480681.html\n')

html = open("2480681.html","w").read()


