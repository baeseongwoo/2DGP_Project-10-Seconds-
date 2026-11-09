from pico2d import delay, get_time

FPS = 60
FRAME_TIME = 1.0 / FPS
MAX_STEPS = 5   # 창을 끌다 놓는 등 루프가 멈췄다 돌아와도 한꺼번에 따라잡지 않게 제한한다

running = False
stack = []


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


def quit():
    global running
    running = False


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

        stack[-1].handle_events()
        while lag >= FRAME_TIME and running:
            stack[-1].update()
            lag -= FRAME_TIME
        stack[-1].draw()
        delay(0.001)

    while stack:
        stack.pop().finish()
