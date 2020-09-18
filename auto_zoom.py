from datetime import datetime
import subprocess
import webbrowser
import threading
import time
import math
import json
from win10toast import ToastNotifier

HOUR_IN_SECONDS = 3600
now = datetime.now()
lessons = []


class LessonTime:
    def __init__(self, hour, minute, second, weekday):
        self.hour = hour
        self.minute = minute
        self.second = second
        self.weekday = weekday


class Lesson:
    def __init__(self, name, time: LessonTime, zoom_link, password):
        self.name = name
        self.time = time
        self.zoom_link = zoom_link
        self.password = password


def init_lessons():
    with open('lessons.json') as json_file:
        data = json.load(json_file)
        for lesson in data['lessons']:
            name = lesson['name']
            time = lesson['time'].split(',')
            zoom_link = lesson['zoom_link']
            password = lesson['password']
            lessons.append(Lesson(name, LessonTime(
                time[0], time[1], 0, time[2]), zoom_link, password))


def parseSecs(lessonTime: LessonTime):
    return (lessonTime.hour*3600)+(lessonTime.minute*60)+int(lessonTime.second)


def parseTime(secs: int):
    hh = int(secs/3600)
    mm = int((secs - hh*3600)/60)
    ss = secs - hh*3600 - mm*60
    return datetime(2020, 9, 18, hh, mm, ss)


def is_lesson_start(lesson: Lesson, now: LessonTime, lose: int):
    is_start = False
    lessonSecs = parseSecs(lesson.time)
    nowSecs = parseSecs(now)
    if nowSecs > lessonSecs-lose and nowSecs < lessonSecs+lose:
        if lesson.time.weekday == now.weekday:
            is_start = True
    return is_start


def countdown_next_check(interval: int, now: LessonTime):
    current_time = parseSecs(now)
    next_checking_time = interval * (math.ceil(current_time / interval))
    diff = next_checking_time - current_time
    print(f"Next check will be at {parseTime(next_checking_time)}")
    print(f"{diff} seconds until next check")
    time.sleep(diff)
    # for s in range(diff):
    #     print(f"{diff-s} seconds left")
    #     time.sleep(1)


terminate = False


def check(interval: int):
    now = datetime.now()
    now = LessonTime(now.hour, now.minute, now.second, now.weekday())
    print("checking")
    for lesson in lessons:
        if is_lesson_start(lesson, now, interval):
            subprocess.call(
                ["C:/Users/85256/AppData/Roaming/Zoom/bin/Zoom.exe"])
            webbrowser.open(lesson.zoom_link)
            notifier = ToastNotifier()
            notifier.show_toast(
                "Auto Zoom", f"lesson: {lesson.name}, password: {lesson.password}", duration=10)
            break
    countdown_next_check(interval, now)
    if terminate == False:
        check(interval)


print("initializing lessons.")
init_lessons()
print(f"{len(lessons)} lessons loaded.")
thread = threading.Thread(target=check, args=[900, ])
thread.start()
input("enter anything to exit\n")
terminate = True
print("Done.")
