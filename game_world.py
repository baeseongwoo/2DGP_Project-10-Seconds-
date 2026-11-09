# 0: 배경과 타일, 1: 오브젝트, 2: 캐릭터
world = [[], [], []]

show_bb = False   # F1로 충돌 상자를 보이게 한다


def collide(a, b):
    la, ba, ra, ta = a.get_bb()
    lb, bb, rb, tb = b.get_bb()
    return la < rb and lb < ra and ba < tb and bb < ta


def add_object(o, depth):
    world[depth].append(o)


def remove_object(o):
    for layer in world:
        if o in layer:
            layer.remove(o)
            return


def clear():
    for layer in world:
        layer.clear()


def update():
    for layer in world:
        for o in layer:
            o.update()


def render():
    for layer in world:
        for o in layer:
            o.draw()
