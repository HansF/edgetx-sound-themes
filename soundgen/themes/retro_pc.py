"""Old PC and phone themes: 1-bit speaker, 2-op FM card, dial-up desktop, 2003 phone."""
import numpy as np

from .. import synth as S
from ..render import inst
from ..score import pitch_of
from ..theme import Theme, MAJOR, MINOR, MIXOLYDIAN

# ---------------------------------------------------------------- extra instruments

# OPL2-style 2-op patches (sine carrier, sine modulator, fixed envelopes)
inst("fm:opl-lead", env=(0.004, 0.25, 0.6, 0.05), gm=80)(
    lambda f, n, note: S.fm(f, 1.0, 1.6 * (0.5 + 0.5 * np.exp(-S.t_axis(n) / 0.08)), feedback=0.5))
inst("fm:opl-bass", env=(0.002, 0.2, 0.45, 0.04), gm=33)(
    lambda f, n, note: S.fm(f, 0.5, 2.2 * np.exp(-S.t_axis(n) / 0.1)))
inst("fm:opl-bell", env=(0.001, 0.5, 0, 0.08), gm=11)(
    lambda f, n, note: S.fm(f, 3.0, 1.8 * np.exp(-S.t_axis(n) / 0.25)))
inst("fm:opl-kick", env=(0.001, 0.14, 0, 0.02), gm=115)(
    lambda f, n, note: S.fm(f * (1 + 3 * np.exp(-S.t_axis(n) / 0.018)), 1.0, 1.5 * np.exp(-S.t_axis(n) / 0.02)))
inst("fm:opl-snare", env=(0.001, 0.09, 0, 0.02), gm=115)(
    lambda f, n, note: 0.6 * S.fm(f, 2.3, 6.0) + 0.6 * S.noise(n))
inst("fm:opl-hat", env=(0.001, 0.03, 0, 0.01), gm=115)(
    lambda f, n, note: S.fm(f, 7.13, 9.0))

# 2003 phone: vibrate motor (low pulse, amplitude-modulated)
inst("syn:vibra", env=(0.01, 0, 1, 0.03), gm=38)(
    lambda f, n, note: S.lp(S.pulse(np.full(n, 140.0), 0.3), 600)
    * (0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 32 * S.t_axis(n)))))
# polyphonic ringtone "marimba" is fm:marimba; a hard mono square ringtone voice:
inst("syn:ring-sq", env=(0.002, 0, 1, 0.01), gm=80)(lambda f, n, note: S.square_raw(f, 0.5) * 0.8)


def _opl_beat(s, pattern, step, t=0.0, vol=0.8):
    """FM drum kit: k = kick, s = snare, h = hat."""
    for i, c in enumerate(pattern.replace(" ", "")):
        at = t + i * step
        if c == "k":
            s.track("fm:opl-kick", vol).note("C3", at, 0.12)
        elif c == "s":
            s.track("fm:opl-snare", vol * 0.8).note("A3", at, 0.1)
        elif c == "h":
            s.track("fm:opl-hat", vol * 0.35).note("C7", at, 0.03)


def _beep_chord(tr, pitches, t, dur, rate=0.016):
    """1-bit chord: cycle the notes fast enough to blur into a chord."""
    k = 0
    end = t + dur
    while t < end - 1e-6:
        tr.note(pitches[k % len(pitches)], t, min(rate, end - t))
        t += rate
        k += 1
    return end


# ---------------------------------------------------------------- PC Speaker

class PCSpeaker(Theme):
    id = "pc-speaker"
    name = "PC Speaker"
    category = "pc"
    tagline = "One bit. No mercy."
    blurb = ("The beeper inside a 1987 beige tower: a single square wave, fake chords from frantic "
             "arpeggios and the BIOS beep you still hear in your sleep.")
    skin = {"bg": "#0000a8", "surface": "#000000", "ink": "#e8e8e8", "muted": "#a8a8a8",
            "accent": "#fcfc54", "font": "VT323"}
    root, scale, step = "C5", MAJOR, 0.08
    lead = alt = bass = "chip:beeper"
    kit = "kit:chip"

    def startup(self):
        s = self.score()
        b = s.track("chip:beeper")
        b.note("B5", 0, 0.12)                           # POST beep
        t = 0.3
        for ch in (["C5", "E5", "G5"], ["F5", "A5", "C6"], ["G5", "B5", "D6"]):
            t = _beep_chord(b, ch, t, 0.18) + 0.03
        _beep_chord(b, ["C5", "E5", "G5", "C6"], t, 0.5)
        return s

    def arm(self):
        s = self.score()
        b = s.track("chip:beeper")
        t = b.arp(["C5", "E5", "G5", "C6", "E6", "G6"], 0.03, gap=0)
        _beep_chord(b, ["C6", "E6", "G6"], t, 0.3)
        return s

    def disarm(self):
        s = self.score()
        b = s.track("chip:beeper")
        b.note("G6", 0, 0.35, bend=-24, steps=14)
        b.note("C4", 0.4, 0.2)
        return s

    def yes(self):
        s = self.score()
        s.track("chip:beeper").seq("C6 G6", 0.06, gap=0.2)
        return s

    def no(self):  # "Bad command or file name"
        s = self.score()
        s.track("chip:beeper").note("A3", 0, 0.3)
        return s

    def found(self):
        s = self.score()
        s.track("chip:beeper").note("C5", 0, 0.3, bend=24, steps=24)
        s.track("chip:beeper").note("C7", 0.32, 0.12)
        return s

    def lost(self):
        s = self.score()
        s.track("chip:beeper").note("C7", 0, 0.5, bend=-36, steps=30)
        return s

    def lowbat(self):
        s = self.score()
        s.track("chip:beeper").seq("E6 C6 R D6 Bb5 R C6 Ab5", 0.08, gap=0.15)
        return s

    def critbat(self):
        s = self.score()
        b = s.track("chip:beeper")
        for i in range(4):
            b.arp(["A6", "E6", "A6", "E6"], 0.03, i * 0.22, gap=0)
        return s

    def signal_warn(self):
        s = self.score()
        s.track("chip:beeper").seq("C6 R C6 R", 0.08)
        return s

    def signal_crit(self):
        s = self.score()
        for i in range(4):
            s.track("chip:beeper").note("F6", i * 0.16, 0.08)
        return s

    def error(self):
        s = self.score()
        b = s.track("chip:beeper")
        b.note("A2", 0, 0.25)
        b.note("A2", 0.32, 0.25)
        return s

    def warn_a(self):
        s = self.score()
        s.track("chip:beeper").note("C5", 0, 0.15, bend=12, steps=6)
        return s

    def warn_b(self):
        s = self.score()
        b = s.track("chip:beeper")
        b.note("C5", 0, 0.12, bend=12, steps=6)
        b.note("G5", 0.16, 0.15, bend=12, steps=6)
        return s

    def powerdown(self):
        s = self.score()
        s.track("chip:beeper").note("C6", 0, 0.5, bend=-30)
        return s

    def flip(self):
        s = self.score()
        for i in range(4):
            s.track("chip:beeper").note("C5", i * 0.08, 0.06, bend=12, steps=4)
        return s

    def launch(self):
        s = self.score()
        s.track("chip:beeper").note("C4", 0, 0.5, bend=36, steps=36)
        _beep_chord(s.track("chip:beeper"), ["C7", "E7", "G7"], 0.52, 0.2)
        return s

    def land(self):
        s = self.score()
        s.track("chip:beeper").note("C7", 0, 0.55, bend=-36, steps=36)
        s.track("chip:beeper").note("C3", 0.6, 0.08)
        return s

    def home(self):
        s = self.score()
        b = s.track("chip:beeper")
        t = b.seq("G5 C6 E6", 0.08, gap=0.1)
        _beep_chord(b, ["C6", "E6", "G6"], t, 0.35)
        return s

    def cut(self):
        s = self.score()
        s.track("chip:beeper").note("C3", 0, 0.12)
        return s

    def thr_on(self):
        s = self.score()
        s.track("chip:beeper").note("G6", 0, 0.1, bend=-14)
        return s


# ---------------------------------------------------------------- AdLib FM

class AdLibFM(Theme):
    id = "adlib-fm"
    name = "AdLib FM"
    category = "pc"
    tagline = "Nine voices, two operators, pure shareware."
    blurb = ("A 1991 FM sound card in a DOS shareware platformer: bouncy 2-op leads, "
             "a rubbery FM bass and drums made from nothing but sine waves.")
    skin = {"bg": "#0f2d2a", "surface": "#173f3a", "ink": "#fdf6e3", "muted": "#9fc9bf",
            "accent": "#ffb000", "font": "Tiny5"}
    root, scale, step = "C5", MIXOLYDIAN, 0.09
    lead, alt, bass, kit = "fm:opl-lead", "fm:opl-bell", "fm:opl-bass", "kit:chip"

    def startup(self):
        s = self.score()
        st = 0.09
        s.track("fm:opl-lead").seq("G5 C6 D6 E6 G6*2 E6 F6 D6 E6*4", st)
        s.track("fm:opl-bell", 0.4).seq("C6*2 R*2 E6*2 R*2 D6*2 C6*4", st)
        s.track("fm:opl-bass").seq("C3 C4 C3 C4 F2 F3 G2 G3 C3*4", st)
        _opl_beat(s, "k.h.s.h.k.k.s...", st)
        return s

    def arm(self):  # power-up zap
        s = self.score()
        s.track("fm:opl-lead").arp(["C5", "G5", "C6", "E6", "G6", "C7"], 0.04, gap=0)
        s.track("fm:opl-bell").note("C7", 0.24, 0.35)
        _opl_beat(s, "sss.k", 0.05, 0.0, 0.7)
        return s

    def disarm(self):  # womp
        s = self.score()
        s.track("fm:opl-bass").note("C3", 0, 0.45, bend=-12)
        s.track("fm:opl-lead").seq("G5 E5 C5", 0.09)
        return s

    def yes(self):  # pickup
        s = self.score()
        s.track("fm:opl-bell").note("A6", 0, 0.06)
        s.track("fm:opl-bell").note("E7", 0.06, 0.25)
        return s

    def no(self):
        s = self.score()
        s.track("fm:opl-bass").note("E3", 0, 0.16, bend=-10)
        _opl_beat(s, "k", 0.1)
        return s

    def found(self):
        s = self.score()
        s.track("fm:opl-lead").arp(["C6", "E6", "G6", "C7", "E7", "G7"], 0.045)
        s.track("fm:opl-bass", 0.7).note("C4", 0, 0.3)
        return s

    def lost(self):  # original minor slide-down
        s = self.score()
        t = s.track("fm:opl-lead").seq("G5 F#5 F5", 0.1)
        s.track("fm:opl-lead").note("E5", t, 0.4, bend=-12)
        s.track("fm:opl-bass").note("C3", 0, 0.7, bend=-5)
        return s

    def lowbat(self):
        s = self.score()
        t = 0.0
        for ch in (["E5", "G5", "C6"], ["D5", "F5", "Bb5"], ["C5", "E5", "A5"]):
            for p in ch:
                s.track("fm:opl-lead", 0.5).note(p, t, 0.16)
            t += 0.26
        return s

    def critbat(self):
        s = self.score()
        for i in range(3):
            s.track("fm:opl-lead").arp(["A6", "E6"], 0.07, i * 0.27, gap=0.1)
        return s

    def signal_warn(self):
        s = self.score()
        s.track("fm:opl-bell").seq("E6 C6 E6 C6", 0.09)
        return s

    def signal_crit(self):
        s = self.score()
        for i in range(4):
            s.track("fm:opl-lead").note("B6", i * 0.17, 0.08, decay=0.05)
        return s

    def warn_a(self):  # jump
        s = self.score()
        s.track("fm:opl-lead").note("C5", 0, 0.16, bend=12)
        return s

    def warn_b(self):  # spring
        s = self.score()
        s.track("fm:opl-lead").note("G4", 0, 0.3, bend=19, vib=0.5, vib_rate=14)
        return s

    def error(self):
        s = self.score()
        s.track("fm:opl-bass").note("C2", 0, 0.25, vib=1.0, vib_rate=25)
        s.track("fm:opl-bass").note("B1", 0.3, 0.3, vib=1.0, vib_rate=25)
        return s

    def flip(self):
        s = self.score()
        for i in range(4):
            s.track("fm:opl-lead").note("E5", i * 0.08, 0.07, bend=12)
        return s

    def launch(self):
        s = self.score()
        s.track("fm:opl-lead").note("C4", 0, 0.5, bend=24)
        s.track("fm:opl-bell").arp(["G6", "C7", "E7", "G7"], 0.06, 0.45)
        _opl_beat(s, "k...s", 0.1, 0.45)
        return s

    def land(self):
        s = self.score()
        s.track("fm:opl-lead").note("C7", 0, 0.55, bend=-24)
        _opl_beat(s, "k", 0.1, 0.55)
        return s

    def home(self):
        s = self.score()
        st = 0.09
        s.track("fm:opl-lead").seq("C6 D6 E6 G6*2 A6 G6*4", st)
        s.track("fm:opl-bass").seq("C3 C3 F2 G2*2 G2 C3*4", st)
        _opl_beat(s, "k.s.k.s.k", st)
        return s

    def cut(self):
        s = self.score()
        _opl_beat(s, "k", 0.1)
        s.track("fm:opl-bass").note("C2", 0.02, 0.2)
        return s


# ---------------------------------------------------------------- Dial-Up '98

class DialUp98(Theme):
    id = "dialup-98"
    name = "Dial-Up '98"
    category = "pc"
    tagline = "Please don't pick up the phone."
    blurb = ("A 1998 beige desktop: dial tones and the modem handshake, a lush made-up startup chord, "
             "messenger knocks, error dings and the CD-ROM spinning up.")
    skin = {"bg": "#008080", "surface": "#c0c0c0", "ink": "#000000", "muted": "#404040",
            "accent": "#000080", "font": "IBM Plex Mono"}
    root, scale, step = "Db5", MAJOR, 0.1
    lead, alt, bass, kit = "fm:bell", "fm:marimba", "syn:sub", "kit:acoustic"
    master = [("reverb", {"size": 0.9, "wet": 0.2})]

    def startup(self):  # original startup chord, Db major 9
        s = self.score()
        for p, v in (("Db3", 0.6), ("Ab3", 0.5), ("Eb4", 0.45), ("F4", 0.45), ("C5", 0.35)):
            s.track("syn:pad", v).note(p, 0, 1.6)
        s.track("fm:bell", 0.7).arp(["Ab5", "Eb6", "F6", "C7"], 0.22, 0.25)
        s.track("syn:sub", 0.5).note("Db2", 0, 1.5)
        return s

    def arm(self):  # dial, handshake, connected
        s = self.score(fx=[])
        dtmf = s.track("fx:dtmf", 0.5)
        for i, k in enumerate((5, 5, 5, 0, 1, 9)):
            dtmf.note(k, i * 0.09, 0.06)
        s.track("fx:modem", 0.5).note("C5", 0.6, 0.75)
        s.track("fm:bell", 0.8).note("Ab6", 1.4, 0.3)
        s.track("fm:bell", 0.8).note("Db7", 1.5, 0.4)
        return s

    def disarm(self):  # shutdown chord
        s = self.score()
        for p, v in (("Db4", 0.5), ("F4", 0.45), ("Ab4", 0.4)):
            s.track("syn:pad", v).note(p, 0, 1.0, bend=-5)
        s.track("fm:bell", 0.7).arp(["C7", "Ab6", "F6", "Db6"], 0.16)
        return s

    def yes(self):  # buddy signed on (original)
        s = self.score()
        s.track("fm:bell").seq("Ab5 Db6*2", 0.08)
        s.track("fm:marimba", 0.5).note("F5", 0, 0.1)
        return s

    def no(self):  # buddy signed off
        s = self.score()
        s.track("fm:bell").seq("Db6 Ab5*2", 0.08)
        s.track("fm:marimba", 0.8).note("Db4", 0.1, 0.08, decay=0.04)
        return s

    def found(self):  # new message
        s = self.score()
        s.track("fm:marimba").seq("Db6 F6 Ab6 Db7*3", 0.07)
        return s

    def lost(self):  # busy signal
        s = self.score(fx=[])
        for i in range(3):
            s.track("syn:sine", 0.5).note(pitch_of("B4") - 0.05, i * 0.4, 0.22)   # ~480 Hz
            s.track("syn:sine", 0.5).note(pitch_of("D#5") - 0.4, i * 0.4, 0.22)  # ~620 Hz
        return s

    def lowbat(self):
        s = self.score()
        s.track("fm:bell").seq("E6 C6 R E6 C6", 0.1)
        return s

    def critbat(self):  # uh-oh style (original), three times
        s = self.score(fx=[])
        for i in range(3):
            s.track("fm:epiano").note("G5", i * 0.34, 0.1)
            s.track("fm:epiano").note("D5", i * 0.34 + 0.12, 0.1, bend=-1)
        return s

    def error(self):  # critical stop ding (original)
        s = self.score()
        for p in ("C5", "F#5", "C6"):
            s.track("fm:bell", 0.6).note(p, 0, 0.5)
        return s

    def signal_warn(self):
        s = self.score()
        s.track("fx:static", 0.4).note("C5", 0, 0.2)
        s.track("fm:bell").note("A5", 0.22, 0.2)
        return s

    def signal_crit(self):
        s = self.score(fx=[])
        for i in range(4):
            s.track("fx:static").note("C5", i * 0.2, 0.1)
        return s

    def warn_a(self):  # exclamation ding
        s = self.score()
        for p in ("Ab5", "Db6", "F6"):
            s.track("fm:bell", 0.6).note(p, 0, 0.4)
        return s

    def warn_b(self):  # knock knock
        s = self.score()
        s.track("fm:marimba").seq("G3 G3", 0.12, gap=0.3, decay=0.03)
        s.track("kit:acoustic", 0.4).hit("rim", 0)
        s.track("kit:acoustic", 0.4).hit("rim", 0.12)
        return s

    def idle(self):  # screensaver
        s = self.score()
        s.track("syn:pad", 0.5).note("F4", 0, 1.2)
        s.track("fm:bell", 0.6).arp(["C6", "Ab5"], 0.5, 0.2)
        return s

    def launch(self):  # CD-ROM spin-up
        s = self.score()
        s.track("syn:sine", 0.35).note("C3", 0, 1.0, bend=24)
        s.track("fx:whoosh", 0.5).note("C5", 0.1, 0.9)
        s.track("kit:acoustic", 0.5).hit("rim", 0)
        return s

    def land(self):  # spin-down and click
        s = self.score()
        s.track("syn:sine", 0.35).note("C5", 0, 0.8, bend=-24)
        s.track("fx:whoosh", 0.4).note("C5", 0, 0.7)
        s.track("kit:acoustic", 0.6).hit("rim", 0.8)
        return s

    def home(self):
        s = self.score()
        s.track("fm:marimba").seq("Db5 F5 Ab5 Db6*2 C6 Db6*3", 0.09)
        s.track("syn:pad", 0.4).note("Db4", 0, 0.9)
        s.track("syn:pad", 0.3).note("Ab4", 0, 0.9)
        return s

    def cut(self):  # power switch click
        s = self.score(fx=[])
        s.track("kit:acoustic").hit("rim", 0)
        s.track("syn:sub", 0.8).note("Db2", 0.01, 0.2, bend=-5)
        return s

    def thr_on(self):
        s = self.score()
        s.track("fx:modem", 0.5).note("C5", 0, 0.25)
        return s

    def powerdown(self):
        return self.disarm()


# ---------------------------------------------------------------- Polyphonic 2003

class Polyphonic2003(Theme):
    id = "polyphonic-2003"
    name = "Polyphonic 2003"
    category = "pc"
    tagline = "16-voice ringtones, now in color."
    blurb = ("A 2003 candybar phone: marimba ringtones, a waltz by Tárrega on the keypad synth, "
             "SMS morse beeps, the vibrate motor and that battery chirp.")
    skin = {"bg": "#9fc4e8", "surface": "#dbe9f5", "ink": "#0b1a33", "muted": "#3e5a7a",
            "accent": "#ff6a00", "font": "Doto"}
    root, scale, step = "A5", MAJOR, 0.075
    lead, alt, bass, kit = "fm:marimba", "syn:ring-sq", "fm:bass", "kit:808"

    def startup(self):  # Gran Vals (Tárrega, public domain), bars 13-16
        s = self.score()
        st = 0.075
        s.track("fm:marimba").seq("E6 D6 F#5*2 G#5*2 C#6 B5 D5*2 E5*2 B5 A5 C#5*2 E5*2 A5*4", st, gap=0.05)
        s.track("fm:kalimba", 0.5).seq("E5 D5 F#4*2 G#4*2 C#5 B4 D4*2 E4*2 B4 A4 C#4*2 E4*2 A4*4", st, gap=0.05)
        s.track("fm:bass", 0.6).seq("A2*4 E2*4 B2*4 E2*4 A2*4", st)
        return s

    def arm(self):
        s = self.score()
        s.track("fm:marimba").arp(["A5", "C#6", "E6", "A6", "C#7"], 0.06)
        s.track("fm:kalimba", 0.7).note("A6", 0.3, 0.3)
        s.track("fm:bass", 0.6).note("A2", 0, 0.4)
        return s

    def disarm(self):  # switching off
        s = self.score()
        s.track("fm:marimba").arp(["E6", "C#6", "A5", "E5", "A4"], 0.08)
        s.track("syn:ring-sq", 0.4).note("A5", 0.42, 0.2, bend=-12)
        return s

    def yes(self):  # keypad beeps
        s = self.score()
        s.track("syn:ring-sq", 0.6).seq("E6 A6", 0.06, gap=0.2)
        return s

    def no(self):
        s = self.score()
        s.track("syn:ring-sq", 0.6).seq("A4 A4", 0.08, gap=0.35)
        return s

    def found(self):  # SMS: ... -- ...  (morse)
        s = self.score()
        d, g = 0.05, 0.05
        t = 0.0
        tr = s.track("syn:ring-sq", 0.6)
        for letter in ("...", "--", "..."):
            for c in letter:
                dur = d if c == "." else 3 * d
                tr.note("A6", t, dur)
                t += dur + g
            t += 2 * g
        return s

    def lost(self):  # call dropped
        s = self.score()
        s.track("syn:ring-sq", 0.6).seq("E6 C6 A5", 0.14, gap=0.3)
        return s

    def lowbat(self):  # battery chirp
        s = self.score()
        tr = s.track("syn:ring-sq", 0.6)
        tr.seq("E7 C7", 0.07, gap=0.15)
        tr.seq("E7 C7", 0.07, 0.45, gap=0.15)
        return s

    def critbat(self):
        s = self.score()
        for i in range(3):
            s.track("syn:ring-sq", 0.6).arp(["E7", "C7"], 0.06, i * 0.3, gap=0.1)
            s.track("syn:vibra", 0.5).note("C3", i * 0.3, 0.12)
        return s

    def signal_warn(self):  # no network
        s = self.score()
        s.track("syn:ring-sq", 0.6).seq("C6 R C6", 0.1)
        return s

    def signal_crit(self):  # old ringer bursts
        s = self.score()
        for i in range(3):
            s.track("syn:ring-sq", 0.6).arp(["A6", "E6"] * 3, 0.03, i * 0.33, gap=0)
        return s

    def warn_a(self):
        s = self.score()
        s.track("syn:vibra").note("C3", 0, 0.3)
        return s

    def warn_b(self):  # bzzt bzzt
        s = self.score()
        s.track("syn:vibra").note("C3", 0, 0.25)
        s.track("syn:vibra").note("C3", 0.35, 0.25)
        return s

    def idle(self):
        s = self.score()
        s.track("syn:vibra", 0.8).note("C3", 0, 0.2)
        s.track("fm:marimba").seq("A6 E6", 0.15, 0.4)
        return s

    def error(self):
        s = self.score()
        s.track("syn:ring-sq", 0.6).note("A3", 0, 0.35)
        return s

    def home(self):
        s = self.score()
        s.track("fm:marimba").seq("E6 C#6 E6 A6*2 G#6 A6*4", 0.08)
        s.track("fm:bass", 0.6).seq("A2*2 E2*2 E2*2 A2*4", 0.08)
        return s

    def launch(self):
        s = self.score()
        s.track("fm:marimba").arp(["A4", "C#5", "E5", "A5", "C#6", "E6", "A6", "C#7"], 0.05)
        s.track("syn:vibra", 0.5).note("C3", 0, 0.3)
        return s

    def land(self):
        s = self.score()
        s.track("fm:marimba").arp(["A6", "E6", "C#6", "A5", "E5", "C#5", "A4"], 0.06)
        s.track("syn:vibra", 0.6).note("C3", 0.42, 0.2)
        return s

    def cut(self):
        s = self.score()
        s.track("syn:vibra").note("C3", 0, 0.15)
        s.track("syn:ring-sq", 0.5).note("A3", 0, 0.1)
        return s

    def thr_on(self):
        s = self.score()
        s.track("syn:ring-sq", 0.6).note("A6", 0, 0.08, bend=-12)
        return s
