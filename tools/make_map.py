"""타일, 발판, 문, 움직이는 발판, 출구, 배경을 그리는 코드. 직접 실행하면 기획서용 맵 미리보기를 만든다."""
import math, os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from make_character import Canvas, c, character, to_ghost, write_png

OUT = sys.argv[1] if len(sys.argv) > 1 else HERE
TILE = 32

A0, A1, A2, A3, A4 = c('#1c2431'), c('#2c3748'), c('#3f4d63'), c('#5d6f88'), c('#9db0c4')
B0, B1, B2, B3 = c('#0d121a'), c('#131a25'), c('#19222f'), c('#212c3b')
O0, O1, O2 = c('#b85c12'), c('#ff9f45'), c('#ffd9a8')
G0, G1, G2 = c('#2f8f4a'), c('#62d67a'), c('#c4f5ce')
R0, R1, R2 = c('#8c2626'), c('#d9463d'), c('#ffb3a8')
Y1, Y2 = c('#ffe27a'), c('#fff6cf')
WH, INK = c('#f1f4f7'), c('#10151e')


def save(g, name):
    write_png(os.path.join(OUT, name), [[v or (0, 0, 0, 0) for v in row] for row in g.p], g.w, g.h)


def blit(dst, src, ox, oy, sx=0, sy=0, sw=None, sh=None, alpha=1.0):
    sw, sh = sw or src.w, sh or src.h
    for y in range(sh):
        for x in range(sw):
            v = src.p[sy + y][sx + x]
            X, Y = ox + x, oy + y
            if not v or not (0 <= X < dst.w and 0 <= Y < dst.h):
                continue
            if alpha >= 1 or not dst.p[Y][X]:
                dst.p[Y][X] = v
            else:
                b = dst.p[Y][X]
                dst.p[Y][X] = tuple(round(v[k] * alpha + b[k] * (1 - alpha)) for k in range(3)) + (255,)


def sheet(frames):
    g = Canvas(sum(f.w for f in frames), frames[0].h)
    x = 0
    for f in frames:
        blit(g, f, x, 0)
        x += f.w
    return g


def wall_tile(top=False, bottom=False, left=False, right=False):
    g = Canvas(TILE, TILE)
    g.rect(0, 0, 31, 31, A1)
    # 큰 선체 판 하나로 보이게 이음매는 가장자리에만 둔다
    g.rect(0, 31, 31, 31, A0)
    g.rect(31, 0, 31, 31, A0)
    g.rect(0, 0, 31, 0, c('#35425a'))
    g.rect(0, 0, 0, 31, c('#35425a'))
    for x, y in ((4, 4), (27, 4), (4, 27), (27, 27)):
        g.px(x, y, A3)
        g.px(x + 1, y + 1, A0)
    if left:
        g.rect(0, 0, 2, 31, A3)
        g.rect(3, 0, 3, 31, A0)
    if right:
        g.rect(29, 0, 31, 31, A0)
        g.rect(28, 0, 28, 31, A2)
    if bottom:
        g.rect(0, 26, 31, 31, A0)
        g.rect(0, 25, 31, 25, A2)
    if top:
        g.rect(0, 0, 31, 2, A4)
        g.rect(0, 3, 31, 5, A3)
        g.rect(0, 6, 31, 6, A0)
        for x in range(4, 32, 8):
            g.px(x, 4, A4)
    return g


def vent_tile():
    g = wall_tile()
    g.rect(5, 6, 26, 25, A0)
    for y in range(8, 25, 3):
        g.rect(7, y, 24, y, A3)
    return g


def hazard_tile():
    g = wall_tile(top=True)
    g.rect(0, 8, 31, 14, INK)
    for x in range(-8, 32, 8):
        g.poly([(x, 15), (x + 4, 15), (x + 11, 8), (x + 7, 8)], O1)
    return g


def light_tile():
    g = wall_tile()
    g.rect(2, 11, 29, 20, A0)
    g.rect(4, 13, 27, 18, O0)
    g.rect(6, 15, 25, 16, O2)
    return g


def platform_tile(left=False, right=False):
    g = Canvas(TILE, TILE)
    x0, x1 = (3 if left else 0), (28 if right else 31)
    g.rect(x0, 0, x1, 2, A4)
    g.rect(x0, 3, x1, 7, A2)
    g.rect(x0, 8, x1, 10, A0)
    for x in range(x0 + 3, x1, 8):
        g.px(x, 5, O1)
    if left:
        g.poly([(3, 11), (12, 11), (6, 19), (3, 19)], A0)
    if right:
        g.poly([(19, 11), (29, 11), (29, 19), (25, 19)], A0)
    return g


def tileset():
    rows = [
        [wall_tile(True, False, True), wall_tile(True), wall_tile(True, False, False, True), platform_tile(left=True)],
        [wall_tile(left=True), wall_tile(), wall_tile(right=True), platform_tile()],
        [wall_tile(False, True, True), wall_tile(bottom=True), wall_tile(False, True, False, True), platform_tile(right=True)],
        [vent_tile(), hazard_tile(), light_tile(), wall_tile(True, True, True, True)],
    ]
    g = Canvas(TILE * 4, TILE * 4)
    for j, row in enumerate(rows):
        for i, t in enumerate(row):
            blit(g, t, i * TILE, j * TILE)
    return g


def pedal(col0, col1, col2, stripes, pressed):
    g = Canvas(48, 16)
    g.rect(1, 11, 46, 14, A2)
    g.rect(1, 15, 46, 15, A0)
    g.rect(1, 11, 46, 11, A3)
    top = 7 if pressed else 2
    g.rect(5, top, 42, 10, col0)
    g.rect(5, top, 42, top + 2, col2 if pressed else col1)
    for x in range(8, 40, 6):
        if stripes:
            g.line(x, top + 3, x + 3, top, col0)
        else:
            g.px(x + 1, top + 1, WH)
            g.px(x + 2, top + 1, WH)
    g.outline(INK)
    return g


def door_frame(col0, col1, col2, mark, offset):
    g = Canvas(48, 96)
    top = 8
    for y in range(top, 96 - offset):
        g.rect(7, y, 40, y, A2)
    bottom = 95 - offset
    if bottom >= top:
        g.rect(7, top, 9, bottom, A3)
        g.rect(38, top, 40, bottom, A0)
        g.rect(23, top, 24, bottom, A1)
        for y in range(max(top, bottom - 5), bottom + 1):
            g.rect(7, y, 40, y, col0 if (y // 2) % 2 else INK)

    # 표식은 문짝과 함께 올라간다
    def mark_px(x, y, v):
        if top <= y <= bottom - 6:
            g.px(x, y, v)
    my = 46 - offset
    if mark == 'up':
        for i in range(9):
            for dx in range(-i, i + 1):
                mark_px(24 + dx, my - 8 + i, col1)
        for y in range(my + 1, my + 11):
            for x in range(21, 27):
                mark_px(x, y, col1)
    elif mark == 'x':
        for i in range(-9, 10):
            for k in (-1, 0, 1):
                mark_px(24 + i + k, my + i, col1)
                mark_px(24 - i + k, my + i, col1)
    else:
        for a in range(0, 360, 6):
            for r in (9, 10):
                mark_px(24 + round(r * math.cos(math.radians(a))), my + round(r * math.sin(math.radians(a))), col1)
        for y in range(my - 7, my + 1):
            mark_px(24, y, col2)
        for x in range(24, 30):
            mark_px(x, my, col2)
    g.rect(0, 0, 4, 95, A1)
    g.rect(43, 0, 47, 95, A1)
    g.rect(0, 0, 0, 95, A3)
    g.rect(47, 0, 47, 95, A0)
    g.rect(5, 8, 6, 95, A0)
    g.rect(41, 8, 42, 95, A0)
    g.rect(0, 0, 47, 7, A2)
    g.rect(0, 0, 47, 1, A4)
    g.rect(14, 3, 33, 5, col1 if offset else col0)
    g.rect(16, 4, 31, 4, col2 if offset else col1)
    return g


def door_sheet(col0, col1, col2, mark):
    return sheet([door_frame(col0, col1, col2, mark, o) for o in (0, 22, 44, 66, 88)])


def moving_platform(flame):
    g = Canvas(96, 24)
    g.poly([(1, 3), (94, 3), (90, 15), (5, 15)], A2)
    g.rect(1, 0, 94, 2, A4)
    g.rect(1, 3, 94, 3, A3)
    g.line(5, 15, 90, 15, A0)
    for x in range(30, 66, 8):
        g.poly([(x, 7), (x + 3, 7), (x + 6, 10), (x + 3, 13), (x, 13), (x + 3, 10)], O1)
    for x in (12, 76):
        g.rect(x, 12, x + 7, 16, A0)
        g.rect(x + 2, 17, x + 5, 17 + flame, O1)
        g.rect(x + 3, 17, x + 4, 15 + flame, Y2)
    g.px(9, 8, O2)
    g.px(86, 8, O2)
    return g


def exit_hatch(lit):
    g = Canvas(64, 96)
    g.rect(0, 0, 63, 95, A1)
    g.rect(0, 0, 63, 3, A4)
    g.rect(0, 0, 2, 95, A3)
    g.rect(61, 0, 63, 95, A0)
    g.disc(32, 38, 26, A3)
    g.disc(32, 38, 23, A0)
    g.disc(32, 38, 18, B0)
    random.seed(10)
    for _ in range(14):
        a, r = random.random() * 6.28, random.random() * 16
        g.px(round(32 + r * math.cos(a)), round(38 + r * math.sin(a)), WH)
    for a in range(0, 360, 45):
        g.disc(round(32 + 24.5 * math.cos(math.radians(a))), round(38 + 24.5 * math.sin(math.radians(a))), 1, Y1 if lit else A1)
    g.rect(10, 70, 53, 89, A0)
    col = Y2 if lit else Y1
    for i in range(7):
        g.rect(14 + i * 5, 73, 16 + i * 5, 86, Y1 if lit and i % 2 == 0 else A2)
    g.poly([(26, 74), (34, 74), (41, 80), (34, 86), (26, 86), (33, 80)], col)
    g.outline(INK)
    return g


def warning_light(on):
    g = Canvas(16, 16)
    g.rect(2, 11, 13, 14, A2)
    g.disc(8, 7, 5, O1 if on else O0)
    g.disc(7, 6, 2, O2 if on else O1)
    g.outline(INK)
    return g


def monitor():
    g = Canvas(48, 40)
    g.rect(1, 1, 46, 32, A2)
    g.rect(1, 1, 46, 1, A4)
    g.rect(4, 4, 43, 29, B0)
    pts = [(5, 22), (11, 22), (14, 11), (18, 26), (22, 18), (28, 18), (31, 8), (36, 20), (42, 20)]
    for a, b in zip(pts, pts[1:]):
        g.line(a[0], a[1], b[0], b[1], O1)
    for y in range(6, 29, 6):
        g.rect(5, y, 42, y, A0)
    g.rect(20, 33, 27, 38, A0)
    g.outline(INK)
    return g


def crate():
    g = Canvas(32, 32)
    g.rect(1, 1, 30, 30, A2)
    g.rect(1, 1, 30, 3, A4)
    g.rect(1, 28, 30, 30, A0)
    g.rect(1, 1, 3, 30, A3)
    g.rect(28, 1, 30, 30, A1)
    g.line(6, 7, 25, 25, A1)
    g.line(25, 7, 6, 25, A1)
    g.rect(11, 12, 20, 19, INK)
    g.rect(12, 13, 19, 18, O1)
    g.rect(14, 15, 17, 16, INK)
    g.outline(INK)
    return g


def stasis_pod():
    g = Canvas(48, 96)
    g.rect(4, 12, 43, 83, c('#101a24'))
    g.disc(24, 34, 7, c('#1e2c3a'))
    g.poly([(15, 44), (33, 44), (31, 72), (17, 72)], c('#1e2c3a'))
    g.line(9, 16, 9, 78, c('#2c3e4e'))
    g.line(11, 16, 11, 50, c('#2c3e4e'))
    g.line(36, 22, 31, 30, A3)
    g.line(31, 30, 35, 37, A3)
    g.line(31, 30, 26, 32, A3)
    g.rect(2, 2, 45, 11, A2)
    g.rect(2, 2, 45, 3, A4)
    g.rect(2, 12, 4, 83, A1)
    g.rect(43, 12, 45, 83, A0)
    g.rect(1, 84, 46, 95, A2)
    g.rect(1, 84, 46, 85, A3)
    g.rect(1, 94, 46, 95, A0)
    g.rect(16, 87, 31, 93, B0)
    g.rect(20, 88, 20, 92, O1)
    g.rect(24, 88, 27, 92, O1)
    g.rect(25, 89, 26, 91, B0)
    g.rect(38, 6, 41, 8, O1)
    g.outline(INK)
    return g


def background(w=1280, h=720):
    g = Canvas(w, h)
    g.rect(0, 0, w - 1, h - 1, B1)
    random.seed(2023182017 % 1000)
    for y in range(0, h, 64):
        g.rect(0, y, w - 1, y, B0)
        g.rect(0, y + 1, w - 1, y + 1, B2)
    for j, y in enumerate(range(0, h, 64)):
        for x in range((j % 2) * 40, w, 80):
            g.rect(x, y, x, y + 63, B0)
            g.px(x + 4, y + 6, B3)
            g.px(x + 75, y + 6, B3)
    wins = [(170, 130, 520, 340), (760, 130, 1110, 340)]
    px, py, pr = 1010, 300, 130
    for x0, y0, x1, y1 in wins:
        g.rect(x0 - 14, y0 - 14, x1 + 14, y1 + 14, B3)
        g.rect(x0 - 14, y0 - 14, x1 + 14, y0 - 13, c('#2c3a4c'))
        g.rect(x0 - 3, y0 - 3, x1 + 3, y1 + 3, B0)
        g.rect(x0, y0, x1, y1, c('#05070d'))
        for _ in range((x1 - x0) * (y1 - y0) // 500):
            sx, sy = random.randint(x0, x1), random.randint(y0, y1)
            g.px(sx, sy, random.choice([c('#3a4556'), c('#5d6b80'), c('#8c9aad'), c('#c9d2dc')]))
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                d = (x - px) ** 2 + (y - py) ** 2
                if d <= pr ** 2:
                    band = (y + 14 * math.sin(x / 40)) // 14
                    lit = math.hypot(x - (px - 70), y - (py - 70)) / pr
                    k = 0 if lit < 0.8 else 1 if lit < 1.15 else 2
                    pal = [[c('#5a3b2e'), c('#6e4a38')], [c('#3a2a26'), c('#47332c')], [c('#1c1618'), c('#221a1b')]][k]
                    g.p[y][x] = pal[int(band) % 2]
        for x in range(x0 + 116, x1, 117):
            g.rect(x, y0, x + 3, y1, B3)
    for x in (0, 620, 1216):
        g.rect(x, 0, x + 63, h - 1, B2)
        g.rect(x, 0, x + 1, h - 1, B3)
        g.rect(x + 62, 0, x + 63, h - 1, B0)
        for y in range(40, h, 96):
            g.rect(x + 28, y, x + 35, y + 3, B0)
    g.rect(0, 86, w - 1, 95, B2)
    g.rect(0, 86, w - 1, 87, B3)
    g.rect(0, 95, w - 1, 95, B0)
    for x in range(30, w, 150):
        g.rect(x, 84, x + 7, 97, B3)
    for x in range(100, w, 200):
        g.rect(x, 440, x + 40, 443, c('#3a2a1c'))
        g.rect(x + 8, 441, x + 32, 442, c('#6b4524'))
    return g


def compose(tiles, objs, blocks, platforms, items, actors):
    """blocks: 타일 좌표 사각형 (i0, j0, i1, j1), platforms: (i0, i1, j), items: (이름, x, y, 프레임 또는 None)"""
    w, h = 40, 23
    solid = [[j < 2 or j >= 18 or i < 1 or i >= 39 for i in range(w)] for j in range(h)]
    for i0, j0, i1, j1 in blocks:
        for j in range(j0, j1 + 1):
            for i in range(i0, i1 + 1):
                solid[j][i] = True
    g = Canvas(1280, 720)
    blit(g, objs['bg'], 0, 0)
    for j in range(h):
        for i in range(w):
            if not solid[j][i]:
                continue
            t = j > 0 and not solid[j - 1][i]
            b = j < h - 1 and not solid[j + 1][i]
            l = i > 0 and not solid[j][i - 1]
            r = i < w - 1 and not solid[j][i + 1]
            col = {(True, False): 0, (False, False): 1, (False, True): 2}.get((l, r), 3)
            row = 0 if t else 2 if b else 1
            if col == 3:
                col, row = 3, 3
            blit(g, tiles, i * TILE, j * TILE, col * TILE, row * TILE, TILE, TILE)
    for i0, i1, j in platforms:
        for i in range(i0, i1 + 1):
            row = 0 if i == i0 else 2 if i == i1 else 1
            blit(g, tiles, i * TILE, j * TILE, 3 * TILE, row * TILE, TILE, TILE)
    for name, x, y, frame in items:
        src = objs[name]
        if frame is None:
            blit(g, src, x, y)
        else:
            fw = src.w // {'door_green': 5, 'door_red': 5, 'door_timer': 5, 'moving': 2, 'exit': 2}[name]
            blit(g, src, x, y, frame * fw, 0, fw, src.h)
    me = character()
    ghost = to_ghost(me)
    for kind, x, y in actors:
        if kind == 'ghost':
            blit(g, ghost, x, y, alpha=0.5)
        else:
            blit(g, me, x, y)
    return g


def make_objs():
    return {
        'bg': background(),
        'pedal_green_up': pedal(G0, G1, G2, False, False), 'pedal_green_down': pedal(G0, G1, G2, False, True),
        'pedal_red_up': pedal(R0, R1, R2, True, False), 'pedal_red_down': pedal(R0, R1, R2, True, True),
        'door_green': door_sheet(G0, G1, G2, 'up'), 'door_red': door_sheet(R0, R1, R2, 'x'),
        'door_timer': door_sheet(O0, O1, O2, 'clock'),
        'moving': sheet([moving_platform(2), moving_platform(5)]),
        'exit': sheet([exit_hatch(False), exit_hatch(True)]),
        'light_on': warning_light(True), 'light': sheet([warning_light(False), warning_light(True)]),
        'monitor': monitor(), 'crate': crate(), 'pod': stasis_pod(),
    }


FLOOR = 576


def stage_maps(tiles, objs):
    # 방 1: 과거의 내가 문을 연다. 유령이 초록 발판을 누르는 동안 문을 지난다.
    m1 = compose(tiles, objs, [(26, 2, 27, 14)], [],
                 [('pod', 80, 480, None), ('monitor', 150, 500, None), ('crate', 600, 544, None),
                  ('pedal_green_down', 380, 560, None), ('door_green', 840, 480, 4), ('light_on', 856, 450, None),
                  ('exit', 1140, 480, 1)],
                 [('ghost', 380, 567 - 72), ('me', 900, FLOOR - 72)])
    # 방 3: 3초 안에 달린다. 먼 발판을 유령이 밟아 두고, 나는 문 앞에서 기다린다.
    m3 = compose(tiles, objs, [(30, 2, 31, 14), (12, 16, 17, 17)], [],
                 [('pedal_green_down', 90, 560, None), ('crate', 700, 544, None), ('crate', 732, 544, None),
                  ('door_timer', 968, 480, 4), ('light_on', 984, 450, None), ('exit', 1140, 480, 1)],
                 [('ghost', 90, 567 - 72), ('me', 900, FLOOR - 72)])
    # 방 8: 나를 딛고 오른다. 높은 턱 아래에 유령을 세우고 머리를 밟는다.
    m8 = compose(tiles, objs, [(28, 13, 38, 17)], [(6, 10, 12)],
                 [('pod', 80, 480, None), ('monitor', 220, 330, None), ('exit', 1150, 320, 1),
                  ('light_on', 1100, 384, None)],
                 [('ghost', 830, FLOOR - 72), ('me', 818, FLOOR - 72 - 70)])
    return m1, m3, m8


def catalog(tiles, objs, pedals):
    g = Canvas(640, 360)
    g.rect(0, 0, 639, 359, B2)
    for src, x, y in [(tiles, 8, 8), (pedals, 144, 8), (objs['door_green'], 248, 8), (objs['door_red'], 248, 112),
                      (objs['door_timer'], 248, 216), (objs['moving'], 8, 144), (objs['exit'], 8, 176),
                      (objs['pod'], 144, 176), (objs['monitor'], 144, 56), (objs['crate'], 200, 56), (objs['light'], 200, 100)]:
        blit(g, src, x, y)
    out = Canvas(1280, 720)
    for y in range(360):
        for x in range(640):
            out.rect(x * 2, y * 2, x * 2 + 1, y * 2 + 1, g.p[y][x])
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    tiles = tileset()
    objs = make_objs()
    pedals = Canvas(96, 32)
    blit(pedals, objs['pedal_green_up'], 0, 0)
    blit(pedals, objs['pedal_green_down'], 48, 0)
    blit(pedals, objs['pedal_red_up'], 0, 16)
    blit(pedals, objs['pedal_red_down'], 48, 16)
    save(catalog(tiles, objs, pedals), 'preview_objects.png')
    for name, m in zip(('map_stage1.png', 'map_stage3.png', 'map_stage8.png'), stage_maps(tiles, objs)):
        save(m, name)


if __name__ == '__main__':
    main()
