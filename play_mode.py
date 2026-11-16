from pico2d import clear_canvas, get_events, update_canvas
from sdl2 import SDL_KEYDOWN, SDL_QUIT, SDLK_ESCAPE, SDLK_F1, SDLK_r, SDLK_z

import game_framework
import game_world
import ui
from ghost import Ghost
from objects import Exit
from player import Player
from stage import Stage

ROUND_FRAMES = 600     # 한 회차 10초
CLEAR_FRAMES = 60      # 출구에 닿고 1초 뒤 처음부터 다시 한다
MESSAGE_FRAMES = 150

stage_path = 'stages/test.json'


def init():
    global stage, player, exit_hatch, ghosts, message, message_t
    stage = Stage(stage_path)
    game_world.add_object(stage, game_world.STAGE)
    i, j = stage.exit
    exit_hatch = Exit(stage.left(i), stage.bottom(j))
    game_world.add_object(exit_hatch, game_world.OBJECT)

    player = Player(stage)
    game_world.add_object(player, game_world.PLAYER)
    ghosts = []
    message, message_t = '', 0
    start_round()


def finish():
    game_world.clear()


def pause():
    pass


def resume():
    pass


def start_round():
    """시계를 0으로 돌리고 모든 유령을 0초부터 다시 재생한다"""
    global clock, cleared_t
    clock = 0
    cleared_t = None
    player.respawn()
    for o in ghosts:
        o.reset()
    exit_hatch.lit = False


def show(text):
    global message, message_t
    message, message_t = text, MESSAGE_FRAMES


def restart_stage():
    for g in ghosts:
        game_world.remove_object(g)
    ghosts.clear()
    show('처음부터 다시 한다')
    start_round()


def remove_last_ghost():
    if not ghosts:
        return
    game_world.remove_object(ghosts.pop())
    show(f'{len(ghosts) + 1}번 유령을 지웠다')
    start_round()


def rewind():
    """이번 회차의 기록을 유령으로 남기고 새 회차를 시작한다. 가득 찼으면 기록을 버린다"""
    if len(ghosts) < stage.max_ghosts:
        g = Ghost(player.record, len(ghosts) + 1)
        ghosts.append(g)
        game_world.add_object(g, game_world.GHOST)
    else:
        show(f'유령이 가득 찼다 ({stage.max_ghosts}명). 이번 기록은 버리고 다시 한다')
    start_round()


def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
            continue
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_F1:
                game_world.show_bb = not game_world.show_bb
                continue
            if cleared_t is None:
                if event.key == SDLK_ESCAPE:
                    restart_stage()
                    continue
                if event.key == SDLK_r:
                    rewind()
                    continue
                if event.key == SDLK_z:
                    remove_last_ghost()
                    continue
        player.handle_event(event)


def update():
    global cleared_t, message_t
    message_t = max(0, message_t - 1)
    if cleared_t is not None:
        cleared_t += 1
        if cleared_t >= CLEAR_FRAMES:
            restart_stage()
        return
    play_step()


def play_step():
    """한 프레임. 순서가 언제나 같아야 유령이 같은 결과를 낸다"""
    global clock, cleared_t
    for g in ghosts:
        g.step(clock)
    player.step([], ghosts)
    player.save_frame()

    if player.y + player.H < 0:
        start_round()   # 구덩이에 빠지면 이번 회차를 다시 한다
        return
    if game_world.collide(player, exit_hatch):
        exit_hatch.lit = True
        cleared_t = 0
        print(f'{stage.name} 클리어: 유령 {len(ghosts)}명')
        return

    clock += 1
    if clock >= ROUND_FRAMES:
        rewind()


def draw():
    clear_canvas()
    game_world.render()
    if message_t:
        w = ui.text_width(message, 22)
        ui.box(640 - w / 2 - 18, 586, 640 + w / 2 + 18, 622, ui.INK, 200)
        ui.text(message, 640, 604, 22, ui.WHITE, align='center')
    update_canvas()
