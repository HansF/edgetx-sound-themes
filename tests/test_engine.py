import io

import mido
import numpy as np

from soundgen.render import render, INSTR
from soundgen.score import Score, pitch_of
from soundgen import synth as S


def test_pitch_names():
    assert pitch_of("A4") == 69
    assert pitch_of("C#5") == 73
    assert pitch_of("Bb3") == 58


def test_midi_roundtrip_keeps_notes():
    s = Score(name="t")
    s.track("chip:p25").seq("C5 E5 G5*2 R C6+E6", 0.1)
    s.track("kit:808").beat({"kick": "x..x", "hat": "xxxx"}, 0.1)
    s.track("syn:saw").note("A3", 0, 0.5, bend=12)
    buf = io.BytesIO()
    s.to_midi().save(file=buf)
    buf.seek(0)
    m = mido.MidiFile(file=buf)
    got = sorted((msg.channel, msg.note) for tr in m.tracks for msg in tr if msg.type == "note_on")
    want = []
    ch = 0
    for tr in s.tracks:
        c = 9 if tr.inst.startswith("kit:") else ch
        ch += 0 if tr.inst.startswith("kit:") else 1
        want += [(c, int(round(n.pitch))) for n in tr.notes]
    assert got == sorted(want)
    assert any(msg.type == "pitchwheel" for tr in m.tracks for msg in tr)
    assert abs(m.length - s.end) < 0.01


def test_every_instrument_renders():
    for name in INSTR:
        s = Score()
        s.track(name).note("A4", 0, 0.2)
        x = render(s)
        assert np.isfinite(x).all() and np.abs(x).max() > 0.01, name


def test_every_fx_renders():
    for name, fn in S.FX.items():
        y = fn(0.4, 330.0, 0.8)
        assert np.isfinite(y).all() and np.abs(y).max() > 0.01, name
