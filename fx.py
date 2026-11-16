"""코드로 그린 픽셀 이펙트 시트를 재생한다 (pixelfx 방식: 시트는 fx_*.png, 만드는 코드는 tools 밖에 둔다)"""
import assets
import game_world

# 이름: (파일, 칸 너비, 칸 높이, 칸 수, 재생 프레임, 빛처럼 더해서 그리기)
SHEETS = {
    'rewind': ('fx_rewind.png', 128, 128, 16, 28, True),
    'blink': ('fx_blink.png', 64, 112, 12, 20, True),
    'collapse': ('fx_collapse.png', 160, 160, 14, 40, False),
    'spark_green': ('fx_spark_green.png', 64, 32, 8, 14, True),
    'spark_red': ('fx_spark_red.png', 64, 32, 8, 14, True),
    'spark_timer': ('fx_spark_timer.png', 64, 32, 8, 14, True),
    'clear': ('fx_clear.png', 96, 200, 18, 54, True),
}


class Effect:
    def __init__(self, kind, x, y):
        name, self.w, self.h, self.frames, self.duration, additive = SHEETS[kind]
        self.image = assets.image(name, additive)
        self.x, self.y = x, y
        self.t = 0

    def update(self):
        self.t += 1
        if self.t >= self.duration:
            game_world.remove_object(self)

    def draw(self):
        f = min(self.frames - 1, self.t * self.frames // self.duration)
        self.image.clip_draw(f * self.w, 0, self.w, self.h,
                             self.x + game_world.ox, self.y + game_world.oy)


def spawn(kind, x, y):
    """x, y는 이펙트 칸의 가운데"""
    game_world.add_object(Effect(kind, x, y), game_world.FX)
