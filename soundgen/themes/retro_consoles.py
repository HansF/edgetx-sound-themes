"""Retro console themes: block puzzle handheld, DMG handheld, 16-bit FM console,
16-bit RPG, golden-age arcade."""
import numpy as np

from .. import synth as S
from ..render import inst
from ..theme import Theme, MAJOR, MINOR

# ---------------------------------------------------------------- extra instruments

inst("fm:ym-metal", env=(0.001, 0.35, 0, 0.05), gm=14)(
    lambda f, n, note: S.fm(f, 1.41, 4.0 * np.exp(-S.t_axis(n) / 0.12), feedback=0.4))
inst("fm:ym-stab", env=(0.004, 0.18, 0.35, 0.06), gm=61)(
    lambda f, n, note: S.fm(f, 1.0, 1.0 + 3.0 * np.exp(-S.t_axis(n) / 0.05), feedback=0.8))
inst("syn:16bit-string", env=(0.06, 0, 1, 0.18), gm=48)(
    lambda f, n, note: S.lp(S.supersaw(f, 0.005, 3), 2600))


def _drop(tr, t, pitch, dur=0.12, vol=1.0):
    """Block lock / thunk on the wave channel."""
    tr.note(pitch, t, dur, vol, bend=-12, decay=0.05)


# ---------------------------------------------------------------- Block Drop

class BlockDrop(Theme):
    id = "block-drop"
    name = "Block Drop"
    category = "retro"
    tagline = "Rotate. Drop. Clear four lines."
    blurb = ("A 1989 handheld block puzzle: a Russian folk tune on a pulse lead, wave-channel bass, "
             "rotate clicks, piece locks and the four-line clear.")
    skin = {"bg": "#1b1b3a", "surface": "#f2e9d8", "ink": "#1b1b3a", "muted": "#5b5878",
            "accent": "#e0463a", "font": "Silkscreen"}
    root, scale, step = "A5", MINOR, 0.08
    lead, alt, bass, kit = "chip:p50", "chip:p25", "chip:wave", "kit:chip"

    def startup(self):  # Korobeiniki (public domain), first phrase
        s = self.score()
        st = 0.085
        s.track("chip:p50").seq("E5*2 B4 C5 D5*2 C5 B4 A4*2 A4 C5 E5*2 D5 C5 B4*3", st, vib=0.05)
        s.track("chip:p25", 0.35).seq("G#4*2 G#4 A4 B4*2 A4 G#4 E4*2 E4 A4 C5*2 B4 A4 G#4*3", st)
        s.track("chip:wave", 0.9).seq("E2 E3 E2 E3 E2 E3 E2 E3 A2 A3 A2 A3 A2 A3 A2 A3 G#2 G#3 E2", st)
        s.track("kit:chip", 0.35).beat({"hat": "x.x.x.x.x.x.x.x.x.x"}, st)
        return s

    def arm(self):  # four-line clear
        s = self.score()
        t = s.track("chip:p50").arp(["A5", "C6", "E6", "A6", "C7", "E7", "A7"], 0.04, gap=0.05)
        s.track("chip:p50").note("A7", t, 0.25, decay=0.12)
        s.track("chip:p25", 0.5).arp(["E5", "A5", "C6", "E6", "A6", "C7", "E7"], 0.04)
        s.track("chip:mnoise", 0.4).note("C7", 0.1, 0.35, decay=0.1)
        s.track("chip:wave").note("A3", 0, 0.28, bend=12)
        return s

    def disarm(self):  # stack settles
        s = self.score()
        s.track("chip:p50").seq("E5 C5 A4 E4*3", 0.09)
        _drop(s.track("chip:wave"), 0.3, "A2", 0.2)
        s.track("chip:mnoise", 0.6).note("C4", 0.3, 0.1, decay=0.03)
        return s

    def yes(self):  # rotate
        s = self.score()
        s.track("chip:p50").note("E6", 0, 0.05, bend=7)
        s.track("chip:p50").note("B6", 0.06, 0.05, bend=5)
        return s

    def no(self):  # piece lock
        s = self.score()
        s.track("chip:mnoise").note("C4", 0, 0.08, decay=0.025)
        _drop(s.track("chip:wave"), 0, "E3")
        return s

    def found(self):  # level up
        s = self.score()
        s.track("chip:p50").seq("E6 A6 C#7 E7*3", 0.06)
        s.track("chip:p25", 0.45).seq("C#6 E6 A6 C#7*3", 0.06)
        s.track("chip:wave").seq("A3 E3 A3 A2*3", 0.06)
        return s

    def lost(self):  # top out
        s = self.score()
        s.track("chip:p25").seq("A5 G#5 G5 F#5 F5 E5*4", 0.07)
        s.track("chip:mnoise", 0.35).note("C5", 0, 0.8, decay=0.3)
        s.track("chip:wave").note("E3", 0.35, 0.4, bend=-12)
        return s

    def lowbat(self):  # Korobeiniki second phrase, faster
        s = self.score()
        st = 0.058
        s.track("chip:p50").seq("D6*3 F6 A6*2 G6 F6 E6*3 C6 E6*2 D6 C6", st)
        s.track("chip:wave").seq("D3 D4 D3 D4 C3 C4 C3 C4 A2 A3 A2 A3 E3 E3 E3 E3", st)
        return s

    def critbat(self):
        s = self.score()
        for i in range(3):
            s.track("chip:p12").arp(["E6", "B5", "C6", "D6"], 0.035, i * 0.25, gap=0)
            s.track("chip:wave").note("E3", i * 0.25, 0.12)
        return s

    def signal_warn(self):
        s = self.score()
        s.track("chip:p50").seq("A6 E6 R A6 E6", 0.07)
        return s

    def signal_crit(self):
        s = self.score()
        for i in range(4):
            s.track("chip:p12").arp(["A6", "E6"], 0.045, i * 0.2, gap=0)
        return s

    def warn_a(self):  # soft drop blips
        s = self.score()
        s.track("chip:p50").seq("C6 C6 C6", 0.05, gap=0.4)
        return s

    def warn_b(self):  # hard drop
        s = self.score()
        s.track("chip:p50").note("A6", 0, 0.14, bend=-24, steps=12)
        _drop(s.track("chip:wave"), 0.14, "A2", 0.18)
        s.track("chip:mnoise", 0.6).note("C4", 0.14, 0.1, decay=0.03)
        return s

    def flip(self):
        s = self.score()
        for i in range(4):
            s.track("chip:p50").note(["E6", "G6", "B6", "E7"][i], i * 0.07, 0.05, bend=7)
        return s

    def launch(self):
        s = self.score()
        s.track("chip:p50").note("A4", 0, 0.45, bend=24, steps=16)
        s.track("chip:p25", 0.6).arp(["A6", "C7", "E7", "A7"], 0.06, 0.42)
        return s

    def land(self):
        return self.warn_b()

    def home(self):
        s = self.score()
        s.track("chip:p50").seq("A5 C6 E6 A6*2 G#6 A6*4", 0.08)
        s.track("chip:p25", 0.5).seq("E5 A5 C6 E6*2 E6 E6*4", 0.08)
        s.track("chip:wave").seq("A2*2 E3*2 E2*2 A2*4", 0.08)
        return s


# ---------------------------------------------------------------- Pocket DMG

class PocketDMG(Theme):
    id = "pocket-dmg"
    name = "Pocket DMG"
    category = "retro"
    tagline = "Four shades of green, four channels of sound."
    blurb = ("The 1989 handheld's own voice: the two-note boot ding, thin 12.5% pulse menus, the 32-step "
             "wave channel and the metallic noise mode.")
    skin = {"bg": "#9bbc0f", "surface": "#8bac0f", "ink": "#0f380f", "muted": "#306230",
            "accent": "#0f380f", "font": "Pixelify Sans"}
    root, scale, step = "C6", MAJOR, 0.07
    lead, alt, bass, kit = "chip:p12", "chip:p50", "chip:wave", "kit:chip"
    master = [("hp", {"fc": 140})]

    def startup(self):  # ba-DING
        s = self.score()
        s.track("chip:p50").note("C6", 0, 0.07)
        s.track("chip:p50").note("C7", 0.07, 1.1, decay=0.32)
        return s

    def arm(self):
        s = self.score()
        s.track("chip:p12").seq("C6 E6 G6 C7*2 G6 C7*4", 0.07)
        s.track("chip:p50", 0.35).seq("G5 C6 E6 G6*2 E6 G6*4", 0.07)
        s.track("chip:wave").seq("C4*2 G3*2 C4*5", 0.07)
        return s

    def disarm(self):
        s = self.score()
        s.track("chip:p12").seq("C7 G6 E6 C6*3", 0.08)
        s.track("chip:wave").seq("C4*2 G3 C3*3", 0.08)
        return s

    def yes(self):  # menu select
        s = self.score()
        s.track("chip:p50").note("A6", 0, 0.035)
        s.track("chip:p50").note("E7", 0.035, 0.09, decay=0.05)
        return s

    def no(self):  # menu cancel
        s = self.score()
        s.track("chip:p12").seq("A3 A3", 0.08, gap=0.3)
        return s

    def found(self):  # link established
        s = self.score()
        s.track("chip:p12").seq("C6 G6 C7 G7*3", 0.05)
        s.track("chip:wave").note("C4", 0, 0.35)
        return s

    def lost(self):
        s = self.score()
        s.track("chip:mnoise", 0.5).note("C6", 0, 0.18, decay=0.08)
        s.track("chip:p12").seq("G6 E6 C6 G5*3", 0.07, 0.18)
        return s

    def lowbat(self):  # low-HP alarm
        s = self.score()
        s.track("chip:p50").seq("G6 E6 G6 E6 G6 E6", 0.1, gap=0.25)
        return s

    def critbat(self):
        s = self.score()
        for i in range(4):
            s.track("chip:p12").arp(["C6", "A5", "C6", "A5"], 0.04, i * 0.24, gap=0)
        return s

    def signal_warn(self):
        s = self.score()
        s.track("chip:p12").seq("E6 R E6", 0.08)
        return s

    def signal_crit(self):
        s = self.score()
        for i in range(4):
            s.track("chip:p50").note("B6", i * 0.14, 0.07)
        return s

    def warn_a(self):  # bump into a wall
        s = self.score()
        s.track("chip:p12").note("C4", 0, 0.1, bend=-5)
        s.track("chip:mnoise", 0.4).note("C4", 0, 0.05, decay=0.02)
        return s

    def warn_b(self):
        s = self.score()
        s.track("chip:p12").seq("C6 G6 C6 G6", 0.06, gap=0.2)
        return s

    def idle(self):
        s = self.score()
        for i in range(3):
            s.track("chip:p50").note("C7", i * 0.35, 0.2, decay=0.07)
        return s

    def error(self):
        s = self.score()
        s.track("chip:wave").note("C3", 0, 0.25, vib=0.8, vib_rate=25)
        s.track("chip:wave").note("B2", 0.3, 0.3, vib=0.8, vib_rate=25)
        return s

    def home(self):
        s = self.score()
        s.track("chip:p12").seq("E6 G6 C7 E7*2 D7 C7*4", 0.07)
        s.track("chip:p50", 0.3).seq("C6 E6 G6 C7*2 B6 G6*4", 0.07)
        s.track("chip:wave").seq("C4*2 E4*2 G3*2 C4*4", 0.07)
        return s


# ---------------------------------------------------------------- Blast Processing

class BlastProcessing(Theme):
    id = "blast-processing"
    name = "Blast Processing"
    category = "retro"
    tagline = "Six FM voices and an attitude."
    blurb = ("The 1990 16-bit FM console: slap bass, gritty brass stabs, metallic bells, PSG squares "
             "and sampled drums pushed a little too hard.")
    skin = {"bg": "#0b0d17", "surface": "#16213e", "ink": "#f5f7ff", "muted": "#8ea0c9",
            "accent": "#2f6bff", "font": "Chakra Petch"}
    root, scale, step = "C5", MINOR, 0.08
    lead, alt, bass, kit = "fm:lead", "fm:ym-stab", "fm:bass", "kit:909"
    master = [("drive", {"amount": 1.6}), ("bitcrush", {"bits": 10, "hold": 2})]

    def startup(self):
        s = self.score()
        st = 0.08
        s.track("fm:bass").seq("C2 C2 C3 C2 Bb1 C2 Eb2 F2 G2 G2 G3*2 C2*4", st, gap=0.2)
        s.track("fm:ym-stab", 0.6).seq("C4+Eb4+G4+Bb4*2 R*4 Bb3+D4+F4+Ab4*2 R*2 C4+Eb4+G4+C5*4", st)
        s.track("kit:909", 0.8).beat({"kick": "x...x...x.x.x...", "snare": "....x.......x...",
                                      "hat": "x.x.x.x.x.x.x.x.", "crash": "............x..."}, st)
        s.track("fm:ym-metal", 0.5).note("C7", 12 * st, 0.4)
        return s

    def arm(self):
        s = self.score()
        s.track("fm:lead", 0.8).arp(["C5", "Eb5", "G5", "C6", "Eb6", "G6", "C7"], 0.035)
        for p in ("C4", "Eb4", "G4", "C5"):
            s.track("fm:ym-stab", 0.7).note(p, 0.25, 0.3)
        s.track("kit:909").hit("kick", 0.25)
        s.track("kit:909", 0.7).hit("crash", 0.25)
        s.track("fm:bass").note("C2", 0.25, 0.3)
        return s

    def disarm(self):
        s = self.score()
        for p in ("C4", "Eb4", "G4"):
            s.track("fm:ym-stab", 0.7).note(p, 0, 0.55, bend=-12)
        s.track("fm:bass").note("C3", 0, 0.5, bend=-12)
        s.track("kit:909").hit("snare", 0)
        return s

    def yes(self):
        s = self.score()
        s.track("fm:ym-metal").note("E6", 0, 0.06)
        s.track("fm:ym-metal").note("B6", 0.06, 0.25)
        return s

    def no(self):
        s = self.score()
        s.track("fm:bass").note("G2", 0, 0.18, bend=-7)
        s.track("kit:909", 0.7).hit("kick", 0)
        return s

    def found(self):
        s = self.score()
        s.track("fm:lead").note("G5", 0, 0.2, bend=12)
        for p in ("C5", "Eb5", "G5", "C6"):
            s.track("fm:ym-stab", 0.6).note(p, 0.2, 0.35)
        s.track("fm:ym-metal", 0.6).note("G7", 0.2, 0.3)
        return s

    def lost(self):
        s = self.score()
        s.track("fm:lead").note("C6", 0, 0.7, bend=-24, vib=0.8, vib_rate=12)
        s.track("fm:bass").note("C3", 0.05, 0.4, bend=-12)
        return s

    def lowbat(self):
        s = self.score()
        for i, ch in enumerate((("G4", "Bb4", "D5"), ("F4", "Ab4", "C5"), ("Eb4", "G4", "Bb4"))):
            for p in ch:
                s.track("fm:ym-stab", 0.6).note(p, i * 0.22, 0.15)
            s.track("fm:bass").note(ch[0][0] + "2", i * 0.22, 0.15)
            s.track("kit:909", 0.6).hit("snare", i * 0.22)
        return s

    def critbat(self):
        s = self.score()
        for i in range(3):
            s.track("fm:lead").arp(["G6", "Eb6"], 0.06, i * 0.26, gap=0.05)
            s.track("kit:909", 0.7).hit("snare", i * 0.26)
        return s

    def signal_warn(self):
        s = self.score()
        s.track("chip:p50", 0.7).seq("A5 E5 A5 E5", 0.08)
        s.track("fm:bass").seq("A2 R A2 R", 0.08)
        return s

    def signal_crit(self):
        s = self.score()
        for i in range(4):
            s.track("fm:ym-metal").note("F6", i * 0.18, 0.08, decay=0.04)
            s.track("chip:p50", 0.5).note("B5", i * 0.18, 0.08)
        return s

    def error(self):
        s = self.score()
        s.track("fm:bass").note("C2", 0, 0.25, vib=1.0, vib_rate=30)
        s.track("fm:bass").note("B1", 0.3, 0.3, vib=1.0, vib_rate=30)
        return s

    def flip(self):  # spin-up rev
        s = self.score()
        for i in range(4):
            s.track("fm:lead", 0.8).note("C5", i * 0.08, 0.07, bend=12 + 3 * i)
        return s

    def launch(self):  # rev and release
        s = self.score()
        for i in range(3):
            s.track("fm:lead", 0.6).note("G4", i * 0.1, 0.09, bend=12)
        s.track("fx:whoosh").note("C6", 0.3, 0.45)
        s.track("fm:lead").note("C5", 0.3, 0.35, bend=24)
        s.track("kit:909").hit("crash", 0.3)
        return s

    def land(self):
        s = self.score()
        s.track("fm:lead").note("G6", 0, 0.5, bend=-24)
        s.track("kit:909").hit("kick", 0.5)
        s.track("fm:bass").note("C2", 0.5, 0.3)
        return s

    def home(self):
        s = self.score()
        st = 0.09
        s.track("fm:ym-stab").seq("C5+Eb5+G5 R Bb4+D5+F5 R Ab4+C5+Eb5*2 Bb4+D5+F5*2 C5+E5+G5*4", st)
        s.track("fm:bass").seq("C3 R Bb2 R Ab2*2 Bb2*2 C3*4", st)
        s.track("kit:909", 0.7).beat({"kick": "x.x.x.x.x...", "snare": "......x.x..."}, st)
        return s


# ---------------------------------------------------------------- 16-Bit Quest

class SixteenBitQuest(Theme):
    id = "16bit-quest"
    name = "16-Bit Quest"
    category = "retro"
    tagline = "Rest at the inn. Save your progress."
    blurb = ("A 1994 console RPG: harp arpeggios, sampled strings and flute, a glockenspiel save point "
             "and everything run through that console's famous echo.")
    skin = {"bg": "#0c1445", "surface": "#1f3a93", "ink": "#ffffff", "muted": "#b8c4f0",
            "accent": "#ffd84a", "font": "DotGothic16"}
    root, scale, step = "Eb5", MAJOR, 0.1
    lead, alt, bass, kit = "gm:73", "gm:46", "gm:48", "kit:acoustic"
    master = [("echo", {"delay": 0.17, "feedback": 0.33, "repeats": 3, "tone": 3500}),
              ("reverb", {"size": 0.8, "wet": 0.2})]

    def startup(self):
        s = self.score()
        s.track("gm:46").arp(["Eb4", "G4", "Bb4", "Eb5", "G5", "Bb5", "Eb6"], 0.06, gap=0)
        s.track("gm:48", 0.55).note("Eb3", 0, 1.5)
        for p in ("G3", "Bb3", "Eb4"):
            s.track("gm:48", 0.45).note(p, 0.1, 1.4)
        s.track("gm:73", 0.9).seq("Bb5*2 C6 D6 Eb6*6", 0.1, 0.45)
        s.track("gm:9", 0.4).note("Eb7", 0.42, 0.3)
        return s

    def arm(self):  # item-get fanfare (original)
        s = self.score()
        s.track("gm:55", 0.7).note("C4", 0, 0.3)
        s.track("gm:56", 0.8).seq("G4 C5 E5 G5*2 F5 A5*4", 0.09)
        s.track("gm:9", 0.6).seq("G5 C6 E6 G6*2 F6 A6*4", 0.09)
        s.track("gm:48", 0.5).note("F3", 0.45, 0.6)
        s.track("gm:48", 0.5).note("C4", 0.45, 0.6)
        return s

    def disarm(self):  # inn rest (original)
        s = self.score()
        s.track("gm:46").seq("G5 Eb5 Bb4 G4 Bb4*2 Eb5*3", 0.11)
        s.track("gm:48", 0.45).note("Eb3", 0, 1.1)
        s.track("gm:48", 0.4).note("Bb3", 0.2, 0.9)
        return s

    def yes(self):  # save point shimmer
        s = self.score()
        s.track("gm:9", 0.9).arp(["Eb6", "G6", "Bb6", "Eb7"], 0.045, gap=0)
        return s

    def no(self):
        s = self.score()
        s.track("gm:46").seq("Bb4 Eb4*2", 0.1)
        s.track("gm:48", 0.4).note("Eb3", 0, 0.25)
        return s

    def found(self):  # healing
        s = self.score()
        s.track("gm:46").arp(["Bb4", "Eb5", "G5", "Bb5", "Eb6", "G6", "Bb6"], 0.04, gap=0)
        s.track("gm:52", 0.5).note("Eb5", 0.1, 0.5)
        s.track("gm:52", 0.4).note("G5", 0.1, 0.5)
        return s

    def lost(self):
        s = self.score()
        s.track("gm:73").seq("C6 Bb5 Ab5 G5*4", 0.1, vib=0.1)
        s.track("gm:48", 0.5).note("C3", 0, 0.8)
        s.track("gm:48", 0.4).note("Eb3", 0, 0.8)
        return s

    def lowbat(self):
        s = self.score()
        s.track("gm:73").seq("G5 F5 Eb5 R G5 F5 D5*2", 0.1)
        s.track("gm:48", 0.45).note("C4", 0, 0.9)
        return s

    def critbat(self):  # dry: echo would fill the gaps
        s = self.score(fx=[])
        for i in range(3):
            s.track("fm:bell").note("Ab6", i * 0.3, 0.08, decay=0.06)
            s.track("fm:bell", 0.7).note("D6", i * 0.3 + 0.08, 0.08, decay=0.06)
        return s

    def signal_warn(self):
        s = self.score()
        s.track("gm:9").seq("Bb6 G6 Bb6 G6", 0.1)
        return s

    def signal_crit(self):
        s = self.score(fx=[])
        for i in range(4):
            s.track("fm:bell").note("C7", i * 0.2, 0.07, decay=0.05)
        return s

    def warn_a(self):
        s = self.score()
        s.track("gm:9").seq("Eb6 Bb6", 0.08)
        return s

    def warn_b(self):
        s = self.score()
        s.track("gm:55", 0.8).note("Bb3", 0, 0.3)
        s.track("gm:9").seq("D6 F6 Ab6", 0.07, 0.05)
        return s

    def launch(self):  # battle start
        s = self.score()
        s.track("fx:whoosh").note("C6", 0, 0.45)
        s.track("gm:48").arp(["C4", "D4", "Eb4", "F4", "G4", "Ab4", "B4"], 0.045, 0.1, gap=0)
        s.track("gm:55").note("C4", 0.45, 0.4)
        s.track("gm:55", 0.8).note("C5", 0.45, 0.4)
        return s

    def land(self):
        s = self.score()
        s.track("gm:46").arp(["Eb6", "Bb5", "G5", "Eb5", "Bb4", "G4", "Eb4"], 0.05, gap=0)
        s.track("gm:48", 0.5).note("Eb3", 0.35, 0.6)
        return s

    def home(self):  # full inn rest jingle
        s = self.score()
        s.track("gm:73").seq("Eb5 G5 Bb5 Eb6*2 D6 Eb6*5", 0.1)
        s.track("gm:46", 0.7).arp(["Eb4", "Bb4", "G5", "Ab4", "C5", "Eb5", "Bb4", "D5", "Eb4"], 0.1)
        s.track("gm:48", 0.4).note("Eb3", 0, 1.3)
        return s

    def idle(self):
        s = self.score()
        s.track("gm:46").arp(["G5", "Eb5", "Bb4"], 0.25)
        return s

    def error(self):
        s = self.score()
        s.track("gm:55").note("C3", 0, 0.3)
        s.track("gm:48", 0.7).note("C#3", 0.02, 0.4)
        return s


# ---------------------------------------------------------------- Arcade '82

class Arcade82(Theme):
    id = "arcade-82"
    name = "Arcade '82"
    category = "retro"
    tagline = "Insert coin. Defend the base."
    blurb = ("Golden-age cabinets in a smoky arcade: pulse lasers, the four-note invader march, "
             "a warbling saucer, the insert-coin chime and noise-channel explosions.")
    skin = {"bg": "#120a2a", "surface": "#1f1147", "ink": "#fff6e0", "muted": "#b7a6e0",
            "accent": "#ff2e88", "font": "Jersey 10"}
    root, scale, step = "C5", MINOR, 0.08
    lead, alt, bass, kit = "chip:p50", "chip:p25", "chip:p50", "kit:chip"

    def _boom(self, s, t, vol=1.0, dur=0.45):
        s.track("chip:noise", vol).note("A4", t, dur, bend=-24, decay=dur / 3)

    def _pew(self, s, t, pitch="C8", dur=0.13, vol=1.0):
        s.track("chip:p25", vol).note(pitch, t, dur, bend=-30)

    def startup(self):
        s = self.score()
        s.track("chip:p50").seq("E7 G7", 0.06)                     # coin
        s.track("chip:p50").note("C8", 0.12, 0.3, decay=0.12)
        st = 0.13
        s.track("chip:p50", 0.9).seq("C3 B2 Bb2 A2 C3 B2 Bb2 A2", st, 0.45, gap=0.45)
        self._pew(s, 0.45 + 3 * st)
        self._boom(s, 0.45 + 7 * st, 0.8)
        return s

    def arm(self):  # player ready
        s = self.score()
        for i, p in enumerate(("C5", "G5", "C6")):
            s.track("chip:p50").note(p, i * 0.12, 0.1, bend=5)
        s.track("chip:p25").seq("C6 E6 G6 C7*4", 0.06, 0.36)
        s.track("chip:tri").note("C3", 0.36, 0.4)
        return s

    def disarm(self):  # game over wah-wah
        s = self.score()
        self._boom(s, 0, 0.7, 0.35)
        s.track("chip:p50").seq("G4 F#4 F4 E4*4", 0.12, 0.2, vib=0.4, vib_rate=9)
        return s

    def yes(self):  # insert coin
        s = self.score()
        s.track("chip:p50").note("E7", 0, 0.05)
        s.track("chip:p50").note("B7", 0.05, 0.22, decay=0.08)
        return s

    def no(self):
        s = self.score()
        s.track("chip:p50").note("C4", 0, 0.14, bend=-12)
        s.track("chip:noise", 0.5).note("C4", 0, 0.08, decay=0.03)
        return s

    def found(self):  # bonus
        s = self.score()
        s.track("chip:p25").arp(["C6", "E6", "G6", "C7"] * 2, 0.035, gap=0.1)
        s.track("chip:p50").note("C7", 0.28, 0.2, decay=0.08)
        return s

    def lost(self):  # saucer warble descending
        s = self.score()
        s.track("chip:p25").note("C7", 0, 0.75, bend=-24, vib=1.5, vib_rate=16)
        return s

    def lowbat(self):  # invader march
        s = self.score()
        s.track("chip:p50").seq("C3 B2 Bb2 A2", 0.18, gap=0.45)
        s.track("chip:noise", 0.3).seq("C3 R C3 R", 0.18, gap=0.7)
        return s

    def critbat(self):
        s = self.score()
        for i in range(3):
            s.track("chip:p25").note("A6", i * 0.28, 0.16, vib=1.2, vib_rate=22)
        return s

    def signal_warn(self):  # siren warble
        s = self.score()
        s.track("chip:p50").note("E6", 0, 0.6, vib=2.5, vib_rate=4)
        return s

    def signal_crit(self):
        s = self.score()
        for i in range(4):
            self._pew(s, i * 0.18, "G7", 0.1)
        return s

    def warn_a(self):
        s = self.score()
        self._pew(s, 0)
        return s

    def warn_b(self):
        s = self.score()
        self._pew(s, 0)
        self._pew(s, 0.16, "E8")
        return s

    def error(self):
        s = self.score()
        self._boom(s, 0, 1.0, 0.5)
        return s

    def flip(self):  # wakka wakka
        s = self.score()
        for i in range(4):
            s.track("chip:p50").note("G4" if i % 2 == 0 else "C5", i * 0.1, 0.09,
                                     bend=7 if i % 2 == 0 else -7)
        return s

    def launch(self):
        s = self.score()
        s.track("chip:p50").note("C3", 0, 0.6, bend=36, steps=24)
        self._pew(s, 0.55, "C8", 0.15)
        return s

    def land(self):
        s = self.score()
        s.track("chip:p25").note("C7", 0, 0.6, bend=-30, vib=0.6, vib_rate=14)
        self._boom(s, 0.6, 0.6, 0.3)
        return s

    def home(self):  # high score entry
        s = self.score()
        s.track("chip:p25").seq("C6 E6 G6 C7 G6 C7*4", 0.07)
        s.track("chip:p50", 0.6).seq("C3 G2 C3 E3 G3 C4*4", 0.07)
        return s

    def idle(self):  # attract mode
        s = self.score()
        s.track("chip:p50").seq("C3 B2 Bb2 A2", 0.2, gap=0.5)
        s.track("chip:p25", 0.5).note("E7", 0.85, 0.2, vib=1.2, vib_rate=10)
        return s
