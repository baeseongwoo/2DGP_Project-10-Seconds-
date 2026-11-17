from sdl2 import SDL_KEYDOWN, SDLK_ESCAPE, SDLK_RETURN, SDLK_SPACE, SDLK_r

import game_framework
import play_mode
import select_mode
import ui

t = 0


def init():
    global t
    t = 0
    r = play_mode.result
    select_mode.record(r['number'], r['stars'])


def finish():
    pass


def pause():
    pass


def resume():
    pass


def handle_events(events):
    for e in events:
        if e.type != SDL_KEYDOWN or t < 20:
            continue
        if e.key in (SDLK_SPACE, SDLK_RETURN):
            nxt = select_mode.next_stage(play_mode.result['number'])
            if nxt:
                select_mode.start(nxt)
            else:
                game_framework.fade_to(select_mode)
        elif e.key == SDLK_r:
            play_mode.stage_path = play_mode.result['path']
            game_framework.fade_to(play_mode)
        elif e.key == SDLK_ESCAPE:
            game_framework.fade_to(select_mode)


def update():
    global t
    t += 1
    play_mode.update_effects()


def draw():
    r = play_mode.result
    play_mode.draw()
    ui.box(0, 0, 1279, 719, ui.INK, 170)
    ui.box(380, 200, 900, 540, (20, 27, 38), 235)
    ui.frame(380, 200, 900, 540, (63, 77, 99))
    ui.text('스테이지 클리어', 640, 500, 34, ui.GOLD, align='center')
    ui.text(f'{r["number"]}. {r["name"]}', 640, 456, 20, ui.WHITE, align='center')
    for k in range(3):
        # 별이 하나씩 차례로 나타난다
        on = k < r['stars'] and t >= 12 + k * 10
        ui.text('★' if on else '☆', 560 + k * 80, 390, 56, ui.GOLD if on else ui.GREY, align='center')
    ui.text(f'사용한 기록체 {r["ghosts"]}명 (권장 {r["recommended"]}명)', 640, 320, 18, ui.CYAN, align='center')
    ui.text(f'시간 붕괴 {r["collapses"]}회', 640, 292, 18, ui.RED if r['collapses'] else ui.GREY, align='center')
    ui.text('Space 다음 스테이지    R 다시 하기    Esc 스테이지 선택', 640, 236, 16, ui.GREY, align='center')
