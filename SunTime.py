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
# latitude, longitude = -1.0842112,135.2012817 # о. Биак / Biak island

localOffset = -time.timezone / 3600
# localOffset = 9
pii = pi / 180
zenith = cos((90 + 5 / 6) * pii)


def t_now():  # сколько сейчас времени в секундах / how many time in seconds
    tt = datetime.now().time()
    r = tt.hour * 60 * 60
    r += tt.minute * 60
    r += tt.second
    r += tt.microsecond / 10e5
    return r


def linker():
    tr = time_of_rise_set(False)
    ts = time_of_rise_set(True)
    tr_t = time_of_rise_set(False, tomorrow=True)
    ts_y = time_of_rise_set(True, yesterday=True)
    tz = (ts - tr) / 2 + tr
    tn = ((tr_t - ts) / 2 + ts + 12 * 3600)
    tn_y = ((tr - ts_y) / 2 + ts_y + 12 * 3600)

    return [tn_y - 24 * 3600,  # 0
            tr,  # 6
            tz,  # 12
            ts,  # 18
            tn  # 24
            ]


def How_Many_t(t: int):
    sp = linker()

    if sp[0] < t < sp[1]:  # 0-6
        return (sp[1] - sp[0]) / (6 * 3600), 1, sp

    elif sp[1] < t < sp[2]:  # 6-12
        return (sp[2] - sp[1]) / (6 * 3600), 2, sp

    elif sp[2] < t < sp[3]:  # 12-18
        return (sp[3] - sp[2]) / (6 * 3600), 3, sp

    elif sp[3] < t < sp[4]:  # 18-24
        return (sp[4] - sp[3]) / (6 * 3600), 4, sp

    elif sp[3] < t + 24 * 3600 < sp[4]:  # если t между надиром 12ч ночи/ if "t" between nadir ahd 12 midnight
        return (sp[4] - sp[3]) / (6 * 3600), 4, sp


def time_of_rise_set(night: bool = 0, tomorrow: bool = 0, yesterday: bool = 0):
    if tomorrow:
        today = dt.today()
        date = today + timedelta(days=1)
    elif yesterday:
        today = dt.today()
        date = today + timedelta(days=-1)
    else:
        date = datetime.now()

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

    if cosH < -1: # TODO: реализовать полярный день и ночь
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
real_t = t_now()
speed, place, sp_t = How_Many_t(real_t)

last = 1
while 1:

    sun_t = (t_now() - sp_t[place - 1]) / speed + 21600 * (place - 1)
    if int(sun_t) != last:
        print('\r' + datetime.utcfromtimestamp(sun_t).strftime('%H:%M:%S'), end='')
        last = int(sun_t)

    now = t_now()
    if now < 6 * 3600:
        now += 24 * 3600

    if now >= sp_t[4] and place == 4:
        speed, place, sp_t = How_Many_t(t_now())
    elif now >= sp_t[place]:
        speed = (sp_t[place + 1] - sp_t[place]) / (6 * 3600)
        place += 1
