STAGE, OBJECT, GHOST, PLAYER, FX = range(5)
world = [[] for _ in range(5)]

show_bb = False   # F1로 충돌 상자를 보이게 한다
ox = oy = 0       # 화면 흔들림. 그릴 때 모든 좌표에 더한다


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
        for o in layer[:]:   # 이펙트가 끝나면 스스로 빠지므로 복사본을 돈다
            o.update()


def render():
    for layer in world:
        for o in layer:
            o.draw()
