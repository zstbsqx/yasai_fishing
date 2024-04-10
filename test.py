import time
from pathlib import Path

import cv2 as cv
import numpy
from PIL import Image, ImageDraw
import pyautogui


def print_cursor_cv(haystack_image: str):
    name = Path(haystack_image).stem
    print(haystack_image)
    full_img = cv.imread(haystack_image)
    bar_img = cv.imread("data/fishing_bar_left.png")
    methods = [
        cv.TM_SQDIFF,
        cv.TM_SQDIFF_NORMED,
        cv.TM_CCORR_NORMED,
        cv.TM_CCOEFF,
        cv.TM_CCOEFF_NORMED,
    ]
    for i, method in enumerate(methods):
        img = full_img.copy()
        res = cv.matchTemplate(img, bar_img, method)
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(res)
        print(i, min_val, max_val, min_loc, max_loc)
 
        # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
        if method in [cv.TM_SQDIFF, cv.TM_SQDIFF_NORMED]:
            top_left = min_loc
        else:
            top_left = max_loc
        bottom_right = (top_left[0] + 30, top_left[1] + 138)
        cv.rectangle(img, top_left, bottom_right, 255, 2)
        cv.imwrite(f'{name}-{i}.png', img)

def print_cursor(haystack_image: str):
    name = Path(haystack_image).stem
    fishing_bar_box = pyautogui.locate("data/fishing_bar_left.png", haystack_image, confidence=0.8)
    try:
        cursor_box = pyautogui.locate("data/fishing_bar_cursor.png", haystack_image, confidence=0.95)
    except pyautogui.ImageNotFoundException:
        print("Not found. Top or bottom")
        return

    with Image.open(haystack_image) as img:
        draw = ImageDraw.Draw(img)
        draw.rectangle([fishing_bar_box.left, fishing_bar_box.top, fishing_bar_box.left + 30, fishing_bar_box.top + 138], outline=(255, 0, 0))
        draw.rectangle([cursor_box.left, cursor_box.top, cursor_box.left + 30, cursor_box.top + 2], outline=(0, 0, 255))
        img.save(f'{name}.png')

def test1():
    print_cursor("data/top.png")
    print_cursor("data/bottom.png")
    print_cursor("data/need_up.png")
    print_cursor("data/need_down.png")


def test():
    holding_up = False
    holding_down = False
    bar_img = cv.imread("data/fishing_bar_left.png")
    cursor_img = cv.imread("data/fishing_bar_cursor.png")

    last_cursor_y = None
    fish_direction  = None

    while True:
        screen = cv.cvtColor(numpy.array(pyautogui.screenshot()), cv.COLOR_RGB2BGR)
        bar_res = cv.matchTemplate(screen, bar_img, cv.TM_CCOEFF_NORMED)
        bar_min_val, bar_max_val, bar_min_loc, bar_max_loc = cv.minMaxLoc(bar_res)
        if bar_max_val < 0.9:
            if fish_direction:
                print("Fish!")
            # Not fishing
            if holding_up:
                print("Release UP")
                pyautogui.keyUp("up")
                holding_up = False
            if holding_down:
                print("Release DOWN")
                pyautogui.keyUp("down")
                holding_down = False
            last_cursor_y = None
            fish_direction = None
            continue
        cursor_res = cv.matchTemplate(screen, cursor_img, cv.TM_CCOEFF_NORMED)
        cursor_min_val, cursor_max_val, cursor_min_loc, cursor_max_loc = cv.minMaxLoc(cursor_res)
        if cursor_max_val < 0.999:
            continue
        # print(cursor_min_val, cursor_max_val, cursor_min_loc, cursor_max_loc)
        bar_top_y = bar_max_loc[1]
        cursor_y = cursor_max_loc[1]
        bar_bottom_y = bar_top_y + 138
        print(bar_top_y, cursor_y, bar_bottom_y)

        if fish_direction is None and last_cursor_y is not None:
            if cursor_y == last_cursor_y:
                continue
            fish_direction = "up" if last_cursor_y > cursor_y else "down"
            print(f"{fish_direction=}")
        last_cursor_y = cursor_y
        if cursor_y > bar_bottom_y or cursor_y < bar_top_y:
            raise ValueError("Invalid cursor Y")
        if fish_direction == "down":
            assert not holding_down
            if cursor_y < bar_top_y + 69:
                if holding_up:
                    print("Release UP")
                    pyautogui.keyUp("up")
                    holding_up = False
            else:
                if not holding_up:
                    print("Press UP")
                    pyautogui.keyDown("up")
                    holding_up = True
        elif fish_direction == "up":
            assert not holding_up
            if cursor_y < bar_top_y + 69:
                if not holding_down:
                    print("Press DOWN")
                    pyautogui.keyDown("down")
                    holding_down = True
            else:
                if holding_down:
                    print("Release DOWN")
                    pyautogui.keyUp("down")
                    holding_down = False


test()
