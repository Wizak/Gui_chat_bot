import pyautogui
import pytesseract
import time
import random
import pyperclip
import json

from keyboard import press_and_release
from fuzzywuzzy import fuzz


def check_chat_activity(control_image):
    control_pixel = pyautogui.screenshot().load()
    x, y = pyautogui.locateOnScreen(control_image[0])[:2]
    checking = [
        pyautogui.locateOnScreen(control_image[1]),
        control_pixel[int(x + 16), int(y - 25)] == (255, 255, 255)
    ]

    if all(checking):
        return True
    else:
        return False


def check_window_activity():
    if 'Telegram' in pyautogui.getActiveWindowTitle():
        return True
    else:
        return False


def message_region(etalon):
    top_message_coords = list(pyautogui.locateAllOnScreen(etalon[0]))
    bottom_message_coords = list(pyautogui.locateAllOnScreen(etalon[1]))
    control_y = list(pyautogui.locateAllOnScreen(etalon[2]))[-1][1]

    top = [t[:2] for t in top_message_coords if t[1] > control_y]
    bottom = [b[:2] for b in bottom_message_coords if b[1] > control_y]
    regions = [(t[0] + 4, t[1] + 4, b[0] - t[0] - 35, b[1] - t[1] + 2) for t, b in zip(top, bottom)]

    return regions


def message_content(coords):
    text = []

    for c in coords:
        screen_message = pyautogui.screenshot(region=c)
        text_message = pytesseract.image_to_string(screen_message, lang='ukr')
        
        if '\n' in text_message:
            text_message = text_message.splitlines()[0]
        if '\x0c' in text_message:
            text_message = text_message[:-1]
        
        text.append(text_message)

    return text


def complete_answer(post): 
    with open("data.json", "r") as read_file:
        prediction = json.load(read_file)
    get = []

    for text in post:
        for phrases in prediction:
            status = False
            complete = [prediction[phrases][phr] for phr in prediction[phrases]]
            
            for phrase in complete[0]:
                text.lower()
                ratio = fuzz.WRatio(phrase, text)
                part_ratio = fuzz.partial_ratio(phrase, text)

                if ratio >= 80 or part_ratio >= 80:
                    answ = random.choice(complete[1])
                    status = True
                    
                    get.append(answ)
                    break

            if status:
                break
    
    return get


def message_send(control_image, answer):
    def paste(text: str):    
        pyperclip.copy(text)
        press_and_release('ctrl + v')

    def type(text: str, interval=0.0):    
        buffer = pyperclip.paste()
        if not interval:
            paste(text)
        else:
            for char in text:
                paste(char)
                time.sleep(interval)
        pyperclip.copy(buffer)


    for phrase in answer:
        x, y = pyautogui.locateOnScreen(control_image)[:2]
        x, y = x + 150, y + 10

        pyautogui.click(x, y)
        type(phrase, 0.15)
        pyautogui.press('enter')


def main():
    edge_message = [
        'top_message.png',
        'bottom_message.png',
        'control_check_message.png'
    ]
    control_check = [
        'control_point_answer.png',
        'user_id.png'
    ]

    while True:
        try:
            if check_window_activity():
                if check_chat_activity(control_check):
                    coords_message = message_region(edge_message)
                    content_message = message_content(coords_message)

                    if content_message:
                        answers_message = complete_answer(content_message)
                        message_send(control_check[0], answers_message)

                    time.sleep(0.7)
        except:
            continue


if __name__ == '__main__':
    main()