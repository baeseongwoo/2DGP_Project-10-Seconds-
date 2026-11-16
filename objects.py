"""스테이지 오브젝트. 시계로 움직이는 것들은 step(clock)으로 한 프레임씩 진행한다.

같은 회차 시간에는 언제나 같은 상태가 되어야 유령 재생이 어긋나지 않는다.
"""
from pico2d import draw_rectangle

import assets
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
    """두 칸 너비 바닥에 놓인다. 플레이어든 유령이든 몸이 닿아 있으면 눌린다"""
    W, H = 48, 16

    def __init__(self, color, left, bottom):
        self.color = color   # green, red, timer
        self.cx, self.bottom = left + TILE, bottom
        self.image = assets.image(f'pedal_{color}.png')
        self.reset()

    def reset(self):
        self.pressed = False
        self.just_pressed = False

    def get_bb(self):
        return self.cx - 22, self.bottom, self.cx + 22, self.bottom + 10

    def step(self, bodies):
        was = self.pressed
        self.pressed = any(game_world.collide(self, b) for b in bodies)
        self.just_pressed = self.pressed and not was

    def update(self):
        pass

    def draw(self):
        self.image.clip_draw(self.W if self.pressed else 0, 0, self.W, self.H,
                             self.cx + game_world.ox, self.bottom + self.H // 2 + game_world.oy)
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
        self.frame = float(self.LAST_FRAME) if self.kind == 'red' else 0.0

    def is_closed(self):
        # 문짝이 반 넘게 올라가야 지나갈 수 있다
        return self.frame < 3

    def get_bb(self):
        return self.cx - 16, self.bottom, self.cx + 16, self.bottom + self.H

    def step(self, clock):
        pressed = any(p.pressed for p in self.pedals)
        if self.kind == 'green':
            want_open = pressed
        elif self.kind == 'red':
            want_open = not pressed
        else:
            # 계속 밟고 있어도 다시 열리지 않는다. 다시 밟아야 3초가 새로 시작된다
            if any(p.just_pressed for p in self.pedals):
                self.open_until = clock + Door.OPEN_FRAMES
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
        if self.kind == 'timer' and self.open_until > getattr(self, 'clock', 0):
            # 남은 시간 막대
            left = (self.open_until - self.clock) / Door.OPEN_FRAMES
            ui.box(self.cx - 20 + ox, self.bottom + self.H + 4 + oy,
                   self.cx - 20 + 40 * left + ox, self.bottom + self.H + 8 + oy, ui.ORANGE)
        if game_world.show_bb and self.is_closed():
            draw_rectangle(*self.get_bb())
