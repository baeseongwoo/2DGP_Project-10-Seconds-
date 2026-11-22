"""pixelfx(github.com/patch-gg/pixelfx)의 방식을 따라 이펙트를 코드로 그려 스프라이트 시트로 만든다.

- 이펙트 하나 = draw(p, t) 함수. t는 0~1, 같은 t면 언제나 같은 그림 (무작위는 시드 고정)
- 색은 어두운 색 -> 밝은 색 팔레트 단계로 고른다. 팔레트만 바꾸면 같은 이펙트를 다른 색으로 쓴다
- 빛나는 이펙트는 게임에서 가산 합성으로 그린다 (pixelfx의 light 버퍼)
"""
import math, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_character import write_png


def ramp(*hexes):
    return [(int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)) for h in hexes]


TIME = ramp('#0f5f5a', '#1fa39a', '#5fe0d0', '#c9fff7', '#ffffff')
GOLD = ramp('#7a4a10', '#c47a18', '#ff9f45', '#ffd9a8', '#fff6cf')
RED = ramp('#4a0f14', '#8c2626', '#d9463d', '#ff8a70', '#ffd9cc')
GREEN = ramp('#1d5a30', '#2f8f4a', '#62d67a', '#c4f5ce', '#ffffff')


class P:
    """한 칸짜리 RGBA 버퍼. 같은 칸에 여러 번 찍으면 더 밝은 쪽을 남긴다"""

    def __init__(self, w, h, pal):
        self.w, self.h, self.pal = w, h, pal
        self.px = [[None] * w for _ in range(h)]

    def dot(self, x, y, level, alpha=1.0):
        """level 0~1을 팔레트 단계로 바꿔 찍는다"""
        x, y = int(round(x)), int(round(y))
        if not (0 <= x < self.w and 0 <= y < self.h) or alpha <= 0.02:
            return
        level = max(0.0, min(1.0, level))
        col = self.pal[min(len(self.pal) - 1, int(level * len(self.pal)))]
        a = int(255 * max(0.0, min(1.0, alpha)))
        old = self.px[y][x]
        if old is None or old[3] < a or (old[3] == a and sum(old[:3]) < sum(col)):
            self.px[y][x] = col + (a,)

    def square(self, x, y, s, level, alpha=1.0):
        for j in range(s):
            for i in range(s):
                self.dot(x + i - s // 2, y + j - s // 2, level, alpha)

    def line(self, x0, y0, x1, y1, level, alpha=1.0):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for k in range(n + 1):
            u = k / n
            self.dot(x0 + (x1 - x0) * u, y0 + (y1 - y0) * u, level, alpha)


def ease_out(u):
    return 1 - (1 - u) ** 3


# ---- 이펙트 ----

def rewind_ring(p, t):
    """되감기: 시곗바늘이 거꾸로 돌며 시간이 가운데로 빨려 들어간다"""
    cx, cy = p.w / 2, p.h / 2
    r = 6 + 54 * (1 - ease_out(t))
    spin = -t * math.tau * 0.8
    fade = 1 - t * 0.6
    for k in range(12):
        a = spin + k * math.tau / 12
        ln = 7 if k % 3 == 0 else 4
        p.line(cx + math.cos(a) * r, cy + math.sin(a) * r,
               cx + math.cos(a) * (r - ln), cy + math.sin(a) * (r - ln), 0.95 if k % 3 == 0 else 0.7, fade)
    for d in range(0, 360, 4):
        a = math.radians(d) + spin
        p.dot(cx + math.cos(a) * (r + 3), cy + math.sin(a) * (r + 3), 0.35, fade * 0.8)
    for speed, ln, lv in ((-3.0, 18, 0.9), (-0.9, 12, 0.6)):
        a = -math.pi / 2 + speed * t * math.tau
        p.line(cx, cy, cx + math.cos(a) * ln * (1 - t * 0.5), cy + math.sin(a) * ln * (1 - t * 0.5), lv, 1 - t)
    p.square(cx, cy, 3, 1.0, 1 - t * 0.5)


def blink_in(p, t):
    """등장: 세로 빛기둥이 좁아지며 몸이 나타난다"""
    cx = p.w / 2
    half = 18 * (1 - t) ** 1.5
    for y in range(p.h):
        edge = 1 - abs(y - p.h * 0.55) / (p.h * 0.6)
        for x in range(int(cx - half), int(cx + half) + 1):
            core = 1 - abs(x - cx) / (half + 1)
            p.dot(x, y, 0.2 + 0.8 * core, edge * core * (1 - t) * 1.2)
    rnd = random.Random(11)
    for _ in range(16):
        x0, y0, v = rnd.uniform(4, p.w - 4), rnd.uniform(p.h * 0.3, p.h), rnd.uniform(30, 60)
        y = y0 - v * t
        tw = 1 if int(t * 12 + x0) % 2 else 0.6
        p.dot(x0, y, 0.9 * tw, (1 - t) * 1.1)


def collapse_burst(p, t):
    """시간 붕괴: 금이 가고, 조각이 튀고, 화면 줄이 어긋난다"""
    cx, cy = p.w / 2, p.h / 2
    rnd = random.Random(23)
    # 금
    if t < 0.6:
        grow = min(1.0, t / 0.25)
        for k in range(7):
            a = k * math.tau / 7 + rnd.uniform(-0.3, 0.3)
            x, y = cx, cy
            for s in range(6):
                a2 = a + rnd.uniform(-0.5, 0.5)
                seg = 10 * grow
                nx, ny = x + math.cos(a2) * seg, y + math.sin(a2) * seg
                for ox, oy in ((0, 0), (1, 0), (0, 1)):
                    p.line(x + ox, y + oy, nx + ox, ny + oy, 0.9 - s * 0.1, 1 - t / 0.6)
                x, y = nx, ny
    else:
        for k in range(7):
            rnd.uniform(-0.3, 0.3)
            for s in range(6):
                rnd.uniform(-0.5, 0.5)
    # 조각
    for _ in range(22):
        a, v, size = rnd.uniform(0, math.tau), rnd.uniform(40, 80), rnd.choice((2, 2, 3))
        x = cx + math.cos(a) * v * ease_out(t)
        y = cy + math.sin(a) * v * ease_out(t) + 30 * t * t
        p.square(x, y, size, rnd.uniform(0.4, 0.9), 1 - t ** 2)
    # 어긋난 줄
    if t < 0.5:
        for _ in range(5):
            y, w, off = rnd.randrange(p.h), rnd.randrange(30, 90), rnd.randrange(-12, 12)
            x0 = rnd.randrange(0, p.w - w)
            for x in range(x0, x0 + w, 2):
                p.dot(x + off, y, 0.55, 0.8 - t)


def spark(p, t):
    """발판을 밟았을 때 위로 튀는 불꽃"""
    rnd = random.Random(5)
    for _ in range(12):
        a = rnd.uniform(math.radians(30), math.radians(150))
        v = rnd.uniform(18, 34)
        x = p.w / 2 + math.cos(a) * v * ease_out(t) * 1.4
        y = p.h - 2 - math.sin(a) * v * ease_out(t) + 22 * t * t
        p.square(x, y, 2, 0.7 - t * 0.5, 1 - t)
    if t < 0.4:
        for x in range(4, p.w - 4, 3):
            p.dot(x, p.h - 2, 0.6, 1 - t / 0.4)


def clear_beam(p, t):
    """탈출: 탈출정에서 금빛 기둥이 솟는다"""
    cx = p.w / 2
    rise = ease_out(min(1.0, t / 0.5))
    fade = 1 if t < 0.6 else 1 - (t - 0.6) / 0.4
    top = p.h * (1 - rise)
    half = 14 + 6 * math.sin(t * 20)
    for y in range(int(top), p.h):
        for x in range(int(cx - half), int(cx + half) + 1):
            core = 1 - abs(x - cx) / (half + 1)
            p.dot(x, y, 0.3 + 0.7 * core, core * fade)
    rnd = random.Random(31)
    for _ in range(20):
        x0, d, v = rnd.uniform(8, p.w - 8), rnd.uniform(0, 0.5), rnd.uniform(80, 160)
        u = max(0.0, t - d)
        if u <= 0:
            continue
        p.square(x0, p.h - v * u, 2, 0.95, fade * (1 - u))


EFFECTS = [
    # 이름, 함수, 칸 크기, 칸 수, 팔레트
    ('fx_rewind', rewind_ring, (128, 128), 16, TIME),
    ('fx_blink', blink_in, (64, 112), 12, TIME),
    ('fx_collapse', collapse_burst, (160, 160), 14, RED),
    ('fx_spark_green', spark, (64, 32), 8, GREEN),
    ('fx_spark_red', spark, (64, 32), 8, RED),
    ('fx_spark_timer', spark, (64, 32), 8, GOLD),
    ('fx_clear', clear_beam, (96, 200), 18, GOLD),
]


def render(fn, size, frames, pal):
    w, h = size
    rows = [[(0, 0, 0, 0)] * (w * frames) for _ in range(h)]
    for f in range(frames):
        p = P(w, h, pal)
        fn(p, f / (frames - 1) if frames > 1 else 0)
        for y in range(h):
            for x in range(w):
                if p.px[y][x]:
                    rows[y][f * w + x] = p.px[y][x]
    return rows, w * frames, h


def main(out):
    os.makedirs(out, exist_ok=True)
    for name, fn, size, frames, pal in EFFECTS:
        rows, w, h = render(fn, size, frames, pal)
        write_png(os.path.join(out, name + '.png'), rows, w, h)
        print(name, w, h)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'resource'))
