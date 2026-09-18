"""Score -> audio. Instruments are named "<family>:<patch>":

    chip:p12|p25|p50|p75|tri|wave|noise|mnoise|beeper    NES / Game Boy / PC-speaker channels
    syn:saw|sq|pad|bass|sub|sine|theremin|brass|lead|pluck|organ|calliope|musicbox|808|reese|choir|whistle
    fm:epiano|bell|celesta|marimba|brass|bass|organ|lead|kalimba|harpsi
    kit:808|909|chip|phonk|acoustic                     drums on GM note numbers
    fx:<name>                                            procedural effects (synth.FX)
    gm:<program>                                         General MIDI via fluidsynth + soundfont
"""
import hashlib
import io
import os
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np

from . import synth as S
from .score import Score

SF2 = Path(os.environ.get("EDGETX_SF2", Path.home() / ".cache/edgetx-sound-themes/GeneralUser-GS.sf2"))
CACHE = Path(os.environ.get("EDGETX_CACHE", Path.home() / ".cache/edgetx-sound-themes/fluid"))

# ---------------------------------------------------------------- instruments
# fn(f, n, note) -> raw audio; env = (attack, decay, sustain, release); raw=True skips env.

INSTR = {}


def inst(name, env=(0.003, 0.0, 1.0, 0.02), gm=80, raw=False):
    def deco(fn):
        INSTR[name] = (fn, env, gm, raw)
        return fn
    return deco


for d in (12, 25, 50, 75):
    inst(f"chip:p{d}", gm=80)(lambda f, n, note, d=d: S.pulse(f, d / 100))
inst("chip:tri", gm=38)(lambda f, n, note: S.tri_nes(f))
inst("chip:wave", gm=38)(lambda f, n, note: S.wavetable(f))
inst("chip:noise", gm=127)(lambda f, n, note: S.noise(n, float(np.mean(f)) * 12))
inst("chip:mnoise", gm=127)(lambda f, n, note: S.noise(n, float(np.mean(f)) * 12, True))
inst("chip:beeper", env=(0, 0, 1, 0), gm=80, raw=True)(lambda f, n, note: S.square_raw(f))


def _filter_env(n, lo, hi, attack=0.02, decay=0.3, sustain=0.5):
    t = S.t_axis(n)
    e = np.minimum(1, t / attack) * (sustain + (1 - sustain) * np.exp(-np.maximum(0, t - attack) / decay))
    return lo + (hi - lo) * e


inst("syn:saw", gm=81)(lambda f, n, note: S.lp(S.supersaw(f), _filter_env(n, 800, 6000), 1.2))
inst("syn:sq", gm=80)(lambda f, n, note: S.lp(S.pulse(f, 0.5), 3500))
inst("syn:pad", env=(0.18, 0, 1, 0.25), gm=89)(lambda f, n, note: S.chorus(S.lp(S.supersaw(f, 0.008, 5), 2200)))
inst("syn:bass", gm=38)(lambda f, n, note: S.lp(S.saw(f) + S.sine(f / 2), _filter_env(n, 250, 2200, decay=0.12, sustain=0.2), 1.5))
inst("syn:sub", gm=38)(lambda f, n, note: S.sine(f) + 0.15 * S.sine(2 * f))
inst("syn:sine", gm=80)(lambda f, n, note: S.sine(f))
inst("syn:whistle", env=(0.03, 0, 1, 0.05), gm=78)(
    lambda f, n, note: S.sine(f * (1 + 0.004 * np.sin(2 * np.pi * 5.5 * S.t_axis(n)))) + 0.05 * S.bp(S.noise(n), float(np.mean(f)) * 2, 3))
inst("syn:theremin", env=(0.09, 0, 1, 0.12), gm=40)(
    lambda f, n, note: S.sine(f * 2 ** (0.25 / 12 * np.sin(2 * np.pi * 6.2 * S.t_axis(n)) * np.minimum(1, S.t_axis(n) / 0.25))) * 0.9
    + 0.1 * S.tri(f))
inst("syn:brass", env=(0.03, 0, 1, 0.08), gm=62)(
    lambda f, n, note: S.lp(S.supersaw(f, 0.006, 3) + 0.4 * S.pulse(f * 0.5, 0.5), _filter_env(n, 400, 4500, 0.05, 0.25, 0.55), 1.3))
inst("syn:lead", env=(0.005, 0, 1, 0.05), gm=81)(lambda f, n, note: S.lp(S.saw(f * 1.003) + S.pulse(f * 0.997, 0.4), 5000))
inst("syn:pluck", env=(0, 0, 1, 0.05), gm=25)(lambda f, n, note: S.karplus(float(f[0]), n, 0.995, 0.5) * 1.5)
inst("syn:lute", env=(0, 0, 1, 0.05), gm=24)(lambda f, n, note: S.bp(S.karplus(float(f[0]), n, 0.992, 0.35), 900, 0.5) * 3)
inst("syn:organ", env=(0.01, 0, 1, 0.05), gm=16)(
    lambda f, n, note: sum(a * S.sine(f * h) for h, a in ((0.5, 0.5), (1, 1), (2, 0.6), (3, 0.4), (4, 0.3), (6, 0.15), (8, 0.2))) / 2)
inst("syn:calliope", env=(0.02, 0, 1, 0.05), gm=82)(
    lambda f, n, note: S.sine(f * (1 + 0.006 * np.sin(2 * np.pi * 7 * S.t_axis(n)))) + 0.25 * S.sine(2 * f)
    + 0.12 * S.bp(S.noise(n), float(np.mean(f)) * 2, 2))
inst("syn:musicbox", env=(0, 0.35, 0, 0.05), gm=10)(
    lambda f, n, note: S.sine(f) + 0.35 * S.sine(f * 5.4) * np.exp(-S.t_axis(n) / 0.05) + 0.2 * S.sine(f * 2))
inst("syn:808", env=(0.002, 0, 1, 0.06), gm=38)(
    lambda f, n, note: S.drive(S.sine(f * (1 + 1.5 * np.exp(-S.t_axis(n) / 0.02))) * np.exp(-S.t_axis(n) / 0.9), 1.8))
inst("syn:reese", env=(0.01, 0, 1, 0.05), gm=38)(
    lambda f, n, note: S.lp(S.saw(f * 0.993) + S.saw(f * 1.007) + S.sine(f / 2), 700 + 300 * np.sin(2 * np.pi * 0.7 * S.t_axis(n))))
inst("syn:choir", env=(0.12, 0, 1, 0.25), gm=52)(
    lambda f, n, note: S.formant(S.supersaw(f, 0.006, 3), "a", 6) * 2.5 + S.formant(S.supersaw(f * 1.5, 0.005, 3), "o", 6) * 0.8)

inst("fm:epiano", env=(0.001, 0.6, 0.15, 0.15), gm=4)(
    lambda f, n, note: S.fm(f, 1.0, 1.8 * np.exp(-S.t_axis(n) / 0.3)) + 0.15 * S.fm(f, 14, 1.0) * np.exp(-S.t_axis(n) / 0.05))
inst("fm:bell", env=(0.001, 0.9, 0, 0.2), gm=14)(lambda f, n, note: S.fm(f, 3.5, 2.5 * np.exp(-S.t_axis(n) / 0.6)))
inst("fm:celesta", env=(0.001, 0.45, 0, 0.1), gm=8)(
    lambda f, n, note: S.fm(f, 4.0, 1.2 * np.exp(-S.t_axis(n) / 0.2)) + 0.3 * S.sine(2 * f) * np.exp(-S.t_axis(n) / 0.1))
inst("fm:marimba", env=(0.001, 0.22, 0, 0.05), gm=12)(lambda f, n, note: S.fm(f, 3.9, 2.2 * np.exp(-S.t_axis(n) / 0.03)))
inst("fm:kalimba", env=(0.001, 0.3, 0, 0.05), gm=108)(lambda f, n, note: S.fm(f, 5.5, 1.6 * np.exp(-S.t_axis(n) / 0.04)))
inst("fm:brass", env=(0.02, 0, 1, 0.06), gm=61)(lambda f, n, note: S.fm(f, 1.0, 0.5 + 2.2 * np.minimum(1, S.t_axis(n) / 0.06), feedback=0.3))
inst("fm:bass", env=(0.001, 0.25, 0.3, 0.04), gm=36)(lambda f, n, note: S.fm(f, 1.0, 3.5 * np.exp(-S.t_axis(n) / 0.08), feedback=0.6))
inst("fm:organ", env=(0.005, 0, 1, 0.04), gm=17)(lambda f, n, note: S.fm(f, 2.0, 1.2) * 0.7 + 0.5 * S.fm(f, 1.0, 0.6))
inst("fm:lead", env=(0.003, 0, 1, 0.04), gm=80)(lambda f, n, note: S.fm(f, 1.0, 1.5, feedback=0.9))
inst("fm:harpsi", env=(0.001, 0.5, 0, 0.05), gm=6)(lambda f, n, note: S.fm(f, 3.0, 3 * np.exp(-S.t_axis(n) / 0.15)) * 0.7 + 0.3 * S.saw(f) * np.exp(-S.t_axis(n) / 0.2))

GM_FAMILY = {"chip": 80, "syn": 81, "fm": 4, "fx": 122, "kit": 0}


def gm_program_for(name):
    fam, _, patch = name.partition(":")
    if fam == "gm":
        return int(patch) % 128
    if name in INSTR:
        return INSTR[name][2]
    return GM_FAMILY.get(fam, 80)


# ---------------------------------------------------------------- notes & tracks

def pitch_curve(note, n):
    t = S.t_axis(n)
    p = np.full(n, note.pitch)
    if note.bend:
        g = max(1e-3, note.glide or note.dur)
        x = np.clip(t / g, 0, 1)
        if note.steps:
            x = np.floor(x * note.steps) / note.steps
        p = p + note.bend * x
    if note.vib:
        p = p + note.vib * np.sin(2 * np.pi * note.vib_rate * t) * np.minimum(1, t / 0.12)
    return S.midi_hz(p)


def render_note(name, note):
    fam, _, patch = name.partition(":")
    if fam == "kit":
        return S.drum(note.pitch, patch, note.vel)
    if fam == "fx":
        return S.FX[patch](note.dur, float(S.midi_hz(note.pitch)), note.vel)
    fn, (a, d, s, r), _, raw = INSTR[name]
    if note.decay is not None:
        d, s = note.decay, 0.0
    n = S.n_samples(note.dur + r)
    x = fn(pitch_curve(note, n), n, note)
    if raw:
        return x * np.where(np.arange(n) < S.n_samples(note.dur), 1.0, 0.0)
    return x * S.adsr(n, a, d, s, r, gate=S.n_samples(note.dur)) * note.vel


FX_CHAIN = {
    "reverb": S.reverb, "echo": S.echo, "chorus": S.chorus, "wobble": S.wobble,
    "bitcrush": S.bitcrush, "drive": S.drive, "lp": S.lp, "hp": S.hp, "bp": S.bp,
    "telephone": S.telephone,
    "crackle": lambda x, level=0.3, density=30: x + S.crackle(len(x), density, level),
    "gain": lambda x, g=1.0: x * g,
}


def apply_fx(x, chain):
    for item in chain:
        name, kw = (item, {}) if isinstance(item, str) else item
        x = FX_CHAIN[name](x, **kw)
    return x


def mix_at(parts):
    if not parts:
        return np.zeros(1)
    n = max(o + len(a) for o, a in parts)
    out = np.zeros(n)
    for o, a in parts:
        out[o:o + len(a)] += a
    return out


def render_track(tr):
    if tr.inst.startswith("gm:"):
        x = render_gm(tr)
    else:
        x = mix_at([(S.n_samples(n.t), render_note(tr.inst, n)) for n in tr.notes])
    return apply_fx(x * tr.vol, tr.fx)


def render(score: Score):
    x = mix_at([(0, render_track(tr)) for tr in score.tracks])
    return apply_fx(x, score.fx)


# ---------------------------------------------------------------- fluidsynth (gm:*)

def have_fluidsynth():
    return shutil.which("fluidsynth") is not None and SF2.exists()


def render_gm(tr):
    one = Score(tracks=[tr.__class__(tr.inst, 1.0, [], tr.notes)])
    buf = io.BytesIO()
    one.to_midi().save(file=buf)
    mid = buf.getvalue()
    key = hashlib.sha1(mid + SF2.name.encode()).hexdigest()[:16]
    CACHE.mkdir(parents=True, exist_ok=True)
    cached = CACHE / f"{key}.npy"
    if cached.exists():
        return np.load(cached)
    if not have_fluidsynth():
        raise RuntimeError(f"gm track needs fluidsynth and a soundfont at {SF2}")
    with tempfile.TemporaryDirectory() as d:
        mp, wp = Path(d) / "in.mid", Path(d) / "out.wav"
        mp.write_bytes(mid)
        subprocess.run(["fluidsynth", "-ni", "-q", "-R", "0", "-C", "0", "-g", "0.8",
                        "-r", str(S.SR), "-F", str(wp), str(SF2), str(mp)],
                       check=True, capture_output=True)
        with wave.open(str(wp)) as w:
            ch, sw = w.getnchannels(), w.getsampwidth()
            raw = w.readframes(w.getnframes())
        dt = {2: "<i2", 4: "<i4"}[sw]
        x = np.frombuffer(raw, dt).astype(float) / (2 ** (8 * sw - 1))
        x = x.reshape(-1, ch).mean(axis=1)
    nz = np.flatnonzero(np.abs(x) > 1e-4)
    x = x[: nz[-1] + 1] if len(nz) else x
    np.save(cached, x)
    return x
