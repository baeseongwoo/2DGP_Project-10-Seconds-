import json

from pico2d import load_image

TILE = 32
SCREEN_H = 720

WALL, PLATFORM = '#', '-'
START, EXIT = 'P', 'E'


class Stage:
    """JSON 맵을 읽어 타일을 그리고 충돌 판정에 쓸 칸 정보를 준다.

    맵은 위에서 아래로 쓴 문자열 줄이다. # 벽, - 아래에서 통과하는 발판, P 시작 위치, E 출구(왼쪽 아래 칸).
    """

    def __init__(self, path):
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
        self.name = data['name']
        self.rows = data['map']
        self.h = len(self.rows)
        self.w = len(self.rows[0])
        assert all(len(r) == self.w for r in self.rows), path
        # 맵이 화면보다 크면 아래쪽이 잘리도록 맞춘다 (23줄이면 16px)
        self.origin_y = SCREEN_H - self.h * TILE

        self.start = self.find(START)
        self.exit = self.find(EXIT)

        self.background = load_image('resource/background.png')
        self.tiles = load_image('resource/tiles.png')
        self.draw_list = self.make_draw_list()

    def find(self, ch):
        for j, row in enumerate(self.rows):
            i = row.find(ch)
            if i >= 0:
                return i, j
        raise ValueError(f'{self.name}: {ch} 칸이 없다')

    # 칸 좌표 (i: 왼쪽부터, j: 위부터) <-> 화면 좌표 (pico2d는 왼쪽 아래가 원점)
    def left(self, i):
        return i * TILE

    def bottom(self, j):
        return self.origin_y + (self.h - 1 - j) * TILE

    def col(self, x):
        return int(x // TILE)

    def row(self, y):
        return self.h - 1 - int((y - self.origin_y) // TILE)

    def is_wall(self, i, j):
        if j >= self.h:
            return False   # 맵 아래는 비워 둬서 구덩이에 빠지면 떨어진다
        if i < 0 or i >= self.w or j < 0:
            return True
        return self.rows[j][i] == WALL

    def is_platform(self, i, j):
        return 0 <= j < self.h and 0 <= i < self.w and self.rows[j][i] == PLATFORM

    def make_draw_list(self):
        """벽 칸마다 이웃이 비었는지 보고 tiles.png에서 모서리, 가장자리, 안쪽 그림을 고른다"""
        out = []
        for j in range(self.h):
            for i in range(self.w):
                if self.is_platform(i, j):
                    left_end = not self.is_platform(i - 1, j)
                    right_end = not self.is_platform(i + 1, j)
                    out.append((3, 0 if left_end else 2 if right_end else 1, i, j))
                    continue
                if self.rows[j][i] != WALL:
                    continue
                inside = (lambda a, b: not (0 <= a < self.w and 0 <= b < self.h) or self.rows[b][a] == WALL)
                t, b = not inside(i, j - 1), not inside(i, j + 1)
                l, r = not inside(i - 1, j), not inside(i + 1, j)
                c = {(True, False): 0, (False, False): 1, (False, True): 2}.get((l, r), 3)
                rw = 0 if t else 2 if b else 1
                if c == 3:
                    c, rw = 3, 3
                out.append((c, rw, i, j))
        return out

    def update(self):
        pass

    def draw(self):
        self.background.draw(640, 360)
        for c, rw, i, j in self.draw_list:
            # tiles.png는 4x4 칸이고, 그림 줄 rw는 위에서부터 센다
            self.tiles.clip_draw(c * TILE, (3 - rw) * TILE, TILE, TILE,
                                 self.left(i) + TILE // 2, self.bottom(j) + TILE // 2)
