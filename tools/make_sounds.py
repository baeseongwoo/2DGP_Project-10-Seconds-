"""배경음악과 효과음을 파형 합성으로 직접 만든다: python tools/make_sounds.py [출력 폴더, 기본 resource/]

- music_loop.wav: 정확히 10초(120BPM 4/4 다섯 마디). 회차가 시작될 때마다 처음부터 다시 튼다.
  마지막 3초(7초부터)는 높은 음과 빠른 하이햇으로 급해진다.
- 효과음: 점프, 발판, 문, 되감기, 시간 붕괴, 클리어.
외부 음원은 쓰지 않는다. 무작위 값은 시드를 고정해 언제나 같은 파일이 나온다.
"""
import math, os, random, struct, sys, wave

RATE = 44100
HERE = os.path.dirname(os.path.abspath(__file__))


def note(name):
    """'A3' 같은 음 이름 -> 주파수"""
    names = {'C': -9, 'D': -7, 'E': -5, 'F': -4, 'G': -2, 'A': 0, 'B': 2}
    semis = names[name[0]] + (1 if '#' in name else 0) + (int(name[-1]) - 4) * 12
    return 440.0 * 2 ** (semis / 12)


def square(phase, duty=0.5):
    return 1.0 if (phase % 1.0) < duty else -1.0


def triangle(phase):
    p = phase % 1.0
    return 4 * p - 1 if p < 0.5 else 3 - 4 * p


def env(t, length, attack=0.005, release=0.05):
    if t < attack:
        return t / attack
    if t > length - release:
        return max(0.0, (length - t) / release)
    return 1.0


def mix(buf, start, samples, gain=1.0):
    for i, v in enumerate(samples):
        k = start + i
        if 0 <= k < len(buf):
            buf[k] += v * gain


def tone(freq, length, wave_fn=square, duty=0.5, decay=0.0, attack=0.005, release=0.03):
    n = int(length * RATE)
    out = []
    phase = 0.0
    for i in range(n):
        t = i / RATE
        phase += freq / RATE
        v = wave_fn(phase, duty) if wave_fn is square else wave_fn(phase)
        out.append(v * env(t, length, attack, release) * math.exp(-decay * t))
    return out


def noise(length, decay, seed, lowpass=0.0):
    rnd = random.Random(seed)
    out, last = [], 0.0
    for i in range(int(length * RATE)):
        v = rnd.uniform(-1, 1)
        last = last * lowpass + v * (1 - lowpass)
        out.append(last * math.exp(-decay * i / RATE))
    return out


def sweep(f0, f1, length, wave_fn=square, curve=1.0, decay=0.0):
    n = int(length * RATE)
    out, phase = [], 0.0
    for i in range(n):
        u = i / n
        f = f0 + (f1 - f0) * (u ** curve)
        phase += f / RATE
        v = wave_fn(phase) if wave_fn is not square else square(phase, 0.5)
        out.append(v * env(i / RATE, length, 0.003, 0.03) * math.exp(-decay * i / RATE))
    return out


def save(path, buf, peak=0.85):
    m = max(1e-9, max(abs(v) for v in buf))
    scale = peak / m
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b''.join(struct.pack('<h', int(max(-1, min(1, v * scale)) * 32767)) for v in buf))


def music():
    bpm = 120
    beat = 60 / bpm                 # 0.5초
    total = 20 * beat               # 10초
    buf = [0.0] * int(total * RATE)
    chords = [('A2', ['A4', 'C5', 'E5']), ('F2', ['F4', 'A4', 'C5']), ('C3', ['C4', 'E4', 'G4']),
              ('G2', ['G4', 'B4', 'D5']), ('E2', ['E4', 'G#4', 'B4'])]
    for bar, (root, arp) in enumerate(chords):
        t0 = bar * 4 * beat
        # 베이스: 8분음표 옥타브
        for k in range(8):
            f = note(root) * (2 if k % 2 else 1)
            mix(buf, int((t0 + k * beat / 2) * RATE), tone(f, beat / 2 * 0.9, square, 0.5, decay=3), 0.30)
        # 아르페지오: 16분음표, 7초 뒤에는 한 옥타브 위
        for k in range(16):
            t = t0 + k * beat / 4
            f = note(arp[k % 3]) * (2 if t >= 7.0 else 1)
            mix(buf, int(t * RATE), tone(f, beat / 4 * 0.8, square, 0.25, decay=8), 0.13)
        # 킥(정박), 하이햇(엇박, 7초 뒤에는 16분)
        for k in range(4):
            t = t0 + k * beat
            mix(buf, int(t * RATE), sweep(150, 40, 0.12, triangle, 0.5, decay=20), 0.55)
            hats = (1, 3) if t < 7.0 else (1, 2, 3)
            for h in hats:
                mix(buf, int((t + h * beat / 4) * RATE), noise(0.04, 60, seed=bar * 10 + k * 4 + h, lowpass=0.2), 0.10)
    # 1초마다 시계 초침 소리
    for s in range(10):
        mix(buf, int(s * RATE), tone(note('E6'), 0.025, triangle, decay=80), 0.18)
    return buf


def sfx_jump():
    return sweep(320, 720, 0.13, square, 0.6, decay=10)


def sfx_pedal():
    buf = [0.0] * int(0.14 * RATE)
    mix(buf, 0, noise(0.03, 80, seed=7, lowpass=0.5), 0.5)
    mix(buf, int(0.02 * RATE), tone(note('A5'), 0.1, square, 0.25, decay=25), 0.5)
    return buf


def sfx_door():
    buf = [0.0] * int(0.32 * RATE)
    mix(buf, 0, sweep(90, 160, 0.3, square, 1.0, decay=4), 0.35)
    mix(buf, 0, noise(0.3, 8, seed=11, lowpass=0.85), 0.5)
    return buf


def sfx_rewind():
    """되감기: 거꾸로 감기는 테이프처럼 높은 음에서 빠르게 떨어지며 떨린다 (연출 28프레임 = 0.47초)"""
    n = int(0.47 * RATE)
    out, phase = [], 0.0
    for i in range(n):
        u = i / n
        f = 1400 * (1 - u) ** 1.6 + 120
        f *= 1 + 0.25 * math.sin(2 * math.pi * 18 * i / RATE)
        phase += f / RATE
        out.append(triangle(phase) * env(i / RATE, 0.47, 0.01, 0.08))
    return out


def sfx_collapse():
    buf = [0.0] * int(0.9 * RATE)
    mix(buf, 0, sweep(110, 30, 0.8, square, 0.7, decay=3), 0.5)
    mix(buf, 0, noise(0.6, 5, seed=23, lowpass=0.6), 0.7)
    rnd = random.Random(5)
    for k in range(6):          # 글리치: 짧게 끊기는 높은 음
        mix(buf, int(rnd.uniform(0.02, 0.5) * RATE), tone(rnd.uniform(800, 2400), 0.03, square, 0.5), 0.15)
    return buf


def sfx_clear():
    buf = [0.0] * int(1.0 * RATE)
    for k, name in enumerate(['C5', 'E5', 'G5', 'C6']):
        mix(buf, int(k * 0.09 * RATE), tone(note(name), 0.5 if k == 3 else 0.18, square, 0.25, decay=4), 0.4)
        mix(buf, int(k * 0.09 * RATE), tone(note(name) / 2, 0.2, triangle, decay=6), 0.3)
    return buf


def main(out):
    os.makedirs(out, exist_ok=True)
    save(os.path.join(out, 'music_loop.wav'), music(), peak=0.6)
    for name, fn in (('jump', sfx_jump), ('pedal', sfx_pedal), ('door', sfx_door), ('rewind', sfx_rewind),
                     ('collapse', sfx_collapse), ('clear', sfx_clear)):
        save(os.path.join(out, f'sfx_{name}.wav'), fn(), peak=0.7)
    for f in sorted(os.listdir(out)):
        if f.endswith('.wav'):
            print(f, os.path.getsize(os.path.join(out, f)))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'resource'))
