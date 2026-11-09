from pico2d import clear_canvas, get_events, update_canvas
from sdl2 import SDL_KEYDOWN, SDL_QUIT, SDLK_ESCAPE, SDLK_F1

import game_framework
import game_world
from objects import Exit
from player import Player
from stage import Stage

STAGE_PATH = 'stages/test.json'
CLEAR_FRAMES = 60   # 출구에 닿고 1초 뒤 스테이지를 다시 시작한다

stage = None
player = None
exit_hatch = None
clock = 0           # 프레임 시계. 2주차에 10초(600프레임) 회차로 쓴다
cleared_at = None


def init():
    global stage, player, exit_hatch
    stage = Stage(STAGE_PATH)
    game_world.add_object(stage, 0)
    i, j = stage.exit
    exit_hatch = Exit(stage.left(i), stage.bottom(j))
    game_world.add_object(exit_hatch, 1)
    player = Player(stage)
    game_world.add_object(player, 2)
    reset()


def reset():
    global clock, cleared_at
    clock = 0
    cleared_at = None
    exit_hatch.lit = False
    player.respawn()


def finish():
    game_world.clear()


def pause():
    pass


def resume():
    pass


def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            reset()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_F1:
            game_world.show_bb = not game_world.show_bb
        else:
            player.handle_event(event)


def update():
    global clock, cleared_at
    clock += 1
    if cleared_at is not None:
        if clock - cleared_at >= CLEAR_FRAMES:
            reset()
        return

    game_world.update()
    if player.y + player.H < 0:
        player.respawn()   # 구덩이에 빠지면 시작 위치로
    elif game_world.collide(player, exit_hatch):
        exit_hatch.lit = True
        cleared_at = clock
        print(f'{stage.name} 클리어: {clock / game_framework.FPS:.2f}초')


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()
