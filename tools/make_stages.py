"""stages/*.json을 만든다: python tools/make_stages.py [출력 폴더, 기본 stages/]"""
import json, os, sys

W, H = 40, 23
FLOOR = 18   # 바닥 윗줄. 서 있는 칸은 j=17


class Room:
    def __init__(self):
        self.g = [['.'] * W for _ in range(H)]
        self.fill(0, 0, W - 1, 1)
        self.fill(0, 0, 0, H - 1)
        self.fill(W - 1, 0, W - 1, H - 1)
        self.fill(1, FLOOR, W - 2, H - 1)
        self.pedals, self.doors, self.movers = [], [], []

    def fill(self, i0, j0, i1, j1, ch='#'):
        for j in range(j0, j1 + 1):
            for i in range(i0, i1 + 1):
                self.g[j][i] = ch

    def door(self, kind, i, pedals, need_all=False):
        """바닥에 선 세 칸 높이 문. 위쪽은 천장까지 벽으로 막는다. need_all이면 발판을 모두 밟아야 한다"""
        self.fill(i, 2, i, FLOOR - 4)
        d = {'kind': kind, 'at': [i, FLOOR - 1], 'pedals': pedals}
        if need_all:
            d['all'] = True
        self.doors.append(d)

    def pedal(self, pid, color, i, j=FLOOR - 1):
        self.pedals.append({'id': pid, 'color': color, 'at': [i, j]})

    def save(self, path, number, name, ghosts, start, exit_):
        self.g[start[1]][start[0]] = 'P'
        self.g[exit_[1]][exit_[0]] = 'E'
        data = {'number': number, 'name': name, 'ghosts': ghosts,
                'map': [''.join(r) for r in self.g]}
        for k in ('pedals', 'doors', 'movers'):
            if getattr(self, k):
                data[k] = getattr(self, k)
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write('{\n')
            items = list(data.items())
            for n, (k, v) in enumerate(items):
                end = ',' if n < len(items) - 1 else ''
                if k == 'map':
                    rows = ',\n'.join(f'  "{r}"' for r in v)
                    f.write(f' "map": [\n{rows}\n ]{end}\n')
                elif isinstance(v, list) and v and isinstance(v[0], dict):
                    rows = ',\n'.join('  ' + json.dumps(x, ensure_ascii=False) for x in v)
                    f.write(f' "{k}": [\n{rows}\n ]{end}\n')
                else:
                    f.write(f' "{k}": {json.dumps(v, ensure_ascii=False)}{end}\n')
            f.write('}\n')


def main(out):
    os.makedirs(out, exist_ok=True)
    s = FLOOR - 1

    # 1. 유령이 초록 발판을 밟는 동안 문이 열린다
    r = Room()
    r.pedal('a', 'green', 11)
    r.door('green', 24, ['a'])
    r.save(os.path.join(out, 'stage01.json'), 1, '과거의 내가 문을 연다', [1, 2], (3, s), (34, s))

    # 2. 발판이 공중 발판 위에 있다. 기록체가 그 위에 올라가 멈춰 있어야 문이 열린다
    r = Room()
    r.fill(13, FLOOR - 3, 18, FLOOR - 3, '-')
    r.pedal('a', 'green', 15, FLOOR - 4)
    r.door('green', 25, ['a'])
    r.save(os.path.join(out, 'stage02.json'), 2, '멈출 곳을 정한다', [1, 2], (3, s), (34, s))

    # 3. 타이머 문은 밟은 순간부터 3초만 열린다. 혼자서는 발판에서 문까지 3초 안에 못 간다
    r = Room()
    r.pedal('a', 'timer', 2)
    r.fill(14, FLOOR - 2, 17, FLOOR - 1)
    r.door('timer', 33, ['a'])
    r.save(os.path.join(out, 'stage03.json'), 3, '3초 안에 달린다', [1, 2], (7, s), (36, s))

    # 4. 발판 하나가 초록 문은 열고 빨간 문은 닫는다. 기록체가 밟고 있다가 제때 내려와야 한다
    r = Room()
    r.pedal('a', 'red', 6)
    r.door('green', 14, ['a'])
    r.door('red', 26, ['a'])
    r.save(os.path.join(out, 'stage04.json'), 4, '문이 번갈아 열린다', [1, 2], (3, s), (34, s))

    # 5. 발판 두 개를 동시에 밟아야 열리는 문. 하나는 공중 발판 위에 있다
    r = Room()
    r.pedal('a', 'green', 2)
    r.fill(11, FLOOR - 3, 15, FLOOR - 3, '-')
    r.pedal('b', 'green', 12, FLOOR - 4)
    r.door('green', 22, ['a', 'b'], need_all=True)
    r.save(os.path.join(out, 'stage05.json'), 5, '둘이 함께 누른다', [2, 3], (7, s), (34, s))

    # 6. 기록체 1이 연 문 안쪽에 두 번째 발판이 있다. 기록체 2가 들어가 밟아 출구 문을 연다
    r = Room()
    r.pedal('a', 'green', 5)
    r.door('green', 12, ['a'])
    r.pedal('b', 'green', 16)
    r.door('green', 28, ['b'])
    r.save(os.path.join(out, 'stage06.json'), 6, '유령이 길을 이어 준다', [2, 3], (3, s), (34, s))

    # 7. 구덩이 위를 움직이는 발판이 오간다. 건너편 문은 유령이 열어 둔다
    r = Room()
    r.fill(10, FLOOR, 27, H - 1, '.')
    r.pedal('a', 'green', 2)
    r.door('green', 31, ['a'])
    r.movers.append({'path': [[10, FLOOR], [25, FLOOR]], 'period': 360, 'hold': 60})
    r.save(os.path.join(out, 'stage07.json'), 7, '떠 있는 발판에 오른다', [1, 2], (7, s), (35, s))

    # 8. 일곱 칸 높이 턱. 유령 둘을 쌓아 딛고 오른다
    r = Room()
    r.fill(28, FLOOR - 7, W - 2, FLOOR - 1)
    r.save(os.path.join(out, 'stage08.json'), 8, '나를 딛고 오른다', [2, 3], (3, s), (34, FLOOR - 8))

    # 9. 빨간 발판은 출구 문을 열지만 유령이 지나야 할 빨간 문을 닫는다
    r = Room()
    r.pedal('p', 'red', 6)
    r.pedal('g', 'green', 15)
    r.door('red', 11, ['p'])
    r.door('green', 22, ['g'])
    r.door('green', 30, ['p'])
    r.save(os.path.join(out, 'stage09.json'), 9, '과거를 지켜야 한다', [2, 3], (3, s), (35, s))

    # 10. 타이머 문, 움직이는 발판, 기록체 밟기를 모두 쓴다
    r = Room()
    r.pedal('t', 'timer', 6)
    r.door('timer', 10, ['t'])
    r.fill(13, FLOOR, 22, H - 1, '.')
    r.movers.append({'path': [[13, FLOOR], [20, FLOOR]], 'period': 400, 'hold': 100})
    r.fill(31, FLOOR - 5, W - 2, FLOOR - 1)
    r.save(os.path.join(out, 'stage10.json'), 10, '탈출정에 오른다', [2, 3], (3, s), (35, FLOOR - 6))

    for f in sorted(os.listdir(out)):
        print(f)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'stages'))
