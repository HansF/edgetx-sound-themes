"""Render a theme to an EdgeTX pack: 16 kHz mono 16-bit WAVs + the MIDI sources."""
import hashlib
import io
import wave
from pathlib import Path

import numpy as np
from scipy import signal

from . import synth as S
from .render import render
from .roles import EVENTS, max_len

OUT_SR = 16000
RMS_DB = -15.0     # loudness of the loud half of the clip
PEAK_DB = -1.0


def finalize(x, cap):
    """48 kHz float -> 16 kHz float: band-limit, trim silence, cap length, loudness-match."""
    y = signal.resample_poly(x, 1, S.SR // OUT_SR)
    thr = 1e-3 * (np.max(np.abs(y)) or 1)
    nz = np.flatnonzero(np.abs(y) > thr)
    if len(nz):
        y = y[nz[0]: nz[-1] + 1]
    limit = int(cap * OUT_SR)
    if len(y) > limit:                      # tails (reverb, echo) are faded, never cut hard
        y = y[:limit].copy()
        f = int(0.12 * OUT_SR)
        y[-f:] *= np.linspace(1, 0, f) ** 2
    f = min(len(y), int(0.004 * OUT_SR))
    if f:
        y[-f:] *= np.linspace(1, 0, f)
    loud = np.sort(np.abs(y))[len(y) // 2:]
    y = y * 10 ** (RMS_DB / 20) / (np.sqrt(np.mean(loud ** 2)) or 1)
    y = y * min(1.0, 10 ** (PEAK_DB / 20) / (np.max(np.abs(y)) or 1))
    return y


def wav_bytes(y):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(OUT_SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
    return buf.getvalue()


def midi_bytes(score):
    buf = io.BytesIO()
    score.to_midi().save(file=buf)
    return buf.getvalue()


def build_theme(theme_cls, out_dir: Path):
    """Writes out_dir/SOUNDS/en/<file>.wav and out_dir/midi/<file>.mid.
    Returns {file: {"hash", "dur", "role"}}."""
    theme = theme_cls()
    S.reseed(sum(map(ord, theme.id)))
    cache, index, seen, used = {}, {}, set(), {}
    for file, role, args, _label in EVENTS:
        key = (role, args)
        if key not in cache:
            cache[key] = theme.role(role, args)
        base = cache[key]
        k = used.get(key, 0)
        while True:      # every file gets its own sound: bump the variant until it is new and not too quiet
            score = base.variant(k)
            y = finalize(render(score), max_len(role, args))
            wb = wav_bytes(y)
            k += 1
            loud = np.sort(np.abs(y))[len(y) // 2:]
            quiet = 20 * np.log10(np.sqrt(np.mean(loud ** 2)) + 1e-9) < RMS_DB - 6    # sparse, ringing variants
            if wb not in seen and (not quiet or k == 1):
                break
        used[key] = k
        seen.add(wb)
        mb, dur = midi_bytes(score), len(y) / OUT_SR
        wp = out_dir / "SOUNDS" / "en" / f"{file}.wav"
        mp = out_dir / "midi" / f"{file}.mid"
        wp.parent.mkdir(parents=True, exist_ok=True)
        mp.parent.mkdir(parents=True, exist_ok=True)
        wp.write_bytes(wb)
        mp.write_bytes(mb)
        index[file] = {"hash": hashlib.sha1(wb).hexdigest()[:12], "dur": round(dur, 3), "role": role}
    return index
