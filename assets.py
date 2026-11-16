from pico2d import load_image
import sdl2

_images = {}


def image(name, additive=False):
    """resource 폴더 이미지를 한 번만 불러 같이 쓴다. additive면 빛처럼 더해서 그린다"""
    key = (name, additive)
    if key not in _images:
        img = load_image('resource/' + name)
        if additive:
            sdl2.SDL_SetTextureBlendMode(img.texture, sdl2.SDL_BLENDMODE_ADD)
        _images[key] = img
    return _images[key]
