from pico2d import close_canvas, open_canvas
import pico2d.pico2d as p2
import sdl2

import game_framework
import sound
import title_mode

WIDTH, HEIGHT = 1280, 720

open_canvas(WIDTH, HEIGHT)
sdl2.SDL_SetWindowTitle(p2.window, '10 Seconds'.encode('utf-8'))
# 반투명 사각형(어둡게 덮기, 붉은 번쩍임)이 섞여 그려지게 한다
sdl2.SDL_SetRenderDrawBlendMode(p2.renderer, sdl2.SDL_BLENDMODE_BLEND)
sound.init()
game_framework.run(title_mode)
close_canvas()
