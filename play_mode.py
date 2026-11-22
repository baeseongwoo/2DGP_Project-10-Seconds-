import random

from sdl2 import SDL_KEYDOWN, SDLK_ESCAPE, SDLK_F1, SDLK_r, SDLK_z

import clear_mode
import fx
import game_framework
import game_world
import ui
from ghost import Ghost
from objects import Door, Exit, Mover, Pedal
from player import Player
from stage import Stage

ROUND_FRAMES = 600     # 한 회차 10초
REWIND_FRAMES = 28     # 되감기 연출
COLLAPSE_FRAMES = 50   # 시간 붕괴 연출 뒤 같은 회차를 0초부터
CLEAR_FRAMES = 60
SHAKE_FRAMES = 24
MESSAGE_FRAMES = 150

stage_path = 'stages/stage01.json'   # select_mode가 고른 스테이지
result = None                        # 클리어 화면에 넘길 결과

shake_rnd = random.Random()          # 화면 흔들림 전용. 게임 진행과는 상관없다


def init():
    global stage, player, exit_hatch, pedals, doors, movers, ghosts, collapses
    global message, message_t, shake_t, flash_t
    stage = Stage(stage_path)
    game_world.add_object(stage, game_world.STAGE)

    by_id = {}
    pedals = []
    for p in stage.pedals:
        i, j = p['at']
        pedal = Pedal(p['color'], stage.left(i), stage.bottom(j))
        by_id[p['id']] = pedal
        pedals.append(pedal)
    doors = []
    for d in stage.doors:
        i, j = d['at']
        doors.append(Door(d['kind'], stage.left(i), stage.bottom(j), [by_id[k] for k in d['pedals']],
                          d.get('all', False)))
    movers = [Mover(stage, m['path'], m['period'], m.get('hold', 60)) for m in stage.movers]
    i, j = stage.exit
    exit_hatch = Exit(stage.left(i), stage.bottom(j))
    for o in doors + pedals + movers + [exit_hatch]:
        game_world.add_object(o, game_world.OBJECT)

    player = Player(stage)
    game_world.add_object(player, game_world.PLAYER)
    ghosts = []
    collapses = 0
    message, message_t = '', 0
    shake_t = flash_t = 0
    start_round()


def finish():
    game_world.clear()
    game_world.ox = game_world.oy = 0


def pause():
    pass


def resume():
    pass


def start_round():
    """시계와 문, 발판을 처음 상태로 돌리고 모든 기록체를 0초부터 다시 재생한다"""
    global clock, state, state_t
    clock = 0
    state, state_t = 'play', 0
    player.respawn()
    for o in pedals + doors + movers + ghosts:
        o.reset()
    exit_hatch.lit = False
    fx.spawn('blink', player.x, player.y + 50)


def show(text):
    global message, message_t
    message, message_t = text, MESSAGE_FRAMES


def restart_stage():
    global collapses
    for g in ghosts:
        game_world.remove_object(g)
    ghosts.clear()
    collapses = 0
    show('처음부터 다시 한다')
    start_round()


def remove_last_ghost():
    if not ghosts:
        return
    game_world.remove_object(ghosts.pop())
    show(f'기록체 #{len(ghosts) + 1}을 지웠다')
    start_round()


def begin_rewind():
    global state, state_t
    state, state_t = 'rewind', 0
    fx.spawn('rewind', player.x, player.y + 33)


def finish_rewind():
    if len(ghosts) < stage.max_ghosts:
        g = Ghost(player.record, len(ghosts) + 1)
        ghosts.append(g)
        game_world.add_object(g, game_world.GHOST)
    else:
        show(f'기록체가 가득 찼다 ({stage.max_ghosts}명). 이번 기록은 버리고 다시 한다')
    start_round()


def time_collapse(ghost, door):
    """기록체가 지나야 할 문이 닫혀 과거와 현재가 어긋났다"""
    global state, state_t, collapses, shake_t, flash_t
    state, state_t = 'collapse', 0
    collapses += 1
    shake_t, flash_t = SHAKE_FRAMES, 12
    l, b, r, t = door.get_bb()
    fx.spawn('collapse', (l + r) / 2, ghost.y + ghost.H / 2)
    show(f'시간 붕괴! 기록체 #{ghost.number}이 닫힌 문에 막혔다')


def stage_clear():
    global state, state_t
    state, state_t = 'clear', 0
    exit_hatch.lit = True
    fx.spawn('clear', exit_hatch.left + Exit.W / 2, exit_hatch.bottom + 100)


def make_result():
    stars = 1
    if collapses == 0:
        stars = 2
        if len(ghosts) <= stage.recommended:
            stars = 3
    return {'number': stage.number, 'name': stage.name, 'path': stage_path, 'stars': stars,
            'ghosts': len(ghosts), 'recommended': stage.recommended, 'collapses': collapses}


def handle_events(events):
    for event in events:
        if event.type == SDL_KEYDOWN:
            if event.key == SDLK_F1:
                game_world.show_bb = not game_world.show_bb
                continue
            if state != 'clear':
                if event.key == SDLK_ESCAPE:
                    restart_stage()
                    continue
                if state == 'play' and event.key == SDLK_r:
                    begin_rewind()
                    continue
                if state == 'play' and event.key == SDLK_z:
                    remove_last_ghost()
                    continue
        # 연출 중에도 넘겨서 누르고 있는 방향키를 잃어버리지 않게 한다
        player.handle_event(event)


def update():
    global state_t, message_t, shake_t, flash_t, result
    game_world.update()
    message_t = max(0, message_t - 1)
    flash_t = max(0, flash_t - 1)
    if shake_t > 0:
        shake_t -= 1
        amp = round(8 * shake_t / SHAKE_FRAMES)
        game_world.ox, game_world.oy = shake_rnd.randint(-amp, amp), shake_rnd.randint(-amp, amp)
    else:
        game_world.ox = game_world.oy = 0

    if state == 'play':
        play_step()
        return
    state_t += 1
    if state == 'rewind' and state_t >= REWIND_FRAMES:
        finish_rewind()
    elif state == 'collapse' and state_t >= COLLAPSE_FRAMES:
        start_round()
    elif state == 'clear' and state_t == CLEAR_FRAMES:
        result = make_result()
        game_framework.push_mode(clear_mode)


def update_effects():
    """클리어 화면이 위에 떠 있는 동안에도 이펙트는 끝까지 재생한다"""
    game_world.update()


def play_step():
    """한 프레임. 순서가 언제나 같아야 기록체가 같은 결과를 낸다"""
    global clock
    for m in movers:
        m.step(clock)
    for g in ghosts:
        g.step(clock)
    blocks = [d.get_bb() for d in doors if d.is_closed()]
    player.step(blocks, movers + ghosts)
    bodies = [player] + ghosts
    for p in pedals:
        p.step(bodies)
    for d in doors:
        d.step(clock)
        if d.is_closed():
            player.push_out(*d.get_bb())
    player.save_frame()

    for g in ghosts:
        for d in doors:
            if d.is_closed() and game_world.collide(g, d):
                time_collapse(g, d)
                return
    if player.y + player.H < 0:
        show('떨어졌다. 이번 회차를 다시 한다')
        start_round()
        return
    if game_world.collide(player, exit_hatch):
        stage_clear()
        return

    clock += 1
    if clock >= ROUND_FRAMES:
        begin_rewind()


def draw():
    game_world.render()
    if flash_t:
        ui.box(0, 0, 1279, 719, ui.RED, int(110 * flash_t / 12))
    draw_hud()


def draw_hud():
    remaining = (ROUND_FRAMES - clock) / game_framework.FPS
    ui.text(f'{stage.number}. {stage.name}', 24, 694, 20)
    ui.text(f'{remaining:.1f}', 640, 690, 40, ui.ORANGE if remaining <= 3 else ui.WHITE, align='center')
    ui.box(540, 662, 740, 665, (40, 50, 64))
    ui.box(540, 662, 540 + 200 * remaining / 10, 665, ui.ORANGE if remaining <= 3 else ui.CYAN)
    ui.text(f'{len(ghosts) + 1}회차', 640, 648, 15, ui.GREY, align='center')
    ui.text(f'기록체 {len(ghosts)} / {stage.max_ghosts}', 1256, 694, 20, ui.CYAN, align='right')
    ui.text(f'권장 {stage.recommended}명', 1256, 670, 14, ui.GREY, align='right')
    ui.text('← → 이동    Space 점프    R 되감기    Z 기록체 삭제    Esc 처음부터    F1 충돌 상자',
            24, 16, 14, ui.GREY)
    if message_t:
        w = ui.text_width(message, 22)
        ui.box(640 - w / 2 - 18, 586, 640 + w / 2 + 18, 622, ui.INK, 200)
        ui.text(message, 640, 604, 22, ui.WHITE, align='center')
