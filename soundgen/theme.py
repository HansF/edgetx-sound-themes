"""Theme base class.

A theme is a palette (key, scale, tempo, instruments, master FX, site skin) plus one
method per role returning a Score. Every role has a template default built from the
palette, so a new theme only has to write the sounds that define it. Themes must
write startup/arm/disarm/lowbat/critbat themselves.

Template grammar, so pilots can learn a theme fast:
  rising = good / on, falling = bad / off, repeats = warning, fast repeats = critical,
  N notes = count N.
"""
from .score import Score, pitch_of

MAJOR = [0, 2, 4, 5, 7, 9, 11]
MINOR = [0, 2, 3, 5, 7, 8, 10]
HARM_MINOR = [0, 2, 3, 5, 7, 8, 11]
DORIAN = [0, 2, 3, 5, 7, 9, 10]
PHRYGIAN = [0, 1, 3, 5, 7, 8, 10]
MIXOLYDIAN = [0, 2, 4, 5, 7, 9, 10]
LYDIAN = [0, 2, 4, 6, 7, 9, 11]
PENTA = [0, 2, 4, 7, 9]
MINOR_PENTA = [0, 3, 5, 7, 10]
BLUES = [0, 3, 5, 6, 7, 10]
WHOLE = [0, 2, 4, 6, 8, 10]


class Theme:
    # --- identity (site)
    id = "base"
    name = "Base"
    category = "retro"          # retro | pc | screen | sim | meme
    tagline = ""
    blurb = ""
    skin = {"bg": "#101010", "surface": "#1c1c1c", "ink": "#f0f0f0", "muted": "#9a9a9a",
            "accent": "#ff3366", "font": "Space Mono"}
    # --- palette
    root = "C5"
    scale = MAJOR
    step = 0.09                  # base note length (s)
    lead = "chip:p25"
    alt = "chip:p50"
    bass = "chip:tri"
    kit = "kit:chip"
    master = []                  # master FX chain
    lead_fx = []

    def score(self, fx=None):
        return Score(fx=list(self.master if fx is None else fx), name=f"{self.id}")

    def deg(self, i, octave=0):
        n = len(self.scale)
        return pitch_of(self.root) + self.scale[i % n] + 12 * (i // n + octave)

    def degs(self, *idx, octave=0):
        return [self.deg(i, octave) for i in idx]

    def L(self, s, inst=None, vol=1.0):
        return s.track(inst or self.lead, vol, self.lead_fx)

    # ------------------------------------------------------------ must override

    def startup(self):
        s = self.score()
        self.L(s).arp(self.degs(0, 2, 4, 7, 9, 11, 14), self.step * 0.7)
        s.track(self.bass).note(self.deg(0, -2), 0, self.step * 5)
        return s

    def arm(self):
        s = self.score()
        self.L(s).arp(self.degs(0, 4, 7, 11, 14), self.step * 0.8)
        return s

    def disarm(self):
        s = self.score()
        self.L(s).arp(self.degs(14, 11, 7, 4, 0), self.step * 0.8)
        return s

    def lowbat(self):
        s = self.score()
        t = 0.0
        for i in (4, 3, 2):
            t = self.L(s).arp([self.deg(i + 1), self.deg(i)], self.step * 0.8, t) + self.step * 0.4
        return s

    def critbat(self):
        s = self.score()
        self.L(s).arp([self.deg(7), self.deg(5)] * 5, self.step * 0.55)
        return s

    # ------------------------------------------------------------ templates

    def yes(self):
        s = self.score()
        self.L(s).arp(self.degs(4, 7), self.step * 0.8, decay=0.25)
        return s

    def no(self):
        s = self.score()
        self.L(s).arp(self.degs(4, 0, octave=-1), self.step * 0.9)
        return s

    def found(self):
        s = self.score()
        self.L(s).arp(self.degs(0, 2, 4, 7, 9, 11, 14), self.step * 0.5)
        return s

    def lost(self):
        s = self.score()
        t = self.L(s).arp(self.degs(7, 4, 2), self.step * 0.8)
        self.L(s).note(self.deg(0), t, self.step * 3, bend=-12)
        return s

    def warn_a(self):
        s = self.score()
        self.L(s).note(self.deg(0), 0, 0.18, bend=12, steps=8)
        return s

    def warn_b(self):
        s = self.score()
        t = self.L(s).note(self.deg(0), 0, 0.14, bend=7)
        self.L(s).note(self.deg(4), t + 0.04, 0.22, bend=12, steps=10)
        return s

    def signal_warn(self):
        s = self.score()
        self.L(s).arp(self.degs(7, 4, 7, 4), self.step * 0.9)
        return s

    def signal_crit(self):
        s = self.score()
        self.L(s).arp(self.degs(9, 7) * 5, self.step * 0.5)
        return s

    def error(self):
        s = self.score()
        tr = s.track(self.bass)
        t = tr.note(self.deg(0, -2), 0, 0.22, vib=0.6, vib_rate=28)
        tr.note(self.deg(-1, -2), t + 0.06, 0.28, vib=0.6, vib_rate=28)
        return s

    def powerdown(self):
        s = self.score()
        self.L(s).arp(self.degs(11, 7, 9, 5, 7, 4, 5, 2), self.step * 0.45)
        return s

    def idle(self):
        s = self.score()
        t = 0.0
        for _ in range(2):
            t = self.L(s).arp(self.degs(7, 4), self.step * 1.2, t, decay=0.15) + self.step * 1.5
        return s

    def timer(self, n):
        s = self.score()
        for i in range(n):
            s.merge(self.yes(), at=i * 0.42)
        return s

    def trim(self, level):
        s = self.score()
        p = self.deg(0, level - 1)
        self.L(s).arp([p] * (1 if level == 1 else 2), self.step * 0.9, decay=0.1)
        return s

    def count(self, n, base=0):
        s = self.score()
        self.L(s).arp([self.deg(base + i) for i in range(n)], 0.12, decay=0.12)
        return s

    def flip(self):
        s = self.score()
        for i in range(4):
            self.L(s).note(self.deg(0), i * 0.08, 0.07, bend=12)
        return s

    def launch(self):
        s = self.score()
        self.L(s).note(self.deg(0, -1), 0, 0.5, bend=24, steps=20)
        s.track(self.alt, 0.6).arp(self.degs(7, 9, 11, 14), 0.06, 0.45)
        return s

    def land(self):
        s = self.score()
        self.L(s).note(self.deg(7, 1), 0, 0.65, bend=-28, vib=0.3)
        s.track(self.kit).hit("kick", 0.66)
        return s

    def home(self):
        s = self.score()
        st = self.step
        self.L(s).arp(self.degs(0, 2, 4, 7), st, gap=0.1)
        self.L(s).note(self.deg(7), 4 * st, st * 3)
        s.track(self.alt, 0.5).arp(self.degs(-3, 0, 2, 4), st)
        s.track(self.bass, 0.8).note(self.deg(0, -2), 0, st * 7)
        return s

    def cut(self):
        s = self.score()
        s.track(self.kit).hit("kick", 0)
        s.track(self.bass).note(self.deg(0, -2), 0.02, 0.2)
        return s

    def thr_on(self):
        s = self.score()
        s.track(self.kit, 0.5).hit("hat", 0)
        self.L(s).note(self.deg(7, 1), 0, 0.1, bend=-14)
        return s

    # ------------------------------------------------------------ plumbing

    def role(self, name, args=()):
        return getattr(self, name)(*args)

    def meta(self):
        return {"id": self.id, "name": self.name, "category": self.category,
                "tagline": self.tagline, "blurb": self.blurb, "skin": self.skin}
