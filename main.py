from pico2d import close_canvas, open_canvas

import game_framework
import play_mode

WIDTH, HEIGHT = 1280, 720

open_canvas(WIDTH, HEIGHT)
game_framework.run(play_mode)
close_canvas()
