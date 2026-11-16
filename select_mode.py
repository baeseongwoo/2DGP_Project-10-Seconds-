import os

from sdl2 import SDL_KEYDOWN, SDLK_DOWN, SDLK_ESCAPE, SDLK_LEFT, SDLK_RETURN, SDLK_RIGHT, SDLK_SPACE, SDLK_UP

import assets
import game_framework
import play_mode
import title_mode
import ui

NAMES = ['과거의 내가 문을 연다', '멈출 곳을 정한다', '3초 안에 달린다', '문이 번갈아 열린다', '둘이 함께 누른다',
         '유령이 길을 이어 준다', '떠 있는 발판에 오른다', '나를 딛고 오른다', '과거를 지켜야 한다', '탈출정에 오른다']
COLS = 5
CELL_W, CELL_H = 216, 170

best = {}       # 스테이지 번호: 가장 많이 받은 별
cursor = 0


def path(number):
    return f'stages/stage{number:02d}.json'


def ready(number):
    return os.path.exists(path(number))


def record(number, stars):
    best[number] = max(best.get(number, 0), stars)


def next_stage(number):
    for n in range(number + 1, len(NAMES) + 1):
        if ready(n):
            return n
    return None


def start(number):
    play_mode.stage_path = path(number)
    game_framework.fade_to(play_mode)


def init():
    pass


def finish():
    pass


def pause():
    pass


def resume():
    pass


def handle_events(events):
    global cursor
    for e in events:
        if e.type != SDL_KEYDOWN:
            continue
        if e.key == SDLK_ESCAPE:
            game_framework.fade_to(title_mode)
        elif e.key == SDLK_LEFT:
            cursor = (cursor - 1) % len(NAMES)
        elif e.key == SDLK_RIGHT:
            cursor = (cursor + 1) % len(NAMES)
        elif e.key in (SDLK_UP, SDLK_DOWN):
            cursor = (cursor + COLS) % len(NAMES)
        elif e.key in (SDLK_SPACE, SDLK_RETURN) and ready(cursor + 1):
            start(cursor + 1)


def update():
    pass


def draw():
    assets.image('background.png').draw(640, 360)
    ui.box(0, 0, 1279, 719, ui.INK, 120)
    ui.text('스테이지 선택', 640, 640, 36, ui.WHITE, align='center')
    total = sum(best.values())
    ui.text(f'★ {total} / {len(NAMES) * 3}', 1240, 640, 20, ui.GOLD, align='right')
    x0 = 640 - (COLS * CELL_W + (COLS - 1) * 16) / 2
    for k, name in enumerate(NAMES):
        n = k + 1
        col, row = k % COLS, k // COLS
        l = x0 + col * (CELL_W + 16)
        t = 560 - row * (CELL_H + 24)
        on = ready(n)
        ui.box(l, t - CELL_H, l + CELL_W, t, (26, 34, 47) if on else (18, 22, 30), 235)
        ui.frame(l, t - CELL_H, l + CELL_W, t, ui.CYAN if k == cursor else (52, 64, 82), 3 if k == cursor else 1)
        ui.text(str(n), l + 16, t - 30, 32, ui.WHITE if on else ui.GREY)
        ui.text(name, l + 16, t - 78, 15, ui.WHITE if on else ui.GREY)
        if on:
            stars = best.get(n, 0)
            ui.text('★' * stars + '☆' * (3 - stars), l + 16, t - 130, 26, ui.GOLD)
        else:
            ui.text('준비 중', l + 16, t - 130, 16, ui.GREY)
    ui.text('← → ↑ ↓ 고르기    Space 시작    Esc 타이틀', 640, 70, 16, ui.GREY, align='center')
