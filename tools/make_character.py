"""캐릭터(실험체 10호)를 픽셀 단위로 그리는 바탕 코드와 PNG 저장 함수. 직접 실행하면 기획서용 미리보기를 만든다."""
import struct, sys, zlib, os

OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
W, H = 48, 72


def c(h):
    return (int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16), 255)


S0, S1, S2 = c('#2a3140'), c('#3f4a5e'), c('#5c6b85')
W0, W1, W2 = c('#8f9bab'), c('#c7d0da'), c('#f1f4f7')
O0, O1, O2 = c('#b85c12'), c('#ff9f45'), c('#ffd9a8')
K0, K1, K2 = c('#c98f6c'), c('#eebf9c'), c('#f9d9bf')
H0, H1, H2 = c('#76859b'), c('#c2ccd8'), c('#f4f7fa')
INK = c('#10151e')


class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.p = [[None] * w for _ in range(h)]

    def px(self, x, y, col):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.p[y][x] = col

    def rect(self, x0, y0, x1, y1, col):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.px(x, y, col)

    def poly(self, pts, col):
        for y in range(self.h):
            yc = y + 0.5
            xs = []
            for i in range(len(pts)):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % len(pts)]
                if (y0 <= yc < y1) or (y1 <= yc < y0):
                    xs.append(x0 + (yc - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for a, b in zip(xs[::2], xs[1::2]):
                for x in range(round(a), round(b)):
                    self.px(x, y, col)

    def line(self, x0, y0, x1, y1, col):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            self.px(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), col)

    def disc(self, cx, cy, r, col):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r + r * 0.6:
                    self.px(x, y, col)

    def outline(self, col):
        add = []
        for y in range(self.h):
            for x in range(self.w):
                if self.p[y][x] is None:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.w and 0 <= ny < self.h and self.p[ny][nx] is not None:
                            add.append((x, y))
                            break
        for x, y in add:
            self.p[y][x] = col


def character():
    g = Canvas(W, H)
    # 코트 자락 (뒤)
    g.poly([(13, 33), (24, 33), (24, 58), (6, 63), (10, 46)], W0)
    g.poly([(13, 33), (17, 33), (12, 54), (6, 63), (10, 46)], c('#6f7b8c'))
    g.line(6, 63, 24, 58, O1)
    g.line(7, 61, 11, 60, O2)
    # 먼 쪽 다리
    g.poly([(18, 44), (25, 44), (24, 58), (23, 66), (17, 66), (18, 56)], S0)
    g.poly([(16, 64), (23, 64), (26, 68), (26, 70), (16, 70)], W0)
    g.rect(16, 70, 26, 70, S0)
    # 가까운 쪽 다리
    g.poly([(24, 44), (33, 44), (33, 56), (32, 66), (25, 66), (25, 56)], S1)
    g.line(32, 45, 32, 64, S2)
    g.line(25, 45, 25, 64, S0)
    g.rect(27, 53, 31, 57, W0)
    g.rect(28, 54, 30, 55, W1)
    g.rect(27, 48, 28, 51, O0)
    g.poly([(25, 63), (32, 63), (37, 67), (37, 70), (25, 70)], W1)
    g.rect(26, 64, 31, 64, W2)
    g.rect(26, 67, 33, 67, O1)
    g.rect(25, 70, 37, 70, S0)
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
    # 가까운 팔
    g.poly([(14, 26), (21, 26), (22, 38), (21, 46), (15, 46), (14, 38)], W0)
    g.poly([(17, 26), (21, 26), (22, 38), (21, 46), (18, 46), (18, 38)], W1)
    g.line(20, 27, 21, 37, W2)
    g.rect(14, 33, 21, 34, S1)
    # 손
    g.poly([(15, 46), (21, 46), (21, 50), (19, 52), (16, 51)], K1)
    g.line(15, 47, 16, 51, K0)
    # 손목 시계
    g.rect(13, 37, 23, 45, S0)
    g.disc(18, 41, 5, O1)
    g.disc(18, 41, 4, S0)
    g.line(18, 41, 18, 38, W2)
    g.line(18, 41, 16, 41, O2)
    g.px(18, 41, W2)
    g.px(14, 38, O2)
    g.px(22, 44, O0)
    # 목
    g.rect(22, 20, 29, 23, K0)
    # 얼굴
    g.poly([(18, 8), (31, 8), (34, 12), (34, 18), (31, 22), (23, 22), (19, 18)], K1)
    g.poly([(18, 8), (22, 8), (22, 21), (19, 18)], K0)
    g.line(32, 10, 33, 16, K2)
    # 눈
    g.rect(25, 13, 27, 15, W2)
    g.rect(26, 13, 27, 15, O1)
    g.rect(27, 14, 27, 15, INK)
    g.rect(31, 13, 32, 15, W2)
    g.rect(32, 13, 32, 15, O1)
    g.px(32, 14, INK)
    g.line(25, 12, 28, 11, H0)
    g.line(31, 12, 33, 11, H0)
    # 코와 입
    g.px(33, 16, K0)
    g.line(29, 19, 32, 19, K0)
    # 뺨의 회로선
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


def watch():
    g = Canvas(25, 25)
    g.rect(8, 0, 16, 24, S1)
    g.rect(8, 0, 9, 24, S0)
    g.rect(15, 0, 16, 24, S2)
    g.disc(12, 12, 11, S0)
    g.disc(12, 12, 10, O1)
    g.disc(12, 12, 8, S0)
    for x, y in ((12, 5), (12, 19), (5, 12), (19, 12)):
        g.px(x, y, W2)
    for x, y in ((7, 7), (17, 7), (7, 17), (17, 17)):
        g.px(x, y, W0)
    # 거꾸로 도는 표시
    g.line(12, 12, 12, 7, W2)
    g.line(12, 12, 8, 12, O2)
    g.line(14, 8, 17, 11, O2)
    g.line(17, 11, 17, 14, O2)
    g.line(14, 8, 16, 8, O1)
    g.line(14, 8, 14, 10, O1)
    g.px(12, 12, W2)
    g.px(3, 3, O2)
    g.outline(INK)
    return g


def to_ghost(g):
    a, b = (15, 95, 90), (201, 255, 247)
    out = Canvas(g.w, g.h)
    for y in range(g.h):
        for x in range(g.w):
            v = g.p[y][x]
            if v:
                L = (0.3 * v[0] + 0.59 * v[1] + 0.11 * v[2]) / 255
                out.p[y][x] = tuple(round(a[i] + (b[i] - a[i]) * L) for i in range(3)) + (255,)
    return out


def write_png(path, rows, w, h):
    raw = b''.join(b'\0' + bytes(v for p in row for v in p) for row in rows)

    def chunk(t, d):
        return struct.pack('>I', len(d)) + t + d + struct.pack('>I', zlib.crc32(t + d))

    with open(path, 'wb') as f:
        f.write(b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
                + chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b''))


def save_sprite(g, path):
    write_png(path, [[v or (0, 0, 0, 0) for v in row] for row in g.p], g.w, g.h)


def stamp(sheet, g, ox, oy, s, alpha=1.0):
    for y in range(g.h):
        for x in range(g.w):
            v = g.p[y][x]
            if not v:
                continue
            for j in range(s):
                for i in range(s):
                    bg = sheet[oy + y * s + j][ox + x * s + i]
                    sheet[oy + y * s + j][ox + x * s + i] = tuple(
                        round(v[k] * alpha + bg[k] * (1 - alpha)) for k in range(3)) + (255,)


def main():
    me, gh, wa = character(), None, watch()
    gh = to_ghost(me)
    os.makedirs(OUT, exist_ok=True)
    save_sprite(me, os.path.join(OUT, 'me_idle.png'))
    save_sprite(gh, os.path.join(OUT, 'ghost_idle.png'))
    sw, sh = 1000, 500
    floor = 450
    sheet = [[c('#1b2430') if y < floor else c('#2d3947') for x in range(sw)] for y in range(sh)]
    for x in range(sw):
        for y in range(floor, floor + 4):
            sheet[y][x] = c('#4a5a6c')
    stamp(sheet, me, 30, floor - 71 * 6 + 2, 6)
    stamp(sheet, gh, 340, floor - 71 * 6 + 2, 6, 0.5)
    stamp(sheet, wa, 690, 30, 11)
    stamp(sheet, me, 700, floor - 71 * 2 + 2, 2)
    stamp(sheet, gh, 800, floor - 71 * 2 + 2, 2, 0.5)
    write_png(os.path.join(OUT, 'character_sheet.png'), sheet, sw, sh)


if __name__ == '__main__':
    main()
