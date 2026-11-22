"""배경음악과 효과음. 소리 장치가 없으면 조용히 넘어간다.

음악은 정확히 10초라서 회차가 시작될 때마다 처음부터 다시 틀면 회차와 박자가 맞는다.
"""
from pico2d import load_music, load_wav

MUSIC_VOLUME = 48
SFX_VOLUME = 64
SFX = ('jump', 'pedal', 'door', 'rewind', 'collapse', 'clear')

music = None
sfx = {}
muted = False


def init():
    global music
    if music is not None or sfx:
        return
    try:
        music = load_music('resource/music_loop.wav')
        for name in SFX:
            sfx[name] = load_wav(f'resource/sfx_{name}.wav')
            sfx[name].set_volume(SFX_VOLUME)
    except IOError:
        music = None
        sfx.clear()


def play_music(loop=False):
    if music and not muted:
        music.set_volume(MUSIC_VOLUME)
        music.repeat_play() if loop else music.play(1)


def stop_music():
    if music:
        music.stop()


def play(name):
    if name in sfx and not muted:
        sfx[name].play()


def toggle_mute():
    global muted
    muted = not muted
    if muted:
        stop_music()
