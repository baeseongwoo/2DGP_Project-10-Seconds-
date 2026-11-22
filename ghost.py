from pico2d import draw_rectangle
import sdl2

import assets
import game_world
import ui
from player import Player, draw_body


class Ghost:
    """기록체: 지난 회차의 나. 기록을 프레임 칸 그대로 다시 보여 준다.

    물리 계산을 하지 않으므로 같은 시계 값이면 언제나 같은 자리에 있다.
    기록이 끝나면(일찍 되감았으면) 마지막 자리에 그대로 서 있다.
    번호마다 색이 다른 홀로그램으로 그린다: 주사선(시트에 들어 있음), 가끔 어긋나는 글리치, 발밑 투영 고리.
    """
    ALPHA = 0.9
    W, H = Player.W, Player.H
    SPRITE_W, SPRITE_H = Player.SPRITE_W, Player.SPRITE_H

    def __init__(self, record, number):
        self.record = record
        self.number = number      # 몇 번째 기록체인지
        self.color = ui.RECORD[(number - 1) % len(ui.RECORD)]
        self.image = assets.image(f'record_{(number - 1) % len(ui.RECORD) + 1}.png')
        self.ring = assets.image('record_ring.png', True)
        self.door_history = []    # 녹화된 회차에서 프레임마다 문이 열려 있었는지 (붕괴 예고에 쓴다)
        self.presses, self.passes = [], []   # 타임라인에 그릴 발판 구간과 문 지난 순간
        self.reset()

    def reset(self):
        self.step(0)
        self.px, self.py = self.x, self.y

    def step(self, clock):
        if hasattr(self, 'x'):
            self.px, self.py = self.x, self.y
        self.clock = clock
        self.x, self.y, self.frame, self.face_dir = self.record[min(clock, len(self.record) - 1)]

    def delta(self):
        return self.x - self.px, self.y - self.py

    def get_bb(self):
        return self.x - self.W / 2, self.y, self.x + self.W / 2, self.y + self.H

    def get_top(self):
        # 머리 위는 위에서 떨어질 때만 밟힌다
        return self.x - self.W / 2 - 4, self.y + self.H, self.x + self.W / 2 + 4

    def glitch(self):
        """시계와 번호로 정하는 글리치. 같은 회차 시간이면 언제나 같은 모양이다"""
        k = (self.clock * 7 + self.number * 31) % 97
        return 0 if k > 3 else (3 if k % 2 else -3)

    def update(self):
        pass

    def draw(self):
        ox, oy = game_world.ox, game_world.oy
        sdl2.SDL_SetTextureColorMod(self.ring.texture, *self.color)
        self.ring.clip_draw(((self.clock // 8) % 4) * 48, 0, 48, 12, self.x + ox, self.y + 2 + oy)

        self.image.opacify(Ghost.ALPHA)
        shift = self.glitch()
        if shift == 0:
            draw_body(self.image, self.x, self.y, self.frame, self.face_dir)
        else:
            # 윗부분만 옆으로 밀려 보이게 둘로 나눠 그린다
            w, h, cut = self.SPRITE_W, self.SPRITE_H, 30
            left = self.frame * w
            x, y = round(self.x) + ox, round(self.y) - 1 + oy
            flip = '' if self.face_dir == 1 else 'h'
            self.image.clip_composite_draw(left, 0, w, cut, 0, flip, x, y + cut / 2, w, cut)
            self.image.clip_composite_draw(left, cut, w, h - cut, 0, flip, x + shift, y + cut + (h - cut) / 2, w, h - cut)
        ui.text(f'#{self.number}', self.x + ox, self.y + self.H + 18 + oy, 14, self.color, align='center')
        if game_world.show_bb:
            draw_rectangle(*self.get_bb(), *self.color)
