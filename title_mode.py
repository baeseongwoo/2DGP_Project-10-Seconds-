from sdl2 import SDL_KEYDOWN, SDLK_ESCAPE, SDLK_RETURN, SDLK_SPACE

import assets
import game_framework
import game_world
import select_mode
import ui
from player import draw_body

t = 0


def init():
    global t
    t = 0
    game_world.ox = game_world.oy = 0


def finish():
    pass


def pause():
    pass


def resume():
    pass


def handle_events(events):
    for e in events:
        if e.type != SDL_KEYDOWN:
            continue
        if e.key == SDLK_ESCAPE:
            game_framework.quit()
        elif e.key in (SDLK_SPACE, SDLK_RETURN):
            game_framework.fade_to(select_mode)


def update():
    global t
    t += 1


def draw():
    assets.image('background.png').draw(640, 360)
    ui.box(0, 0, 1279, 719, ui.INK, 90)
    # 되감기 고리가 천천히 돈다
    ring = assets.image('fx_rewind.png', True)
    ring.clip_draw(((t // 4) % 6) * 128, 0, 128, 128, 640, 470, 384, 384)
    ui.text('10 Seconds', 640, 470, 96, ui.WHITE, align='center')
    ui.text('10초마다 시간이 되감긴다. 과거의 나와 함께 탈출하라.', 640, 380, 22, ui.CYAN, align='center')
    # 나와 지난 회차의 나들
    ghost = assets.image('ghost.png')
    ghost.opacify(0.55)
    for k, x in enumerate((520, 580)):
        draw_body(ghost, x, 180, 1 + (t // 6 + k * 2) % 4, 1)
    draw_body(assets.image('player.png'), 660, 180, 1 + (t // 6) % 4, 1)
    ui.box(0, 150, 1279, 180, (28, 36, 49))
    ui.box(0, 178, 1279, 180, (93, 111, 136))
    if (t // 30) % 2 == 0:
        ui.text('Space 시작', 640, 110, 24, ui.WHITE, align='center')
    ui.text('게임공학과 2023182017 배성우', 640, 40, 14, ui.GREY, align='center')
