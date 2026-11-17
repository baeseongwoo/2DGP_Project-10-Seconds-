from pico2d import Image, draw_rectangle, load_font
import pico2d.pico2d as p2
from sdl2 import SDL_Color, SDL_CreateTextureFromSurface, SDL_FreeSurface
from sdl2.sdlttf import TTF_RenderUTF8_Blended

FONT_PATHS = ['C:/Windows/Fonts/malgunbd.ttf', 'C:/Windows/Fonts/malgun.ttf']

WHITE = (241, 244, 247)
GREY = (140, 155, 175)
CYAN = (95, 224, 208)
ORANGE = (255, 159, 69)
GOLD = (255, 226, 122)
RED = (217, 70, 61)
INK = (11, 15, 22)
# 기록체 #1 마젠타, #2 바이올렛, #3 라임. 문(초록, 빨강, 주황)과 UI(청록) 색과 겹치지 않게 골랐다
RECORD = [(255, 92, 168), (166, 140, 255), (216, 242, 107)]

_fonts = {}
_texts = {}


def font(size):
    if size not in _fonts:
        for path in FONT_PATHS:
            try:
                _fonts[size] = load_font(path, size)
                break
            except IOError:
                continue
    return _fonts[size]


def _texture(s, size, color):
    key = (s, size, color)
    if key not in _texts:
        if len(_texts) > 600:   # 남은 시간 글자처럼 매번 바뀌는 글자가 쌓이지 않게 비운다
            _texts.clear()
        surface = TTF_RenderUTF8_Blended(font(size).font, s.encode('utf-8'), SDL_Color(*color))
        texture = SDL_CreateTextureFromSurface(p2.renderer, surface)
        SDL_FreeSurface(surface)
        _texts[key] = Image(texture)
    return _texts[key]


def text(s, x, y, size=20, color=WHITE, align='left', shadow=True):
    """y는 글자 줄의 가운데. align은 x를 왼쪽, 가운데, 오른쪽 중 어디로 볼지 정한다"""
    if not s:
        return
    img = _texture(s, size, color)
    left = x - img.w / 2 if align == 'center' else x - img.w if align == 'right' else x
    if shadow:
        _texture(s, size, INK).draw(left + img.w / 2 + 2, y - 2)
    img.draw(left + img.w / 2, y)


def text_width(s, size=20):
    return _texture(s, size, WHITE).w if s else 0


def box(x1, y1, x2, y2, color, alpha=255):
    draw_rectangle(x1, y1, x2, y2, *color, alpha, filled=True)


def frame(x1, y1, x2, y2, color, width=2):
    for k in range(width):
        draw_rectangle(x1 + k, y1 + k, x2 - k, y2 - k, *color)
