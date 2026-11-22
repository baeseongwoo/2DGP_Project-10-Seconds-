"""게임에 넣을 스프라이트 시트를 만든다: python tools/make_assets.py [출력 폴더, 기본 resource/]"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_character as mc
from make_character import Canvas, c
import make_map as mm

W, H = mc.W, mc.H
INK = mc.INK
W0, W1, W2 = mc.W0, mc.W1, mc.W2
S0, S1, S2 = mc.S0, mc.S1, mc.S2
K0, K1, K2 = mc.K0, mc.K1, mc.K2
H0, H1, H2 = mc.H0, mc.H1, mc.H2
O0, O1, O2 = mc.O0, mc.O1, mc.O2


def leg(dx, lift):
    """엉덩이(y<50)는 그대로 두고 무릎 아래는 dx만큼, 발(y>=60)은 lift만큼 들어 올린다"""
    def f(x, y):
        if y < 50:
            return x, y
        return x + dx, y - (lift if y >= 60 else lift // 2)
    return f


def pose(far=(0, 0), near=(0, 0), arm=0):
    """make_character.character()와 같은 그림에서 다리와 팔만 움직인 동작 한 칸"""
    g = Canvas(W, H)
    F, N = leg(*far), leg(*near)

    def poly(t, pts, col):
        g.poly([t(x, y) for x, y in pts], col)

    def rect(t, x0, y0, x1, y1, col):
        (a, b), (p, q) = t(x0, y0), t(x1, y1)
        g.rect(a, b, p, q, col)

    def line(t, x0, y0, x1, y1, col):
        (a, b), (p, q) = t(x0, y0), t(x1, y1)
        g.line(a, b, p, q, col)

    I = leg(0, 0)
    # 코트 자락 (뒤)
    poly(I, [(13, 33), (24, 33), (24, 58), (6, 63), (10, 46)], W0)
    poly(I, [(13, 33), (17, 33), (12, 54), (6, 63), (10, 46)], c('#6f7b8c'))
    line(I, 6, 63, 24, 58, O1)
    line(I, 7, 61, 11, 60, O2)
    # 먼 쪽 다리
    poly(F, [(18, 44), (25, 44), (24, 58), (23, 66), (17, 66), (18, 56)], S0)
    poly(F, [(16, 64), (23, 64), (26, 68), (26, 70), (16, 70)], W0)
    rect(F, 16, 70, 26, 70, S0)
    # 가까운 쪽 다리
    poly(N, [(24, 44), (33, 44), (33, 56), (32, 66), (25, 66), (25, 56)], S1)
    line(N, 32, 45, 32, 64, S2)
    line(N, 25, 45, 25, 64, S0)
    rect(N, 27, 53, 31, 57, W0)
    rect(N, 28, 54, 30, 55, W1)
    rect(N, 27, 48, 28, 51, O0)
    poly(N, [(25, 63), (32, 63), (37, 67), (37, 70), (25, 70)], W1)
    rect(N, 26, 64, 31, 64, W2)
    rect(N, 26, 67, 33, 67, O1)
    rect(N, 25, 70, 37, 70, S0)
    # 몸통 재킷
    g.poly([(16, 25), (32, 25), (34, 34), (33, 45), (17, 45), (16, 34)], W1)
    g.poly([(16, 25), (20, 25), (20, 45), (17, 45), (16, 34)], W0)
    g.line(32, 27, 33, 34, W2)
    g.line(33, 34, 32, 41, W2)
    g.line(31, 28, 31, 41, S1)
    # 가슴 번호판 10
    g.rect(23, 30, 29, 36, S0)
    g.line(24, 31, 24, 35, O1)
    g.rect(26, 31, 28, 35, O1)
    g.rect(27, 32, 27, 34, S0)
    # 벨트
    g.rect(17, 42, 33, 44, S0)
    g.rect(27, 42, 30, 44, S2)
    g.rect(28, 43, 29, 43, O1)
    # 칼라
    g.poly([(18, 21), (31, 21), (33, 27), (17, 27)], S1)
    g.line(17, 27, 33, 27, O1)
    g.line(30, 22, 32, 26, S2)
    # 가까운 팔: 팔꿈치(y>=34) 아래를 arm만큼 앞뒤로 흔든다
    A = (lambda x, y: (x + (arm if y >= 34 else 0), y))
    poly(A, [(14, 26), (21, 26), (22, 38), (21, 46), (15, 46), (14, 38)], W0)
    poly(A, [(17, 26), (21, 26), (22, 38), (21, 46), (18, 46), (18, 38)], W1)
    line(A, 20, 27, 21, 37, W2)
    rect(A, 14, 33, 21, 34, S1)
    poly(A, [(15, 46), (21, 46), (21, 50), (19, 52), (16, 51)], K1)
    line(A, 15, 47, 16, 51, K0)
    # 손목 시계
    rect(A, 13, 37, 23, 45, S0)
    g.disc(18 + arm, 41, 5, O1)
    g.disc(18 + arm, 41, 4, S0)
    line(A, 18, 41, 18, 38, W2)
    line(A, 18, 41, 16, 41, O2)
    g.px(18 + arm, 41, W2)
    g.px(14 + arm, 38, O2)
    g.px(22 + arm, 44, O0)
    # 목
    g.rect(22, 20, 29, 23, K0)
    # 얼굴
    g.poly([(18, 8), (31, 8), (34, 12), (34, 18), (31, 22), (23, 22), (19, 18)], K1)
    g.poly([(18, 8), (22, 8), (22, 21), (19, 18)], K0)
    g.line(32, 10, 33, 16, K2)
    g.rect(25, 13, 27, 15, W2)
    g.rect(26, 13, 27, 15, O1)
    g.rect(27, 14, 27, 15, INK)
    g.rect(31, 13, 32, 15, W2)
    g.rect(32, 13, 32, 15, O1)
    g.px(32, 14, INK)
    g.line(25, 12, 28, 11, H0)
    g.line(31, 12, 33, 11, H0)
    g.px(33, 16, K0)
    g.line(29, 19, 32, 19, K0)
    g.line(24, 17, 25, 17, O1)
    # 머리카락
    g.poly([(15, 6), (22, 1), (32, 1), (36, 6), (36, 11), (33, 9), (29, 10), (25, 8), (23, 12), (21, 18), (17, 19), (14, 13)], H1)
    g.poly([(15, 6), (19, 3), (18, 12), (19, 19), (17, 19), (14, 13)], H0)
    g.line(21, 3, 32, 3, H2)
    g.line(24, 4, 30, 8, H2)
    g.line(33, 4, 35, 9, H2)
    g.line(20, 8, 20, 15, H0)
    # 귀 통신기
    g.rect(19, 12, 22, 16, S1)
    g.rect(20, 13, 21, 15, S0)
    g.px(21, 14, O1)
    g.outline(INK)
    return g


# 시트 순서: 0 서기, 1~4 달리기, 5 오르기, 6 떨어지기
FRAMES = [
    pose(),
    pose(far=(-5, 1), near=(5, 0), arm=-2),
    pose(far=(-2, 0), near=(2, 3), arm=0),
    pose(far=(5, 0), near=(-5, 1), arm=2),
    pose(far=(2, 3), near=(-2, 0), arm=0),
    pose(far=(-3, 4), near=(4, 6), arm=-2),
    pose(far=(-2, 1), near=(3, 2), arm=2),
]


RECORD_COLORS = [(255, 92, 168), (166, 140, 255), (216, 242, 107)]


def hologram(g, col):
    """밝기에 따라 어두운 기록체 색 -> 기록체 색 -> 흰빛으로 칠하고, 짝수 줄만 진하게 남긴다"""
    dark = tuple(round(v * 0.22) for v in col)
    light = tuple(round(v + (255 - v) * 0.75) for v in col)
    out = Canvas(g.w, g.h)
    for y in range(g.h):
        for x in range(g.w):
            v = g.p[y][x]
            if not v:
                continue
            L = (0.3 * v[0] + 0.59 * v[1] + 0.11 * v[2]) / 255
            if L < 0.5:
                u = L / 0.5
                rgb = tuple(round(dark[i] + (col[i] - dark[i]) * u) for i in range(3))
            else:
                u = (L - 0.5) / 0.5
                rgb = tuple(round(col[i] + (light[i] - col[i]) * u) for i in range(3))
            out.p[y][x] = rgb + (255 if y % 2 == 0 else 120,)
    return out


def projection_ring():
    """발밑 투영 고리 4칸. 흰색으로 그려 두고 게임에서 기록체 색을 입힌다"""
    frames = []
    for f in range(4):
        g = Canvas(48, 12)
        rx, ry = 18 + f, 4
        for a in range(0, 360, 3):
            import math
            x = 24 + rx * math.cos(math.radians(a))
            y = 6 + ry * math.sin(math.radians(a))
            if (a // 3 + f) % 4 != 0:
                g.px(round(x), round(y), (255, 255, 255, 200 if y > 6 else 110))
        frames.append(g)
    return mm.sheet(frames)


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'resource')
    os.makedirs(out, exist_ok=True)
    mm.OUT = out
    mm.save(mm.sheet(FRAMES), 'player.png')
    mm.save(mm.tileset(), 'tiles.png')
    mm.save(mm.background(), 'background.png')
    objs = mm.make_objs()
    mm.save(objs['exit'], 'exit.png')
    # 2~3주차 오브젝트: 발판은 [올라옴, 눌림] 2칸, 문은 닫힘 -> 열림 5칸
    for color in ('green', 'red'):
        mm.save(mm.sheet([objs[f'pedal_{color}_up'], objs[f'pedal_{color}_down']]), f'pedal_{color}.png')
    gold = (mm.O0, mm.O1, mm.O2)
    mm.save(mm.sheet([mm.pedal(*gold, False, False), mm.pedal(*gold, False, True)]), 'pedal_timer.png')
    for kind in ('green', 'red', 'timer'):
        mm.save(objs[f'door_{kind}'], f'door_{kind}.png')
    mm.save(objs['moving'], 'mover.png')
    # 4주차: 회차별 색 홀로그램 기록체. 밝기를 기록체 색 단계로 바꾸고 홀수 줄을 비워 주사선을 만든다
    for k, col in enumerate(RECORD_COLORS, 1):
        mm.save(mm.sheet([hologram(f, col) for f in FRAMES]), f'record_{k}.png')
    mm.save(projection_ring(), 'record_ring.png')
    import fx_gen
    fx_gen.main(out)
    print(sorted(os.listdir(out)))


if __name__ == '__main__':
    main()
