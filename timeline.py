"""타임라인 트랙, 인과선, 붕괴 예고 (PRD 7.2).

- 트랙: 화면 아래에 회차별 줄을 긋고, 발판을 밟은 구간과 문을 지난 순간을 표시한다.
- 인과선: 발판을 누르는 몸에서 그 발판이 움직이는 문까지 몸의 색으로 점선을 잇는다.
- 붕괴 예고: 기록체가 녹화될 때는 열려 있던 문이 지금은 닫혀 있고, 0.5초 안에 그 문에 닿으면 경고한다.
  원래부터 나중에 열리기로 된 문에는 경고하지 않으므로, 지금의 내가 과거를 바꾼 경우에만 뜬다.
"""
from pico2d import draw_line

import game_world
import ui

ROUND_FRAMES = 600
WARN_FRAMES = 30
X0, X1 = 210, 1070          # 트랙의 0초와 10초 위치
ROW_Y0, ROW_GAP, ROW_H = 46, 16, 10

visible = True               # F2로 숨긴다


def overlaps(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def body_bb(x, y, w, h):
    return x - w / 2, y, x + w / 2, y + h


def analyze(record, w, h, pedals, doors, stays=False):
    """기록에서 발판을 밟은 구간 [(시작, 끝)]과 문을 지난 프레임 목록을 뽑는다.
    stays면 기록이 끝난 뒤에도 그 자리에 서 있는 기록체라서, 마지막에 밟고 있던 발판은 10초까지 계속 밟는다"""
    presses, passes = [], []
    start = None
    inside = [False] * len(doors)
    for t, (x, y, *_rest) in enumerate(record):
        bb = body_bb(x, y, w, h)
        on = any(overlaps(bb, p.get_bb()) for p in pedals)
        if on and start is None:
            start = t
        elif not on and start is not None:
            presses.append((start, t))
            start = None
        for k, d in enumerate(doors):
            now = overlaps(bb, d.get_bb())
            if now and not inside[k]:
                passes.append(t)
            inside[k] = now
    if start is not None:
        presses.append((start, ROUND_FRAMES if stays else len(record)))
    return presses, passes


def warnings(ghosts, doors, clock):
    """[(기록체, 문)] 지금 과거와 어긋나 곧 붕괴할 짝"""
    out = []
    for g in ghosts:
        hist = g.door_history
        was_open = hist[min(clock, len(hist) - 1)] if hist else ()
        for k, d in enumerate(doors):
            if not d.is_closed() or k >= len(was_open) or not was_open[k]:
                continue
            for t in range(clock, clock + WARN_FRAMES):
                x, y = g.record[min(t, len(g.record) - 1)][:2]
                if overlaps(body_bb(x, y, g.W, g.H), d.get_bb()):
                    out.append((g, d))
                    break
    return out


def dotted(x1, y1, x2, y2, color, dash=6, phase=0):
    """점선 (두 줄로 그려 굵게)"""
    dx, dy = x2 - x1, y2 - y1
    n = max(1, int((dx * dx + dy * dy) ** 0.5 // dash))
    for k in range(phase % 2, n, 2):
        a, b = k / n, min(1.0, (k + 1) / n)
        for o in (0, 1):
            draw_line(x1 + dx * a + o, y1 + dy * a, x1 + dx * b + o, y1 + dy * b, *color, 220)


def draw_causal(pedals, doors, clock, warns):
    ox, oy = game_world.ox, game_world.oy
    for p in pedals:
        if not p.presser:
            continue
        b = p.presser
        for d in doors:
            if p in d.pedals:
                dotted(b.x + ox, b.y + 40 + oy, d.cx + ox, d.bottom + d.H + 4 + oy, p.by, phase=clock // 6)
    blink = (clock // 10) % 2 == 0      # 초당 3번
    for g, d in warns:
        if blink:
            dotted(g.x + ox, g.y + 40 + oy, d.cx + ox, d.bottom + d.H // 2 + oy, ui.RED, dash=4)
            ui.text('!', g.x + ox, g.y + g.H + 38 + oy, 26, ui.RED, align='center')


def x_at(frame):
    return X0 + (X1 - X0) * min(frame, ROUND_FRAMES) / ROUND_FRAMES


def draw_track(row, color, presses, passes, end, warn, clock, label):
    y = ROW_Y0 + row * ROW_GAP
    ui.text(label, X0 - 12, y + ROW_H / 2, 14, color, align='right', shadow=False)
    ui.box(X0, y, X1, y + ROW_H, ui.RED if warn and (clock // 10) % 2 == 0 else (32, 40, 54), 230)
    for a, b in presses:
        ui.box(x_at(a), y + 2, max(x_at(a) + 2, x_at(b)), y + ROW_H - 2, color)
    for t in passes:
        ui.box(x_at(t) - 1, y - 2, x_at(t) + 1, y + ROW_H + 2, ui.WHITE)
    if end < ROUND_FRAMES:
        # 기록이 끝난 뒤에는 그 자리에 서 있다: 옅게 칠한다
        ui.box(x_at(end), y + 4, X1, y + ROW_H - 4, color, 90)


def draw_panel(ghosts, player_track, clock, warns):
    if not visible:
        return
    rows = len(ghosts) + 1
    top = ROW_Y0 + rows * ROW_GAP + 4
    ui.box(X0 - 60, ROW_Y0 - 10, X1 + 14, top + 6, ui.INK, 170)
    for s in range(0, 11):
        x = x_at(s * 60)
        ui.box(x, top, x + 1, top + 5, ui.GREY)
    presses, passes = player_track
    draw_track(0, (241, 244, 247), presses, passes, ROUND_FRAMES, False, clock, '나')
    warned = {g for g, _ in warns}
    for k, g in enumerate(ghosts, 1):
        draw_track(k, g.color, g.presses, g.passes, len(g.record), g in warned, clock, f'#{g.number}')
    x = x_at(clock)
    ui.box(x - 1, ROW_Y0 - 6, x + 1, top + 6, ui.ORANGE if clock >= ROUND_FRAMES - 180 else ui.CYAN)
