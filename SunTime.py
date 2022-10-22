import os
from math import sin, cos, tan, asin, acos, atan, pi, floor
from datetime import date as dt
from datetime import datetime, timedelta
import time

import requests

headers = {
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,be;q=0.6',
    'Connection': 'keep-alive',
    'Origin': 'https://ip-api.com',
    'Referer': 'https://ip-api.com/',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

geo = requests.get('https://demo.ip-api.com/json/', headers=headers).json()
latitude, longitude = geo['lat'], geo['lon']

localOffset = -time.timezone / 3600
pii = pi / 180
zenith = cos((90 + 5 / 6) * pii)


def t_s(tt):
    tt = str(tt)
    r = int(tt[:2]) * 60 * 60
    r += int(tt[3:5]) * 60
    r += float(tt[6:])
    return r


def clr():
    os.system('cls' if 'nt' == os.name else 'clear')


def linker():
    t1 = time_of_rise_set(False)
    t3 = time_of_rise_set(True)
    t = time_of_rise_set(False, True)
    t2 = (t3 - t1) / 2 + t1
    t4 = ((t - t3) / 2 + t3 + 12 * 3600)
    if t4 > 24 * 3600:
        sp = [t4 - 24 * 3600,  # 0
              t1,  # 6
              t2,  # 12
              t3,  # 18
              t4]  # 24
    else:  # для городов по типу Биак
        sp = [t4,  # 0
              t1,  # 6
              t2,  # 12
              t3,  # 18
              t4 + 24 * 3600]  # 24

    return sp


def How_Many_t(t):
    sp = linker()

    if sp[0] < t < sp[1]:  # 0-6
        return (sp[1] - sp[0]) / (6 * 3600), 1, sp

    elif sp[1] < t < sp[2]:  # 6-12
        return (sp[2] - sp[1]) / (6 * 3600), 2, sp

    elif sp[2] < t < sp[3]:  # 12-18
        return (sp[3] - sp[2]) / (6 * 3600), 3, sp

    elif sp[3] < t < sp[4]:  # 18-24
        return (sp[4] - sp[3]) / (6 * 3600), 4, sp

    elif sp[3] < t + 24 * 3600 < sp[4]:  # если не дошел до надира
        return (sp[4] - sp[3]) / (6 * 3600), 4, sp


def time_of_rise_set(night: bool = 0, tomorrow: bool = 0):
    if not tomorrow:
        date = datetime.now()
    else:
        today = dt.today()
        date = today + timedelta(days=1)

    day, month, year = date.day, date.month, date.year

    # алгоритм/algorithm
    # https://web.archive.org/web/20161229042556/http://williams.best.vwh.net/sunrise_sunset_example.htm

    # 1
    N1 = floor(275 * month / 9)
    N2 = floor((month + 9) / 12)
    N3 = (1 + floor((year - 4 * floor(year / 4) + 2) / 3))
    N = N1 - (N2 * N3) + day - 30

    # 2
    lngHour = longitude / 15
    if not night:
        t = N + ((6 - lngHour) / 24)
    else:
        t = N + ((18 - lngHour) / 24)

    # 3
    M = (0.9856 * t) - 3.289

    # 4
    L = M + (1.916 * sin(M * pii)) + (0.020 * sin(2 * M * pii)) + 282.634
    if L >= 360 and not night:
        L -= 360
    elif L < 0 and not night:
        L += 360

    # 5a
    RA = atan(0.91764 * tan(L * pii)) / pii

    # 5b
    Lquadrant = (floor(L / 90)) * 90
    RAquadrant = (floor(RA / 90)) * 90
    RA = RA + (Lquadrant - RAquadrant)

    # 5c
    RA = RA / 15

    # 6
    sinDec = 0.39782 * sin(L * pii)
    cosDec = cos(asin(sinDec))

    # 7a
    cosH = (zenith - (sinDec * sin(latitude * pii))) / (cosDec * cos(latitude * pii))

    if cosH < -1:
        print('сегодня полярный день')
        exit()
    elif cosH > 1:
        print('сегодня полярная ночь')
        exit()

    # 7b
    if not night:
        H = 360 - acos(cosH) / pii
    else:
        H = acos(cosH) / pii

    H = H / 15

    # 8
    T = H + RA - (0.06571 * t) - 6.622

    # 9
    UT = T - lngHour

    # 10
    localT = UT + localOffset

    return localT * 3600


raz = 1
real_t = t_s(datetime.now().time())
speed, place, sp_t = How_Many_t(real_t)

last = 1
while 1:

    sun_t = (t_s(datetime.now().time()) - sp_t[place - 1]) / speed + 21600 * (place - 1)
    if int(sun_t) != last:
        clr()
        print('\r'+ datetime.utcfromtimestamp(sun_t).strftime('%H:%M:%S'), end='')
        last = int(sun_t)

    now = t_s(datetime.now().time())
    if now + 24 * 60 * 60 >= sp_t[4] and place == 4:
        print(1, end=' ')
        speed, place, sp_t = How_Many_t(t_s(datetime.now().time()))
    elif now >= sp_t[place]:
        print(2, end=' ')
        speed = (sp_t[place + 1] - sp_t[place]) / 21600
        place += 1
