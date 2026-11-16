from pico2d import draw_rectangle

import assets
import game_world
import ui
from player import Player, draw_body


class Ghost:
    """지난 회차의 나. 기록을 프레임 칸 그대로 다시 보여 준다.

    물리 계산을 하지 않으므로 같은 시계 값이면 언제나 같은 자리에 있다.
    기록이 끝나면(일찍 되감았으면) 마지막 자리에 그대로 서 있다.
    """
    ALPHA = 0.55
    W, H = Player.W, Player.H

    def __init__(self, record, number):
        self.record = record
        self.number = number      # 몇 번째 회차에서 남은 유령인지
        self.image = assets.image('ghost.png')
        self.reset()

    def reset(self):
        self.step(0)
        self.px, self.py = self.x, self.y

    def step(self, clock):
        if hasattr(self, 'x'):
            self.px, self.py = self.x, self.y
        self.x, self.y, self.frame, self.face_dir = self.record[min(clock, len(self.record) - 1)]

    def delta(self):
        return self.x - self.px, self.y - self.py

    def get_bb(self):
        return self.x - self.W / 2, self.y, self.x + self.W / 2, self.y + self.H

    def get_top(self):
        # 머리 위는 위에서 떨어질 때만 밟힌다
        return self.x - self.W / 2 - 4, self.y + self.H, self.x + self.W / 2 + 4

    def update(self):
        pass

    def draw(self):
        self.image.opacify(Ghost.ALPHA)
        draw_body(self.image, self.x, self.y, self.frame, self.face_dir)
        ui.text(str(self.number), self.x + game_world.ox, self.y + self.H + 18 + game_world.oy,
                14, ui.CYAN, align='center')
        if game_world.show_bb:
            draw_rectangle(*self.get_bb(), 95, 224, 208)
