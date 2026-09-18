"""Score / Track / Note: the MIDI-first composition layer.

Every sound in every theme is a Score. A Score is exported as a real Standard MIDI
File (see to_midi) and rendered to audio by render.py with the same note data.

Note strings (Track.seq):
    "E6 G6*2 R C7"      note, xN duration multiplier, R = rest
    "C4+E4+G4*4"        chord
    "E6! G6."           ! accent (full velocity), . staccato (short gate)
Pitches are note names ("C#4", "Bb3") or MIDI numbers.
"""
import re
from dataclasses import dataclass, field

import mido

NOTE_RE = re.compile(r"^([A-Ga-g])([#b]?)(-?\d)$")
SEMI = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

DRUMS = {"kick": 36, "snare": 38, "clap": 39, "hat": 42, "ohat": 46, "crash": 49, "ride": 51,
         "cow": 56, "tom1": 50, "tom2": 47, "tom3": 45, "floor": 41, "rim": 37, "clave": 75,
         "shaker": 70, "tamb": 54}


def pitch_of(p):
    if isinstance(p, (int, float)):
        return float(p)
    m = NOTE_RE.match(p)
    if not m:
        raise ValueError(f"bad note {p!r}")
    return SEMI[m[1].upper()] + {"#": 1, "b": -1, "": 0}[m[2]] + 12 * (int(m[3]) + 1)


@dataclass
class Note:
    pitch: float
    t: float
    dur: float
    vel: float = 0.8
    bend: float = 0.0          # semitones reached at the end of the glide
    glide: float | None = None  # seconds for the bend (default: whole note)
    steps: int = 0              # >0: stepped (hardware-sweep) bend
    vib: float = 0.0            # vibrato depth, semitones
    vib_rate: float = 6.0
    decay: float | None = None  # overrides the instrument's decay (percussive notes)


@dataclass
class Track:
    inst: str
    vol: float = 1.0
    fx: list = field(default_factory=list)   # [(name, {kwargs}), ...] see render.FX_CHAIN
    notes: list = field(default_factory=list)

    def note(self, pitch, t, dur, vel=0.8, **kw):
        self.notes.append(Note(pitch_of(pitch), t, dur, vel, **kw))
        return t + dur

    def chord(self, pitches, t, dur, vel=0.8, **kw):
        """note() for a "C4+E4+G4" chord."""
        for p in pitches.split("+"):
            self.note(p, t, dur, vel, **kw)
        return t + dur

    def seq(self, notes, step, t=0.0, vel=0.8, gap=0.1, **kw):
        for tok in notes.split():
            name, _, mult = tok.partition("*")
            dur = step * float(mult or 1)
            v, g = vel, gap
            if name.endswith("!"):
                name, v = name[:-1], 1.0
            if name.endswith("."):
                name, g = name[:-1], 0.55
            if name not in ("R", "-"):
                for p in name.split("+"):
                    self.note(p, t, dur * (1 - g), v, **kw)
            t += dur
        return t

    def arp(self, pitches, step, t=0.0, vel=0.8, gap=0.1, **kw):
        for p in pitches:
            self.note(p, t, step * (1 - gap), vel, **kw)
            t += step
        return t

    def hit(self, drum, t, vel=0.9, dur=0.1):
        self.notes.append(Note(float(DRUMS.get(drum, drum)), t, dur, vel))
        return t

    def beat(self, pattern, step, t=0.0, vel=0.9):
        """pattern: {"kick": "x...x...", "hat": "..x...x."}; X = accent."""
        end = t
        for drum, pat in pattern.items():
            for i, c in enumerate(pat.replace(" ", "")):
                if c in "xX":
                    self.hit(drum, t + i * step, 1.0 if c == "X" else vel)
            end = max(end, t + len(pat.replace(" ", "")) * step)
        return end

    @property
    def end(self):
        return max((n.t + n.dur for n in self.notes), default=0.0)


@dataclass
class Score:
    tracks: list = field(default_factory=list)
    fx: list = field(default_factory=list)    # master chain
    name: str = ""

    def track(self, inst, vol=1.0, fx=None):
        tr = Track(inst, vol, list(fx or []))
        self.tracks.append(tr)
        return tr

    @property
    def end(self):
        return max((t.end for t in self.tracks), default=0.0)

    def shift(self, dt):
        for tr in self.tracks:
            for n in tr.notes:
                n.t += dt
        return self

    def merge(self, other, at=0.0):
        """Append another score's tracks, offset by `at` seconds."""
        for tr in other.tracks:
            nt = Track(tr.inst, tr.vol, list(tr.fx))
            nt.notes = [Note(**{**n.__dict__, "t": n.t + at}) for n in tr.notes]
            self.tracks.append(nt)
        return self

    # ------------------------------------------------------------ MIDI export

    def to_midi(self, gm_program=None):
        """Standard MIDI File, type 1, 120 bpm, 960 ticks per beat (1 s = 1920 ticks)."""
        from .render import gm_program_for
        gm_program = gm_program or gm_program_for
        tpb = 960
        mf = mido.MidiFile(type=1, ticks_per_beat=tpb)
        meta = mido.MidiTrack()
        meta.append(mido.MetaMessage("set_tempo", tempo=500000, time=0))
        if self.name:
            meta.append(mido.MetaMessage("track_name", name=self.name, time=0))
        mf.tracks.append(meta)
        ch_iter = iter([c for c in range(16) if c != 9] * 4)
        for tr in self.tracks:
            drums = tr.inst.startswith("kit:")
            ch = 9 if drums else next(ch_iter)
            evs = []  # (seconds, order, msg)
            evs.append((0, 0, mido.MetaMessage("track_name", name=tr.inst)))
            if not drums:
                evs.append((0, 0, mido.Message("program_change", program=gm_program(tr.inst), channel=ch)))
                # pitch-bend range: +-48 semitones (RPN 0)
                for c, v in ((101, 0), (100, 0), (6, 48), (38, 0), (101, 127), (100, 127)):
                    evs.append((0, 0, mido.Message("control_change", control=c, value=v, channel=ch)))
            evs.append((0, 0, mido.Message("control_change", control=7, value=int(min(1, tr.vol) * 127), channel=ch)))
            for n in tr.notes:
                key = int(round(min(127, max(0, n.pitch))))
                vel = int(max(1, min(127, n.vel * 127)))
                if n.vib:
                    evs.append((n.t, 1, mido.Message("control_change", control=1, value=min(127, int(n.vib * 127)), channel=ch)))
                if n.bend:
                    g = n.glide or n.dur
                    k = max(2, n.steps or 16)
                    for i in range(k + 1):
                        v = int(max(-8192, min(8191, n.bend * i / k / 48 * 8192)))
                        evs.append((n.t + g * i / k, 1, mido.Message("pitchwheel", pitch=v, channel=ch)))
                evs.append((n.t, 2, mido.Message("note_on", note=key, velocity=vel, channel=ch)))
                evs.append((n.t + n.dur, 0, mido.Message("note_off", note=key, velocity=0, channel=ch)))
                if n.bend:
                    evs.append((n.t + n.dur, 1, mido.Message("pitchwheel", pitch=0, channel=ch)))
                if n.vib:
                    evs.append((n.t + n.dur, 1, mido.Message("control_change", control=1, value=0, channel=ch)))
            evs.sort(key=lambda e: (e[0], e[1]))
            mt = mido.MidiTrack()
            last = 0
            for s, _, msg in evs:
                tick = int(round(s * 2 * tpb))
                mt.append(msg.copy(time=tick - last))
                last = tick
            mf.tracks.append(mt)
        return mf
