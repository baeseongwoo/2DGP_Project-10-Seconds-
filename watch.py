"""남은 시간을 보여 주는 손목시계 다이얼 (PRD 7.3).

눈금 60개가 1/6초(10프레임)마다 하나씩 꺼지고, 3초 이하에서는 남은 눈금이 주황으로 바뀐다.
되감기 중에는 바늘이 거꾸로 돌며 꺼진 눈금이 다시 켜진다.
"""
import math

from pico2d import draw_circle, draw_line

import ui

CX, CY, R = 640, 682, 30
TICKS = 60
ROUND_FRAMES = 600


def point(angle, r):
    return CX + r * math.cos(angle), CY + r * math.sin(angle)


def tick_angle(k):
    # 12시에서 시계 방향으로 돈다
    return math.pi / 2 - k * 2 * math.pi / TICKS


def draw(clock, rewinding=0.0):
    """rewinding: 되감기 연출 진행도 0~1 (0이면 보통 상태)"""
    if rewinding:
        gone = round(min(clock, ROUND_FRAMES) / 10 * (1 - rewinding))
        hand = tick_angle(gone) + rewinding * 6 * math.pi   # 거꾸로 세 바퀴
    else:
        gone = min(clock, ROUND_FRAMES) // 10
        hand = tick_angle(gone)
    remaining = (ROUND_FRAMES - gone * 10 if rewinding else ROUND_FRAMES - clock) / 60
    lit = ui.ORANGE if remaining <= 3 and not rewinding else ui.WHITE

    # 시곗줄과 러그
    ui.box(CX - 62, CY - 9, CX - 30, CY + 9, (40, 50, 64))
    ui.box(CX + 30, CY - 9, CX + 62, CY + 9, (40, 50, 64))
    ui.box(CX + 31, CY - 3, CX + 37, CY + 3, ui.ORANGE)     # 용두
    draw_circle(CX, CY, R + 4, 20, 27, 38, 255, filled=True)
    draw_circle(CX, CY, R + 4, 93, 111, 136)
    for k in range(TICKS):
        a = tick_angle(k)
        big = k % 5 == 0
        x1, y1 = point(a, R - (7 if big else 4))
        x2, y2 = point(a, R)
        col = lit if k >= gone else (52, 62, 78)
        draw_line(x1, y1, x2, y2, *col)
        if big:
            draw_line(x1 + 1, y1, x2 + 1, y2, *col)
    hx, hy = point(hand, R - 9)
    for o in (-1, 0, 1):
        draw_line(CX + o, CY, hx + o, hy, *ui.CYAN)
    draw_circle(CX, CY, 2, *ui.CYAN, 255, filled=True)
    ui.text(f'{max(0.0, remaining):.1f}', CX + 72, CY + 2, 26, lit, align='left')
