from pico2d import clear_canvas, delay, get_events, get_time, update_canvas
from sdl2 import SDL_QUIT

import ui

FPS = 60
FRAME_TIME = 1.0 / FPS
MAX_STEPS = 5     # 창을 끌다 놓는 등 루프가 멈췄다 돌아와도 한꺼번에 따라잡지 않게 제한한다
WIPE_FRAMES = 18  # 화면 전환: 가리는 데 18프레임, 걷는 데 18프레임
BLINDS = 16

running = False
stack = []
wipe_to = None    # 가리는 중이면 다음 모드
wipe_t = 0        # 0이면 전환 없음. 양수면 가리는 중, 음수면 걷는 중


def change_mode(mode):
    if stack:
        stack.pop().finish()
    stack.append(mode)
    mode.init()


def push_mode(mode):
    if stack:
        stack[-1].pause()
    stack.append(mode)
    mode.init()


def pop_mode():
    stack.pop().finish()
    if stack:
        stack[-1].resume()


def fade_to(mode):
    """블라인드가 닫히고, 다 가려지면 모드를 바꾼 뒤 다시 열린다"""
    global wipe_to, wipe_t
    if wipe_t == 0:
        wipe_to, wipe_t = mode, 1


def busy():
    return wipe_t != 0


def quit():
    global running
    running = False


def step_wipe():
    global wipe_to, wipe_t
    if wipe_t > 0:
        wipe_t += 1
        if wipe_t > WIPE_FRAMES:
            # 클리어 화면처럼 위에 얹힌 모드까지 모두 닫고 새 모드 하나로 시작한다
            while stack:
                stack.pop().finish()
            stack.append(wipe_to)
            wipe_to.init()
            wipe_to, wipe_t = None, -WIPE_FRAMES
    elif wipe_t < 0:
        wipe_t += 1


def draw_wipe():
    if wipe_t == 0:
        return
    cover = wipe_t / WIPE_FRAMES if wipe_t > 0 else -wipe_t / WIPE_FRAMES
    w = 1280 / BLINDS
    for k in range(BLINDS):
        # 왼쪽 띠부터 차례로 닫힌다
        u = max(0.0, min(1.0, cover * 1.6 - k / BLINDS * 0.6))
        if u > 0:
            cx = (k + 0.5) * w
            ui.box(cx - w * u / 2, 0, cx + w * u / 2, 720, ui.INK)


def run(start_mode):
    """update는 항상 1/60초 단위로 부른다. 유령 기록을 프레임 칸으로 저장하므로 속도가 달라지면 안 된다."""
    global running
    running = True
    stack.append(start_mode)
    start_mode.init()

    last = get_time()
    lag = 0.0
    while running:
        now = get_time()
        lag = min(lag + now - last, FRAME_TIME * MAX_STEPS)
        last = now

        events = get_events()
        if any(e.type == SDL_QUIT for e in events):
            quit()
        elif not busy():
            stack[-1].handle_events(events)
        while lag >= FRAME_TIME and running:
            if wipe_t <= 0:
                stack[-1].update()
            step_wipe()
            lag -= FRAME_TIME

        clear_canvas()
        stack[-1].draw()
        draw_wipe()
        update_canvas()
        delay(0.001)

    while stack:
        stack.pop().finish()
