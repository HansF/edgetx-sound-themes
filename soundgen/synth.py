"""DSP building blocks: oscillators, envelopes, filters, drums, sound-effect generators, FX.

Everything works on float64 numpy arrays at SR. Oscillators take a per-sample
frequency array so pitch bends and vibrato come for free.
"""
import numpy as np
from scipy import signal

SR = 48000
rng = np.random.default_rng(1985)


def reseed(seed):
    global rng
    rng = np.random.default_rng(seed)


def midi_hz(p):
    return 440.0 * 2 ** ((np.asarray(p, float) - 69) / 12)


def n_samples(dur):
    return max(1, int(round(dur * SR)))


def t_axis(n):
    return np.arange(n) / SR


def phase(f):
    return np.cumsum(np.asarray(f, float) / SR) % 1.0


# ---------------------------------------------------------------- oscillators

def _blep(t, dt):
    y = np.zeros_like(t)
    m = t < dt
    x = t[m] / dt[m]
    y[m] = x + x - x * x - 1
    m = t > 1 - dt
    x = (t[m] - 1) / dt[m]
    y[m] = x * x + x + x + 1
    return y


def saw(f):
    f = np.asarray(f, float)
    t, dt = phase(f), np.clip(f / SR, 1e-6, 0.5)
    return 2 * t - 1 - _blep(t, dt)


def pulse(f, duty=0.5):
    f = np.asarray(f, float)
    t, dt = phase(f), np.clip(f / SR, 1e-6, 0.5)
    t2 = (t + 1 - duty) % 1
    y = (2 * t - 1 - _blep(t, dt)) - (2 * t2 - 1 - _blep(t2, dt))
    return -y  # zero-mean, high for the first `duty` of the cycle


def square_raw(f, duty=0.5):
    """Naive 1-bit square (PC speaker / aliasing on purpose)."""
    return np.where(phase(f) < duty, 1.0, -1.0)


def tri_nes(f):
    p = phase(f)
    return np.round((4 * np.abs(p - 0.5) - 1) * 7.5) / 7.5


def tri(f):
    p = phase(f)
    return 4 * np.abs(p - 0.5) - 1


GB_WAVE = np.array([0, 2, 4, 6, 8, 10, 12, 14, 15, 15, 14, 13, 12, 10, 8, 6,
                    4, 3, 2, 1, 0, 0, 1, 2, 3, 5, 7, 9, 11, 13, 14, 15]) / 7.5 - 1


def wavetable(f, table=GB_WAVE):
    return table[(phase(f) * len(table)).astype(int) % len(table)]


def sine(f):
    return np.sin(2 * np.pi * phase(f))


def supersaw(f, detune=0.012, voices=5):
    f = np.asarray(f, float)
    ds = np.linspace(-detune, detune, voices)
    return sum(saw(f * (1 + d)) for d in ds) / np.sqrt(voices)


def fm(f, ratio=1.0, index=1.0, ratio2=None, index2=0.0, feedback=0.0):
    """2- or 3-operator FM (phase modulation). index may be an array (envelope)."""
    f = np.asarray(f, float)
    mod = np.sin(2 * np.pi * phase(f * ratio))
    if ratio2 is not None:
        mod = np.sin(2 * np.pi * phase(f * ratio) + index2 * np.sin(2 * np.pi * phase(f * ratio2)))
    if feedback:
        mod = mod + feedback * np.sin(2 * np.pi * phase(f * ratio) + mod)
    return np.sin(2 * np.pi * phase(f) + index * mod)


def noise(n, rate=None, metallic=False):
    """LFSR-style sample&hold noise. rate=None -> white."""
    if rate is None:
        return rng.uniform(-1, 1, n)
    hold = max(1, int(SR / rate))
    if metallic:
        src = np.tile(rng.choice([-1.0, 1.0], 93), n // (93 * hold) + 2)
    else:
        src = rng.choice([-1.0, 1.0], n // hold + 2)
    return np.repeat(src, hold)[:n]


def karplus(f0, n, damp=0.996, bright=0.5):
    """Karplus-Strong plucked string (fixed pitch), block-vectorised."""
    L = max(2, int(round(SR / f0)))
    buf = rng.uniform(-1, 1, L)
    buf = signal.lfilter([bright, 1 - bright], [1], buf)
    out = np.empty(n + L)
    out[:L] = buf
    i = L
    while i < n + L:
        k = min(L - 1, n + L - i)
        out[i:i + k] = damp * 0.5 * (out[i - L:i - L + k] + out[i - L + 1:i - L + k + 1])
        i += k
    return out[L:L + n]


# ---------------------------------------------------------------- envelopes & filters

def adsr(n, attack=0.003, decay=0.0, sustain=1.0, release=0.02, gate=None):
    """gate = samples before release starts (defaults to n - release)."""
    t = t_axis(n)
    r = min(n, int(release * SR))
    gate = n - r if gate is None else min(gate, n)
    e = np.ones(n)
    if attack > 0:
        e = np.minimum(1.0, t / attack)
    if decay > 0:
        e = e * (sustain + (1 - sustain) * np.exp(-np.maximum(0, t - attack) / decay))
    elif sustain != 1.0:
        e = e * sustain
    if r and gate < n:
        tail = e[gate - 1] if gate > 0 else 0.0
        e[gate:] = tail * np.linspace(1, 0, n - gate)
    return e


def _sos(kind, fc, q=0.707):
    fc = float(np.clip(fc, 20, SR / 2 * 0.95))
    if kind == "bp":
        bw = fc / q
        lo, hi = max(20, fc - bw / 2), min(SR / 2 * 0.95, fc + bw / 2)
        return signal.butter(2, [lo, hi], "bandpass", fs=SR, output="sos")
    return signal.butter(2, fc, {"lp": "lowpass", "hp": "highpass"}[kind], fs=SR, output="sos")


def lp(x, fc, q=0.707):
    return _swept("lp", x, fc, q)


def hp(x, fc):
    return _swept("hp", x, fc)


def bp(x, fc, q=4.0):
    return _swept("bp", x, fc, q)


def _swept(kind, x, fc, q=0.707, block=256):
    if np.ndim(fc) == 0:
        return signal.sosfilt(_sos(kind, fc, q), x)
    fc = np.asarray(fc, float)
    out = np.empty_like(x)
    zi = None
    for i in range(0, len(x), block):
        sos = _sos(kind, fc[min(i, len(fc) - 1)], q)
        if zi is None or zi.shape[0] != sos.shape[0]:
            zi = np.zeros((sos.shape[0], 2))
        out[i:i + block], zi = signal.sosfilt(sos, x[i:i + block], zi=zi)
    return out


VOWELS = {  # F1, F2, F3 (Hz)
    "a": (800, 1150, 2900), "e": (400, 1600, 2700), "i": (300, 2300, 3000),
    "o": (450, 800, 2830), "u": (325, 700, 2530), "ee": (270, 2800, 3300),
}


def formant(x, vowel="a", q=8.0):
    f1, f2, f3 = VOWELS[vowel] if isinstance(vowel, str) else vowel
    return bp(x, f1, q) + 0.6 * bp(x, f2, q) + 0.3 * bp(x, f3, q)


def formant_morph(x, vowels, q=8.0):
    """Crossfade through a list of vowels over the length of x."""
    n, k = len(x), len(vowels)
    if k == 1:
        return formant(x, vowels[0], q)
    outs = [formant(x, v, q) for v in vowels]
    pos = np.linspace(0, k - 1, n)
    y = np.zeros(n)
    for i, o in enumerate(outs):
        y += o * np.clip(1 - np.abs(pos - i), 0, 1)
    return y


# ---------------------------------------------------------------- drums

def _hit(n, decay):
    return np.exp(-t_axis(n) / decay)


def kick(style="808", vel=1.0, dur=None):
    long = {"808": 0.9, "909": 0.35, "chip": 0.15, "acoustic": 0.3, "phonk": 1.2}[style]
    n = n_samples(dur or long)
    t = t_axis(n)
    f = 45 + 110 * np.exp(-t / (0.03 if style != "chip" else 0.015))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * _hit(n, long / 2.5)
    if style == "909":
        x += noise(n) * _hit(n, 0.004) * 0.6
    if style == "phonk":
        x = np.tanh(x * 3) * 0.8
    if style == "chip":
        x = np.sign(x) * 0.8 * _hit(n, 0.04)
    return x * vel


def snare(style="808", vel=1.0):
    n = n_samples(0.25)
    t = t_axis(n)
    body = np.sin(2 * np.pi * 185 * t) * _hit(n, 0.05) + np.sin(2 * np.pi * 330 * t) * _hit(n, 0.03) * 0.5
    nz = noise(n, 9000, True) if style == "chip" else hp(noise(n), 1800)
    return (body * 0.6 + nz * _hit(n, 0.07 if style != "909" else 0.1)) * vel


def clap(vel=1.0):
    n = n_samples(0.3)
    e = np.zeros(n)
    for o in (0, 0.011, 0.022):
        i = int(o * SR)
        e[i:] += _hit(n - i, 0.008 if o < 0.02 else 0.09)
    return bp(noise(n), 1200, 1.5) * e * 2 * vel


def hat(open_=False, vel=1.0, chip=False):
    n = n_samples(0.35 if open_ else 0.06)
    if chip:
        src = noise(n, 20000, True)
    else:
        t = t_axis(n)
        src = sum(np.sign(np.sin(2 * np.pi * f * t)) for f in (205.3, 304.4, 369.6, 522.7, 540, 800))
        src = hp(src + noise(n) * 2, 7000)
    return src * _hit(n, 0.12 if open_ else 0.018) * 0.5 * vel


def cowbell(vel=1.0):
    n = n_samples(0.35)
    t = t_axis(n)
    x = square_raw(np.full(n, 587.0)) + square_raw(np.full(n, 845.0))
    return bp(x, 700, 2.0) * (_hit(n, 0.02) * 0.6 + _hit(n, 0.12) * 0.4) * vel


def crash(vel=1.0):
    n = n_samples(1.2)
    return hp(noise(n), 4000) * _hit(n, 0.35) * 0.6 * vel


def tom(pitch=110, vel=1.0):
    n = n_samples(0.35)
    t = t_axis(n)
    f = pitch * (1 + 0.5 * np.exp(-t / 0.04))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * _hit(n, 0.12) * vel


def clave(vel=1.0):
    n = n_samples(0.08)
    return np.sin(2 * np.pi * 2500 * t_axis(n)) * _hit(n, 0.012) * vel


def shaker(vel=1.0):
    n = n_samples(0.12)
    e = np.sin(np.pi * np.linspace(0, 1, n)) ** 2
    return hp(noise(n), 5000) * e * 0.5 * vel


def drum(note, style="808", vel=1.0, dur=None):
    chip = style == "chip"
    table = {
        35: lambda: kick(style, vel, dur), 36: lambda: kick(style, vel, dur),
        37: lambda: clave(vel) * 0.6, 38: lambda: snare(style, vel), 40: lambda: snare(style, vel),
        39: lambda: clap(vel), 42: lambda: hat(False, vel, chip), 44: lambda: hat(False, vel, chip),
        46: lambda: hat(True, vel, chip), 49: lambda: crash(vel), 57: lambda: crash(vel),
        51: lambda: hat(True, vel * 0.6, chip), 56: lambda: cowbell(vel),
        41: lambda: tom(80, vel), 45: lambda: tom(110, vel), 47: lambda: tom(140, vel),
        50: lambda: tom(180, vel), 75: lambda: clave(vel), 70: lambda: shaker(vel),
        54: lambda: shaker(vel),
    }
    return table.get(int(note), lambda: snare(style, vel))()


# ---------------------------------------------------------------- effects

def reverb(x, size=1.0, wet=0.3, predelay=0.01, damp=6000, gate=0.0):
    n = n_samples(size)
    ir = rng.standard_normal(n) * np.exp(-t_axis(n) / (size / 6))
    ir = lp(ir, damp)
    if gate:
        ir[n_samples(gate):] *= np.exp(-t_axis(n - n_samples(gate)) / 0.01)
    ir = np.concatenate([np.zeros(n_samples(predelay)), ir])
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-12
    y = signal.fftconvolve(x, ir)
    return np.pad(x, (0, len(y) - len(x))) * (1 - wet * 0.5) + y * wet * 0.5


def echo(x, delay=0.15, feedback=0.4, repeats=4, tone=5000):
    out = np.pad(x, (0, n_samples(delay * repeats)))
    tap = x
    for i in range(1, repeats + 1):
        tap = lp(tap, tone) * feedback
        o = n_samples(delay * i)
        out[o:o + len(tap)] += tap
    return out


def chorus(x, depth=0.003, rate=0.8, mix_=0.5):
    n = len(x)
    t = t_axis(n)
    d = (0.012 + depth * np.sin(2 * np.pi * rate * t)) * SR
    idx = np.arange(n) - d
    y = np.interp(idx, np.arange(n), x, left=0.0)
    return x * (1 - mix_) + y * mix_


def wobble(x, depth=0.004, rate=0.6, flutter=0.0006):
    """Tape wow & flutter via time warp."""
    n = len(x)
    t = t_axis(n)
    off = depth * np.sin(2 * np.pi * rate * t) + flutter * np.sin(2 * np.pi * 11 * t)
    return np.interp(np.arange(n) - off * SR, np.arange(n), x, left=0.0)


def bitcrush(x, bits=6, hold=3):
    y = np.repeat(x[::hold], hold)[:len(x)]
    q = 2 ** (bits - 1)
    return np.round(y * q) / q


def drive(x, amount=3.0):
    return np.tanh(x * amount) / np.tanh(amount)


def crackle(n, density=30, level=0.3):
    y = lp(noise(n), 3000) * 0.04
    pops = rng.random(n) < density / SR
    y[pops] += rng.uniform(-1, 1, pops.sum())
    return y * level


def telephone(x):
    return bp(x, 1400, 1.1)


# ---------------------------------------------------------------- sound-effect generators
# Each takes (dur, pitch_hz, vel) and returns audio. Used through "fx:<name>" instruments.

def fx_vineboom(dur, f, vel):
    n = n_samples(max(dur, 0.9))
    t = t_axis(n)
    fr = f * 0.9 + f * 1.4 * np.exp(-t / 0.05)
    body = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / 0.35)
    thump = lp(noise(n), 400) * np.exp(-t / 0.03)
    x = drive(body + thump * 0.8, 2.5)
    return reverb(x, 1.2, 0.35)[:n + n_samples(0.4)] * vel


def fx_airhorn(dur, f, vel):
    n = n_samples(dur)
    ff = np.full(n, f) * (1 + 0.01 * np.sin(2 * np.pi * 5 * t_axis(n)))
    ff[: n_samples(0.03)] *= np.linspace(0.85, 1, n_samples(0.03))
    x = sum(saw(ff * r) for r in (1, 1.005, 1.5 * 0.998, 2.01)) + pulse(ff, 0.3)
    x = drive(bp(x, 1400, 0.6) * 1.5, 2.0)
    return x * adsr(n, 0.01, release=0.04) * vel


def fx_scratch(dur, f, vel):
    n = n_samples(dur)
    t = t_axis(n)
    speed = np.sin(2 * np.pi * (2.5 / dur) * t * dur / 1.0)
    src = saw(np.abs(speed) * f * 3 + 30) * 0.6 + bp(noise(n), 1500, 1.0)
    return bp(src, 900 + 1600 * np.abs(speed), 1.5) * np.abs(speed) ** 0.5 * vel


def fx_bonk(dur, f, vel):
    n = n_samples(0.35)
    t = t_axis(n)
    fr = f * (1 + 1.5 * np.exp(-t / 0.01))
    x = fm(fr, 1.41, 3 * np.exp(-t / 0.03)) * np.exp(-t / 0.08)
    return (x + bp(noise(n), 2500, 3) * np.exp(-t / 0.01)) * vel


def fx_modem(dur, f, vel):
    n = n_samples(dur)
    t = t_axis(n)
    segs = [
        (0.00, 0.18, lambda tt: np.sin(2 * np.pi * 2100 * tt)),
        (0.18, 0.30, lambda tt: np.sign(np.sin(2 * np.pi * 980 * tt)) * 0.5 + np.sin(2 * np.pi * 1180 * tt) * 0.5),
        (0.30, 0.45, lambda tt: np.sin(2 * np.pi * (1650 + 200 * np.sign(np.sin(2 * np.pi * 150 * tt))) * tt)),
        (0.45, 10.0, lambda tt: bp(noise(len(tt)), 1800, 0.8) * 1.5 + np.sin(2 * np.pi * 2400 * tt) * 0.3),
    ]
    x = np.zeros(n)
    for a, b, g in segs:
        i, j = n_samples(a * dur / 0.9), min(n, n_samples(b * dur / 0.9))
        if i < j:
            x[i:j] = g(t[i:j])
    return telephone(x) * 1.5 * vel


def fx_kaching(dur, f, vel):
    n = n_samples(0.7)
    t = t_axis(n)
    bell = sum(np.sin(2 * np.pi * f * r * t) * np.exp(-t / d) * a
               for r, d, a in ((1, 0.35, 1), (2.76, 0.2, 0.5), (5.4, 0.1, 0.3)))
    bell[: n_samples(0.08)] = 0
    rattle = np.zeros(n)
    for k in range(6):
        i = n_samples(0.012 * k + rng.uniform(0, 0.006))
        m = n_samples(0.02)
        rattle[i:i + m] += bp(noise(m), 5000, 2) * np.exp(-t_axis(m) / 0.004)
    drawer = lp(noise(n), 900) * np.exp(-np.maximum(0, t - 0.05) / 0.04) * (t > 0.05) * 0.4
    return (bell * 0.6 + rattle + drawer) * vel


def fx_click(dur, f, vel):
    """Ratchet: roller-coaster chain lift. f sets click rate (Hz)."""
    n = n_samples(dur)
    x = np.zeros(n)
    step = max(1, int(SR / max(f, 1)))
    m = n_samples(0.012)
    c = bp(noise(m), 3200, 2.5) * np.exp(-t_axis(m) / 0.002) + np.sin(2 * np.pi * 900 * t_axis(m)) * np.exp(-t_axis(m) / 0.004)
    for i in range(0, n - m, step):
        x[i:i + m] += c
    return x * vel


def fx_scream(dur, f, vel):
    """Crowd 'wheee' on a roller coaster: many formant voices, pitch arcs down."""
    n = n_samples(dur)
    t = t_axis(n) / dur
    x = np.zeros(n)
    for k in range(7):
        base = f * rng.uniform(0.8, 1.3)
        ff = base * (1.25 - 0.45 * t) * (1 + 0.02 * np.sin(2 * np.pi * rng.uniform(5, 8) * t_axis(n)))
        x += formant(saw(ff), rng.choice(["a", "i", "ee", "e"]), 6)
    x += bp(noise(n), 2500, 0.8) * 0.3
    return x * np.sin(np.pi * np.clip(t * 1.2, 0, 1)) * vel * 0.5


def fx_whoosh(dur, f, vel):
    n = n_samples(dur)
    t = t_axis(n) / dur
    fc = f * (0.4 + 3 * np.sin(np.pi * t))
    return bp(noise(n), fc, 1.5) * np.sin(np.pi * t) ** 1.5 * 2 * vel


def fx_laser(dur, f, vel):
    n = n_samples(dur)
    t = t_axis(n) / dur
    return pulse(f * 4 * (0.12 ** t), 0.3) * (1 - t) ** 0.5 * vel


def fx_klaxon(dur, f, vel):
    n = n_samples(dur)
    t = t_axis(n)
    ff = f * (0.7 + 0.3 * np.minimum(1, t / 0.06))
    x = pulse(ff, 0.5) + saw(ff * 1.498) * 0.6
    return bp(x, 1100, 0.9) * adsr(n, 0.005, release=0.03) * 2 * vel


def fx_glitch(dur, f, vel):
    n = n_samples(dur)
    src = np.concatenate([saw(np.full(n, f)), noise(n, 4000), pulse(np.full(n, f * 2), 0.12)])
    out = np.zeros(n)
    i = 0
    while i < n:
        seg = int(rng.choice([0.008, 0.015, 0.03, 0.06]) * SR)
        s = int(rng.integers(0, len(src) - seg))
        rep = int(rng.integers(1, 4))
        chunk = np.tile(src[s:s + seg // rep], rep)[:seg]
        out[i:i + seg] = chunk[: n - i] * rng.choice([1, 1, 0.5, 0])
        i += seg
    return bitcrush(out, 5, 2) * vel


def fx_riser(dur, f, vel):
    n = n_samples(dur)
    t = t_axis(n) / dur
    ff = f * 2 ** (3 * t)
    x = supersaw(ff) * 0.5 + bp(noise(n), 500 + 6000 * t, 1.2)
    return x * t ** 1.5 * vel


def fx_impact(dur, f, vel):
    n = n_samples(max(dur, 0.6))
    t = t_axis(n)
    x = np.sin(2 * np.pi * np.cumsum(f * (1 + 2 * np.exp(-t / 0.02))) / SR) * np.exp(-t / 0.3)
    x += lp(noise(n), 2500) * np.exp(-t / 0.08)
    return reverb(drive(x, 2), 1.0, 0.3)[:n] * vel


def fx_bubble(dur, f, vel):
    n = n_samples(dur)
    t = t_axis(n) / dur
    return np.sin(2 * np.pi * np.cumsum(f * (1 + 2.5 * t ** 2)) / SR) * np.sin(np.pi * t) * vel


def fx_zap(dur, f, vel):
    n = n_samples(dur)
    t = t_axis(n) / dur
    ff = f * (1 + 8 * (1 - t) ** 4)
    return fm(ff, 2.01, 4 * (1 - t)) * (1 - t) * vel


def fx_static(dur, f, vel):
    n = n_samples(dur)
    return bp(noise(n, 12000), 2500, 0.7) * adsr(n, 0.005, release=0.02) * vel


def fx_ping(dur, f, vel):
    n = n_samples(0.25)
    t = t_axis(n)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.06)
    return reverb(x, 1.3, 0.55, predelay=0.03)[: n_samples(max(dur, 0.9))] * vel


def fx_heartbeat(dur, f, vel):
    n = n_samples(max(dur, 0.5))
    x = np.zeros(n)
    for o, a in ((0.0, 1.0), (0.16, 0.7)):
        k = kick("808", a, 0.25)
        i = n_samples(o)
        x[i:i + len(k)] += lp(k, 200)[: n - i]
    return x * vel


def fx_siren(dur, f, vel):
    n = n_samples(dur)
    t = t_axis(n)
    ff = f * (1 + 0.35 * np.sin(2 * np.pi * 2.2 * t - np.pi / 2))
    return (pulse(ff, 0.5) * 0.5 + saw(ff) * 0.5) * adsr(n, 0.01, release=0.03) * vel


def fx_sadviolin(dur, f, vel):
    """Tiny sad violin: bowed saw with slow vibrato & resonances."""
    n = n_samples(dur)
    t = t_axis(n)
    ff = f * (1 + 0.012 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / 0.15))
    x = saw(ff)
    x = bp(x, 450, 1.5) * 0.8 + bp(x, 2200, 2) + bp(x, 3500, 3) * 0.5
    return x * adsr(n, 0.08, release=0.1) * vel


def fx_meow(dur, f, vel):
    n = n_samples(dur)
    t = t_axis(n) / dur
    ff = f * (1 + 0.35 * np.sin(np.pi * t) - 0.2 * t)
    x = saw(ff) * 0.7 + pulse(ff, 0.2) * 0.3
    x = formant_morph(x, ["ee", "i", "a", "o", "u"], 7)
    return x * np.sin(np.pi * t) ** 0.7 * vel * 1.5


def fx_purr(dur, f, vel):
    n = n_samples(dur)
    t = t_axis(n)
    am = (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 26 * t))) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.9 * t))
    x = lp(noise(n), 350) * 4 + sine(np.full(n, f)) * 0.3
    return x * am * adsr(n, 0.08, release=0.1) * vel


def fx_squeak(dur, f, vel):
    """Rubber duck: squeezed air through a reed; pitch rises then drops."""
    n = n_samples(dur)
    t = t_axis(n) / dur
    ff = f * (1 + 0.3 * np.sin(np.pi * t)) * (1 + 0.03 * np.sin(2 * np.pi * 38 * t_axis(n)))
    x = pulse(ff, 0.15) + 0.3 * bp(noise(n), 3000, 2)
    return formant(x, "a", 5) * np.sin(np.pi * t) ** 0.5 * vel * 2


def fx_kazoo(dur, f, vel):
    n = n_samples(dur)
    ff = np.full(n, float(f)) * (1 + 0.01 * np.sin(2 * np.pi * 5 * t_axis(n)))
    buzz = saw(ff) + 0.4 * noise(n) * (0.5 + 0.5 * saw(ff))
    return drive(formant(buzz, "u", 5) * 3, 2) * adsr(n, 0.02, release=0.04) * vel


def fx_crowd(dur, f, vel):
    """Cheer/applause."""
    n = n_samples(dur)
    claps = np.zeros(n)
    for _ in range(int(dur * 60)):
        i = int(rng.integers(0, max(1, n - 2000)))
        m = n_samples(0.015)
        claps[i:i + m] += bp(noise(m), rng.uniform(900, 2500), 2) * np.exp(-t_axis(m) / 0.003)
    t = t_axis(n) / dur
    return (claps + fx_scream(dur, f, 0.4)) * np.sin(np.pi * np.clip(t, 0, 1)) ** 0.3 * vel


def fx_coin(dur, f, vel):
    n = n_samples(0.5)
    t = t_axis(n)
    x = np.where(t < 0.06, pulse(np.full(n, f), 0.25), pulse(np.full(n, f * 1.335), 0.25))
    return x * np.where(t < 0.06, 1, np.exp(-(t - 0.06) / 0.15)) * vel


def fx_dialtone(dur, f, vel):
    n = n_samples(dur)
    t = t_axis(n)
    return (np.sin(2 * np.pi * 350 * t) + np.sin(2 * np.pi * 440 * t)) * 0.5 * adsr(n, 0.005, release=0.01) * vel


def fx_dtmf(dur, f, vel):
    """The note number (mod 12) picks the keypad key: C=1, C#=2 ... B=#."""
    rows, cols = (697, 770, 852, 941), (1209, 1336, 1477)
    k = int(round(69 + 12 * np.log2(f / 440.0))) % 12
    n = n_samples(dur)
    t = t_axis(n)
    return (np.sin(2 * np.pi * rows[k // 3] * t) + np.sin(2 * np.pi * cols[k % 3] * t)) * 0.5 * adsr(n, 0.003, release=0.005) * vel


def fx_boing(dur, f, vel):
    n = n_samples(dur)
    t = t_axis(n)
    ff = f * (1 + 0.6 * np.exp(-t / 0.2) * np.sin(2 * np.pi * 14 * t))
    return fm(ff, 1.0, 2 * np.exp(-t / 0.15)) * np.exp(-t / (dur / 2.5)) * vel


def fx_fart(dur, f, vel):  # the brainrot pack needs one. keep it cartoonish.
    n = n_samples(dur)
    t = t_axis(n) / dur
    ff = f * (1 + 0.25 * np.sin(2 * np.pi * 9 * t_axis(n)) * rng.uniform(0.5, 1)) * (1.2 - 0.4 * t)
    x = pulse(ff, 0.1) * 0.7 + lp(noise(n), 300)
    return lp(x, 900) * np.sin(np.pi * t) ** 0.4 * vel * 1.5


FX = {k[3:]: v for k, v in list(globals().items()) if k.startswith("fx_")}
