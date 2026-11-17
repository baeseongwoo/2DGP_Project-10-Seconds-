"""스테이지 오브젝트. 시계로 움직이는 것들은 step(clock)으로 한 프레임씩 진행한다.

같은 회차 시간에는 언제나 같은 상태가 되어야 기록체 재생이 어긋나지 않는다.
"""
from pico2d import draw_rectangle

import assets
import fx
import game_world
import ui
from stage import TILE


class Exit:
    W, H = 64, 96

    def __init__(self, left, bottom):
        self.left, self.bottom = left, bottom
        self.image = assets.image('exit.png')
        self.lit = False

    def get_bb(self):
        # 해치 안쪽 문 부분에 닿아야 통과한다
        return self.left + 16, self.bottom, self.left + self.W - 16, self.bottom + 80

    def update(self):
        pass

    def draw(self):
        self.image.clip_draw(self.W if self.lit else 0, 0, self.W, self.H,
                             self.left + self.W // 2 + game_world.ox, self.bottom + self.H // 2 + game_world.oy)
        if game_world.show_bb:
            draw_rectangle(*self.get_bb())


class Pedal:
    """두 칸 너비 바닥에 놓인다. 나든 기록체든 몸이 닿아 있으면 눌리고, 누른 몸의 색으로 표시등이 켜진다"""
    W, H = 48, 16

    def __init__(self, color, left, bottom):
        self.color = color   # green, red, timer
        self.cx, self.bottom = left + TILE, bottom
        self.image = assets.image(f'pedal_{color}.png')
        self.reset()

    def reset(self):
        self.pressed = False
        self.just_pressed = False
        self.by = None       # 누르고 있는 몸의 색

    def get_bb(self):
        return self.cx - 22, self.bottom, self.cx + 22, self.bottom + 10

    def step(self, bodies):
        was = self.pressed
        on = [b for b in bodies if game_world.collide(self, b)]
        self.pressed = bool(on)
        self.by = on[0].color if on else None
        self.just_pressed = self.pressed and not was
        if self.just_pressed:
            fx.spawn('spark_' + self.color, self.cx, self.bottom + 16)

    def update(self):
        pass

    def draw(self):
        ox, oy = game_world.ox, game_world.oy
        self.image.clip_draw(self.W if self.pressed else 0, 0, self.W, self.H,
                             self.cx + ox, self.bottom + self.H // 2 + oy)
        if self.by:
            ui.box(self.cx - 14 + ox, self.bottom + 1 + oy, self.cx + 14 + ox, self.bottom + 3 + oy, self.by)
        if game_world.show_bb:
            draw_rectangle(*self.get_bb())


class Door:
    """green: 발판을 밟는 동안 열린다. red: 밟는 동안 닫힌다. timer: 밟는 순간부터 3초 열린다"""
    W, H = 48, 96
    OPEN_FRAMES = 180
    LAST_FRAME = 4

    def __init__(self, kind, left, bottom, pedals):
        self.kind = kind
        self.cx, self.bottom = left + TILE // 2, bottom
        self.pedals = pedals
        self.image = assets.image(f'door_{kind}.png')
        self.reset()

    def reset(self):
        self.open_until = -1
        self.by = None       # 이 문을 움직인 몸의 색 (문 위 표시등)
        self.frame = float(self.LAST_FRAME) if self.kind == 'red' else 0.0

    def is_closed(self):
        # 문짝이 반 넘게 올라가야 지나갈 수 있다
        return self.frame < 3

    def get_bb(self):
        return self.cx - 16, self.bottom, self.cx + 16, self.bottom + self.H

    def step(self, clock):
        pressed = any(p.pressed for p in self.pedals)
        if self.kind != 'timer':
            self.by = next((p.by for p in self.pedals if p.pressed), None)
        if self.kind == 'green':
            want_open = pressed
        elif self.kind == 'red':
            want_open = not pressed
        else:
            # 계속 밟고 있어도 다시 열리지 않는다. 다시 밟아야 3초가 새로 시작된다
            if any(p.just_pressed for p in self.pedals):
                self.open_until = clock + Door.OPEN_FRAMES
                self.by = next(p.by for p in self.pedals if p.just_pressed)
            if clock >= self.open_until:
                self.by = None
            want_open = clock < self.open_until
        if want_open:
            self.frame = min(self.LAST_FRAME, self.frame + 0.5)
        else:
            self.frame = max(0.0, self.frame - 1.0)
        self.clock = clock

    def update(self):
        pass

    def draw(self):
        ox, oy = game_world.ox, game_world.oy
        self.image.clip_draw(int(self.frame) * self.W, 0, self.W, self.H,
                             self.cx + ox, self.bottom + self.H // 2 + oy)
        if self.by:
            # 문틀 위 표시등이 이 문을 움직인 몸의 색으로 켜진다
            top = self.bottom + self.H + oy
            ui.box(self.cx - 10 + ox, top - 6, self.cx + 9 + ox, top - 3, self.by)
        if self.kind == 'timer' and self.open_until > getattr(self, 'clock', 0):
            # 남은 시간 막대
            left = (self.open_until - self.clock) / Door.OPEN_FRAMES
            ui.box(self.cx - 20 + ox, self.bottom + self.H + 4 + oy,
                   self.cx - 20 + 40 * left + ox, self.bottom + self.H + 8 + oy, ui.ORANGE)
        if game_world.show_bb and self.is_closed():
            draw_rectangle(*self.get_bb())


class Mover:
    """두 지점 사이를 시계에 맞춰 왕복한다. 위에서만 밟히고, 올라탄 몸을 함께 옮긴다"""
    W, H = 96, 24

    def __init__(self, stage, path, period, hold=60):
        (i0, j0), (i1, j1) = path
        # j는 발판 윗면이 맞닿을 칸 줄: 그 칸의 윗변이 발판 윗면이 된다
        self.a = (stage.left(i0), stage.bottom(j0) + TILE)
        self.b = (stage.left(i1), stage.bottom(j1) + TILE)
        self.period = period
        self.hold = hold                          # 양 끝에서 멈춰 있는 프레임. 이때 타고 내린다
        self.travel = (period - 2 * hold) / 2     # 한쪽으로 가는 데 걸리는 프레임
        self.image = assets.image('mover.png')
        self.reset()

    def reset(self):
        self.step(0)
        self.px, self.ptop = self.x, self.top

    def position(self, clock):
        t, hold, travel = clock % self.period, self.hold, self.travel
        if t < hold:                            # 출발점에서 멈춤
            s = 0.0
        elif t < hold + travel:                 # 가는 길
            s = (t - hold) / travel
        elif t < 2 * hold + travel:             # 끝점에서 멈춤
            s = 1.0
        else:                                   # 돌아오는 길
            s = 1 - (t - 2 * hold - travel) / travel
        s = s * s * (3 - 2 * s)                 # 출발과 도착을 부드럽게
        return (self.a[0] + (self.b[0] - self.a[0]) * s,
                self.a[1] + (self.b[1] - self.a[1]) * s)

    def step(self, clock):
        if hasattr(self, 'x'):
            self.px, self.ptop = self.x, self.top
        self.x, self.top = self.position(clock)
        self.flame = (clock // 6) % 2

    def delta(self):
        return self.x - self.px, self.top - self.ptop

    def get_top(self):
        return self.x + 2, self.top, self.x + self.W - 2

    def update(self):
        pass

    def draw(self):
        self.image.clip_draw(self.flame * self.W, 0, self.W, self.H,
                             self.x + self.W / 2 + game_world.ox, self.top - self.H / 2 + game_world.oy)
        if game_world.show_bb:
            l, t, r = self.get_top()
            draw_rectangle(l, t - 4, r, t)
