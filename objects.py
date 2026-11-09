from pico2d import draw_rectangle, load_image

import game_world


class Exit:
    W, H = 64, 96

    def __init__(self, left, bottom):
        self.left, self.bottom = left, bottom
        self.image = load_image('resource/exit.png')
        self.lit = False

    def get_bb(self):
        # 해치 안쪽 문 부분에 닿아야 통과한다
        return self.left + 16, self.bottom, self.left + self.W - 16, self.bottom + 80

    def update(self):
        pass

    def draw(self):
        self.image.clip_draw(self.W if self.lit else 0, 0, self.W, self.H,
                             self.left + self.W // 2, self.bottom + self.H // 2)
        if game_world.show_bb:
            draw_rectangle(*self.get_bb())
