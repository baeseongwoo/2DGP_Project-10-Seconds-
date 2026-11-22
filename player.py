from pico2d import draw_rectangle
from sdl2 import SDL_KEYDOWN, SDL_KEYUP, SDLK_LEFT, SDLK_RIGHT, SDLK_SPACE
from transitions import Machine

import assets
import game_world
import sound
from stage import TILE


class Player:
    # 물리 값은 모두 1프레임(1/60초) 기준 픽셀이다
    SPEED = 4.5
    GRAVITY = 0.8
    JUMP_SPEED = 13.5      # 최고 높이 약 114px, 세 칸 반
    JUMP_CUT = 0.5         # 점프 키를 일찍 떼면 위로 오르던 속도를 줄여 낮게 뛴다
    MAX_FALL = 16          # 한 칸(32px)보다 작게 둬서 바닥을 뚫지 않게 한다
    COYOTE_FRAMES = 6      # 발판 끝에서 막 떨어진 직후에도 점프를 받아 준다
    BUFFER_FRAMES = 6      # 땅에 닿기 직전에 누른 점프도 받아 준다

    W, H = 20, 66          # 충돌 상자. x는 가운데, y는 발바닥
    SPRITE_W, SPRITE_H = 48, 72
    RUN_FPS = 10
    IDLE, RUN_FIRST, RISE, FALL = 0, 1, 5, 6
    color = (241, 244, 247)   # 발판, 문 표시등에 쓰는 지금의 나의 색

    def __init__(self, stage):
        self.stage = stage
        self.image = assets.image('player.png')
        self.pressed_keys = set()
        self.respawn()

        self.machine = Machine(
            model=self,
            states=['IDLE', 'RUN', 'AIR'],
            transitions=[
                {'trigger': 'start_run', 'source': 'IDLE', 'dest': 'RUN'},
                {'trigger': 'stop_run', 'source': 'RUN', 'dest': 'IDLE'},
                {'trigger': 'take_off', 'source': ['IDLE', 'RUN'], 'dest': 'AIR'},
                # 내려앉을 때 방향키를 누르고 있으면 바로 달린다
                {'trigger': 'land', 'source': 'AIR', 'dest': 'RUN', 'conditions': 'is_moving'},
                {'trigger': 'land', 'source': 'AIR', 'dest': 'IDLE'},
            ],
            initial='IDLE',
            auto_transitions=False,
        )

    def respawn(self):
        i, j = self.stage.start
        self.x = self.stage.left(i) + TILE / 2
        self.y = self.stage.bottom(j)
        self.vx = self.vy = 0.0
        # 방향키를 누른 채로 다시 시작하면 그대로 달린다
        self.dir = int(SDLK_RIGHT in self.pressed_keys) - int(SDLK_LEFT in self.pressed_keys)
        self.face_dir = self.dir or 1
        self.on_ground = True
        self.carrier = None    # 올라타 있는 움직이는 발판이나 기록체
        self.coyote = 0
        self.jump_buffer = 0
        self.frame = 0.0
        self.record = []       # 프레임마다 (x, y, 그림 칸, 바라보는 쪽). 되감으면 기록체가 된다
        if hasattr(self, 'machine'):
            self.machine.set_state('RUN' if self.dir else 'IDLE')

    def is_moving(self):
        return self.dir != 0

    def on_enter_RUN(self):
        self.frame = 0.0

    def handle_event(self, event):
        if event.type not in (SDL_KEYDOWN, SDL_KEYUP):
            return
        if event.key == SDLK_SPACE:
            if event.type == SDL_KEYDOWN:
                self.jump_buffer = Player.BUFFER_FRAMES
            elif self.vy > 0:
                self.vy *= Player.JUMP_CUT
            return
        if event.key not in (SDLK_LEFT, SDLK_RIGHT):
            return

        if event.type == SDL_KEYDOWN:
            self.pressed_keys.add(event.key)
        else:
            self.pressed_keys.discard(event.key)
        self.dir = int(SDLK_RIGHT in self.pressed_keys) - int(SDLK_LEFT in self.pressed_keys)
        if self.dir != 0:
            self.face_dir = self.dir

        if self.state == 'IDLE' and self.dir != 0:
            self.start_run()
        elif self.state == 'RUN' and self.dir == 0:
            self.stop_run()

    def step(self, blocks, floors):
        """blocks: 막힌 상자(닫힌 문), floors: 위에서만 밟히는 것(움직이는 발판, 기록체 머리)"""
        if self.carrier is not None:
            dx, dy = self.carrier.delta()
            self.y += dy
            self.move_x(dx, blocks)

        self.coyote = Player.COYOTE_FRAMES if self.on_ground else max(0, self.coyote - 1)
        if self.jump_buffer > 0:
            self.jump_buffer -= 1
            if self.coyote > 0:
                self.vy = Player.JUMP_SPEED
                sound.play('jump')
                self.jump_buffer = self.coyote = 0

        self.vx = self.dir * Player.SPEED
        self.vy = max(self.vy - Player.GRAVITY, -Player.MAX_FALL)
        self.move_x(self.vx, blocks)
        self.move_y(blocks, floors)

        if self.on_ground and self.state == 'AIR':
            self.land()
        elif not self.on_ground and self.state != 'AIR':
            self.take_off()

        if self.state == 'RUN':
            self.frame = (self.frame + Player.RUN_FPS / 60) % 4

    def save_frame(self):
        self.record.append((self.x, self.y, self.sprite_frame(), self.face_dir))

    def rows_covered(self):
        st = self.stage
        return range(st.row(self.y + self.H - 0.01), st.row(self.y + 0.01) + 1)

    def cols_covered(self):
        st = self.stage
        return range(st.col(self.x - self.W / 2 + 0.01), st.col(self.x + self.W / 2 - 0.01) + 1)

    def move_x(self, dx, blocks):
        st = self.stage
        self.x += dx
        if dx > 0:
            i = st.col(self.x + self.W / 2 - 0.01)
            if any(st.is_wall(i, j) for j in self.rows_covered()):
                self.x = st.left(i) - self.W / 2
        elif dx < 0:
            i = st.col(self.x - self.W / 2)
            if any(st.is_wall(i, j) for j in self.rows_covered()):
                self.x = st.left(i + 1) + self.W / 2
        for l, b, r, t in blocks:
            if self.overlaps(l, b, r, t):
                if dx > 0:
                    self.x = l - self.W / 2
                elif dx < 0:
                    self.x = r + self.W / 2

    def overlaps(self, l, b, r, t):
        return (self.x - self.W / 2 < r and l < self.x + self.W / 2 and
                self.y < t and b < self.y + self.H)

    def move_y(self, blocks, floors):
        st = self.stage
        prev_bottom = self.y
        self.y += self.vy
        self.on_ground = False
        self.carrier = None
        left, right = self.x - self.W / 2, self.x + self.W / 2
        if self.vy < 0:
            land, on = None, None
            j = st.row(self.y)
            top = st.bottom(j) + TILE
            # 통과 발판은 위에서 내려올 때만 밟힌다
            if any(st.is_wall(i, j) or (st.is_platform(i, j) and prev_bottom >= top - 0.01)
                   for i in self.cols_covered()):
                land = top
            for l, b, r, t in blocks:
                if l < right and left < r and prev_bottom >= t - 0.01 and self.y < t:
                    land = t if land is None else max(land, t)
            for f in floors:
                l, t, r = f.get_top()
                if l < right and left < r and prev_bottom >= t - 0.01 and self.y < t:
                    if land is None or t > land:
                        land, on = t, f
            if land is not None:
                self.y = land
                self.vy = 0.0
                self.on_ground = True
                self.carrier = on
        elif self.vy > 0:
            j = st.row(self.y + self.H)
            if any(st.is_wall(i, j) for i in self.cols_covered()):
                self.y = st.bottom(j) - self.H
                self.vy = 0.0
            for l, b, r, t in blocks:
                if self.overlaps(l, b, r, t):
                    self.y = b - self.H
                    self.vy = 0.0

    def push_out(self, l, b, r, t):
        """닫히는 문이 몸과 겹치면 가까운 쪽으로 밀어낸다"""
        if self.overlaps(l, b, r, t):
            if self.x < (l + r) / 2:
                self.x = l - self.W / 2
            else:
                self.x = r + self.W / 2

    def get_bb(self):
        return self.x - self.W / 2, self.y, self.x + self.W / 2, self.y + self.H

    def sprite_frame(self):
        if self.state == 'RUN':
            return Player.RUN_FIRST + int(self.frame)
        if self.state == 'AIR':
            return Player.RISE if self.vy > 0 else Player.FALL
        return Player.IDLE

    def update(self):
        pass

    def draw(self):
        draw_body(self.image, self.x, self.y, self.sprite_frame(), self.face_dir)
        if game_world.show_bb:
            draw_rectangle(*self.get_bb())


def draw_body(image, x, y, frame, face_dir):
    w, h = Player.SPRITE_W, Player.SPRITE_H
    # 그림의 발바닥이 맨 아래에서 한 줄 위에 있어서 1px 내려 그린다
    x, y = round(x) + game_world.ox, round(y) + h // 2 - 1 + game_world.oy
    if face_dir == 1:
        image.clip_draw(frame * w, 0, w, h, x, y)
    else:
        image.clip_composite_draw(frame * w, 0, w, h, 0, 'h', x, y, w, h)
