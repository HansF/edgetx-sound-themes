"""Sim & chill themes: life sim, theme park, city builder, elevator bossa, lo-fi study."""
import numpy as np

from .. import synth as S
from ..theme import Theme, MAJOR, DORIAN


def rate_pitch(hz):
    """MIDI pitch whose frequency equals `hz` (used to set fx:click ratchet rate)."""
    return 69 + 12 * np.log2(hz / 440.0)


# ---------------------------------------------------------------- theme-local effects

def _blegh(dur, f, vel):
    """Comedic retch: growly saw through an e -> a -> o mouth, pitch sagging."""
    n = S.n_samples(dur)
    t = S.t_axis(n) / dur
    ff = f * (1.15 - 0.55 * t)
    growl = 0.65 + 0.35 * np.sin(2 * np.pi * 32 * S.t_axis(n))
    x = S.saw(ff) * growl + 0.25 * S.bp(S.noise(n), 900, 1.2)
    x = S.formant_morph(x, ["e", "a", "o"], 6) * 2.5
    return S.drive(x, 2.0) * np.sin(np.pi * np.clip(t * 1.1, 0, 1)) ** 0.4 * vel


def _dozer(dur, f, vel):
    """Bulldozer: chugging diesel, track rattle, one clank of the blade at the end."""
    n = S.n_samples(dur)
    t = S.t_axis(n)
    chug = 0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 9 * t))
    eng = S.lp(S.pulse(f * (1 + 0.04 * np.sin(2 * np.pi * 3 * t)), 0.3), 500) * chug
    rattle = S.bp(S.noise(n, 3000, True), 1800, 2) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 17 * t))) * 0.25
    x = (eng + rattle + S.lp(S.noise(n), 250) * 0.8) * S.adsr(n, 0.08, release=0.15)
    m = S.n_samples(0.3)
    i = max(0, n - m - S.n_samples(0.05))
    x[i:i + m] += S.fm(np.full(m, 310.0), 3.7, 3 * np.exp(-S.t_axis(m) / 0.04)) * np.exp(-S.t_axis(m) / 0.08) * 0.8
    return x * vel


def _rain(dur, f, vel):
    n = S.n_samples(dur)
    bed = S.lp(S.hp(S.noise(n), 1200), 6000) * 0.25
    drops = np.zeros(n)
    for _ in range(int(dur * 25)):
        i = int(S.rng.integers(0, max(1, n - 400)))
        m = S.n_samples(0.006)
        drops[i:i + m] += S.bp(S.noise(m), S.rng.uniform(2500, 6000), 3) * np.exp(-S.t_axis(m) / 0.0015)
    return (bed + drops) * S.adsr(n, 0.2, release=0.3) * vel


def _tap(dur, f, vel):
    """Pencil tap on a desk."""
    n = S.n_samples(0.08)
    t = S.t_axis(n)
    return (S.bp(S.noise(n), 2400, 3) * np.exp(-t / 0.004) * 1.5
            + np.sin(2 * np.pi * f * t) * np.exp(-t / 0.012)) * vel


def _page(dur, f, vel):
    """Page turn: paper swish with crinkle."""
    n = S.n_samples(dur)
    t = S.t_axis(n) / dur
    crinkle = 0.6 + 0.4 * ((S.rng.random(n) < 0.02).cumsum() % 2)
    x = S.bp(S.noise(n), 3200 - 1800 * t, 1.1) * crinkle
    return x * np.sin(np.pi * t) ** 1.2 * 2 * vel


S.FX["sim_blegh"] = _blegh
S.FX["sim_dozer"] = _dozer
S.FX["sim_rain"] = _rain
S.FX["sim_tap"] = _tap
S.FX["sim_page"] = _page


# ---------------------------------------------------------------- Life Sim

class LifeSim(Theme):
    """Bright vibes-and-marimba jazz, upright bass, brushes."""
    id = "life-sim"
    name = "Life Sim"
    category = "sim"
    tagline = "Your quad's needs are fully met."
    blurb = ("Sunny marimba and vibraphone jazz, a walking upright bass and a three-note chime "
             "for everything going right. When it goes wrong, a trombone says uh-oh.")
    skin = {"bg": "#e6f7df", "surface": "#ffffff", "ink": "#1d3b2a", "muted": "#5b7a66",
            "accent": "#2fbf4f", "font": "Fredoka"}
    root, scale, step = "F5", MAJOR, 0.1
    lead, alt, bass, kit = "fm:marimba", "gm:11", "gm:32", "kit:acoustic"
    master = [("reverb", {"size": 0.8, "wet": 0.18})]

    def chime(self, s, t=0.0, vol=0.9):
        """The signature cue: C - A - F, bright and final."""
        return s.track("gm:11", vol).seq("C7 A6 F7*3", 0.09, t, gap=0.05)

    def startup(self):
        s = self.score()
        mar = s.track("fm:marimba")
        mar.seq("F5 A5 C6 E6 G6 A6 C7*2", 0.075)
        s.track("gm:11", 0.6).note("F4", 0.6, 1.0, 0.7)
        for p in ("A4", "C5", "E5", "G5"):                      # Fmaj9 on vibes
            s.track("gm:11", 0.5).note(p, 0.6, 1.0, 0.65)
        s.track("gm:32", 0.9).seq("F2 A2 C3 D3 F3*3", 0.15, vel=0.9)
        br = s.track("kit:acoustic", 0.35)
        for i in range(8):                                      # swung brushes
            br.hit("shaker", i * 0.15 + (0.05 if i % 2 else 0), 0.6 if i % 2 else 0.9)
        self.chime(s, 1.1, 0.6)
        return s

    def arm(self):                                  # need fulfilled
        s = self.score()
        s.track("fm:marimba").seq("C6 E6 G6 B6 D7 G7*3", 0.065, gap=0.05)
        for p in ("C5", "E5", "G5", "B5", "D6"):    # Cmaj9
            s.track("gm:11", 0.45).note(p, 0.33, 0.6, 0.7)
        s.track("gm:32", 0.8).note("C3", 0.33, 0.5)
        return s

    def disarm(self):
        s = self.score()
        s.track("fm:marimba").seq("A6 F6 D6 Bb5 G5*3", 0.085)
        s.track("gm:32", 0.8).seq("D3*2 G2*3", 0.1)
        return s

    def yes(self):
        s = self.score()
        self.chime(s)
        return s

    def no(self):                                   # uh-oh
        s = self.score()
        tb = s.track("gm:57")
        tb.note("D4", 0, 0.16, 0.85)
        tb.note("A3", 0.2, 0.3, 0.85, bend=-1.5, vib=0.3, vib_rate=5)
        return s

    def found(self):
        s = self.score()
        self.chime(s)
        s.track("fm:celesta", 0.5).seq("F6 A6 C7 F7 A7", 0.04, 0.3)   # cash sparkle
        return s

    def lost(self):                                 # wah wah wah waaah
        s = self.score()
        tb = s.track("gm:57")
        tb.seq("Bb3 A3 Ab3", 0.2, vel=0.85)
        tb.note("G3", 0.6, 0.45, 0.85, bend=-1.2, vib=0.5, vib_rate=6)
        return s

    def lowbat(self):                               # hungry
        s = self.score()
        s.track("fm:marimba").seq("C6 A5 C6 A5 R C6 A5 C6 A5", 0.085)
        s.track("gm:32", 0.7).seq("F2 R R R R C3", 0.085)
        return s

    def critbat(self):
        s = self.score(fx=[])
        m = s.track("fm:marimba")
        for i in range(4):
            m.seq("F6 C7", 0.05, i * 0.22, vel=1.0, decay=0.04)
        return s

    def signal_crit(self):
        s = self.score(fx=[])
        m = s.track("fm:marimba")
        for i in range(4):
            m.seq("A6 E6 A6", 0.045, i * 0.24, vel=1.0, decay=0.035)
        return s

    def signal_warn(self):
        s = self.score()
        s.track("fm:marimba").seq("E6 C6 R E6 C6", 0.09)
        return s

    def home(self):
        s = self.score()
        s.track("fm:marimba").seq("C6 D6 E6 G6 A6*2 G6 C7*3", 0.08)
        for p in ("F4", "A4", "C5", "E5"):
            s.track("gm:11", 0.4).note(p, 0.4, 0.8, 0.6)
        s.track("gm:32", 0.8).seq("F2*2 C3*2 F3*4", 0.1)
        return s

    def idle(self):
        s = self.score()
        s.track("gm:11", 0.8).seq("A6 F6 R R A6 F6", 0.14)
        return s


# ---------------------------------------------------------------- Theme Park '99

class ThemePark99(Theme):
    """Band organ, oompah tuba, glockenspiel, coasters and a very happy crowd."""
    id = "theme-park-99"
    name = "Theme Park '99"
    category = "sim"
    tagline = "Park rating: excellent. Guests: screaming."
    blurb = ("A wheezing band organ, oompah tuba and glockenspiel, the clack of a chain lift on take-off, "
             "riders screaming through a flip and a cash register for every good thing.")
    skin = {"bg": "#fff3d6", "surface": "#ffffff", "ink": "#3a1e0c", "muted": "#8a6242",
            "accent": "#d7263d", "font": "Rye"}
    root, scale, step = "G5", MAJOR, 0.11
    lead, alt, bass, kit = "syn:calliope", "gm:9", "gm:58", "kit:acoustic"
    master = [("reverb", {"size": 0.6, "wet": 0.12})]

    def oompah(self, s, roots, t=0.0, step=None, vol=0.8):
        step = step or self.step
        tu = s.track("gm:58", vol)
        for i, (r, f) in enumerate(roots):
            tu.note(r, t + i * 2 * step, step * 0.9, 0.9)
            tu.note(f, t + (i * 2 + 1) * step, step * 0.9, 0.75)
        return t + len(roots) * 2 * step

    def startup(self):
        s = self.score()
        st = 0.11
        s.track("syn:calliope").seq("G5 B5 D6 G6*2 E6 C6 E6 D6*3 B5 G5*2", st, vel=0.9)
        s.track("gm:20", 0.35).seq("B4+D5*2 R B4+D5 C5+E5*2 R A4+C5 B4+D5*3", st * 1.0)
        s.track("gm:9", 0.5).seq("G6 R D7 R G7 R E7 R D7*3", st)
        self.oompah(s, [("G2", "D3"), ("C3", "G3"), ("D3", "A3"), ("G2", "D3")], 0, st)
        dr = s.track("kit:acoustic", 0.5)
        for i in range(0, 16, 2):
            dr.hit("kick", i * st, 0.8)
        dr.hit("crash", 12 * st, 0.6)
        return s

    def arm(self):                                   # the crowd goes wild
        s = self.score()
        s.track("fx:crowd", 0.8).note("E5", 0, 1.3, 0.8)
        s.track("syn:calliope").seq("D6 G6 B6 D7*4", 0.07, 0.05, vel=0.9)
        s.track("gm:9", 0.6).seq("G6 B6 D7 G7*3", 0.07, 0.05)
        s.track("kit:acoustic", 0.6).hit("crash", 0.33)
        return s

    def disarm(self):                                # ride closed
        s = self.score()
        s.track("syn:calliope").seq("D6 B5 G5 D5*4", 0.12)
        s.track("gm:58", 0.9).seq("D3*2 G2*5", 0.12)
        return s

    def yes(self):
        s = self.score()
        s.track("fx:kaching").note("C7", 0, 0.6, 0.9)
        return s

    def no(self):                                    # tuba blat
        s = self.score()
        s.track("gm:58").seq("D3. G2*2", 0.13, vel=0.95)
        return s

    def found(self):
        s = self.score()
        s.track("fx:kaching").note("C7", 0, 0.6, 0.9)
        s.track("gm:9", 0.7).seq("G6 B6 D7 G7", 0.06, 0.18)
        return s

    def lost(self):                                  # sad trombone
        s = self.score()
        tb = s.track("gm:57")
        tb.seq("B3 Bb3 A3", 0.2, vel=0.9)
        tb.note("Ab3", 0.6, 0.5, 0.9, vib=0.6, vib_rate=6)
        return s

    def lowbat(self):
        s = self.score()
        s.track("syn:calliope").seq("D6 B5 D6 B5 R D6 B5 D6 B5", 0.085)
        self.oompah(s, [("G2", "D3"), ("G2", "D3")], 0, 0.19, 0.6)
        return s

    def critbat(self):                               # blegh x3 (guest felt sick)
        s = self.score(fx=[])
        b = s.track("fx:sim_blegh")
        for i, p in enumerate(("A3", "G3", "E3")):
            b.note(p, i * 0.36, 0.26, 1.0)
        return s

    def signal_crit(self):
        s = self.score(fx=[])
        c = s.track("syn:calliope")
        for i in range(4):
            c.seq("G6 D6", 0.06, i * 0.22, vel=1.0, gap=0.2)
        return s

    def signal_warn(self):
        s = self.score()
        s.track("syn:calliope").seq("E6 C6 E6 C6", 0.1)
        return s

    def launch(self):                                # chain lift, crest, drop
        s = self.score()
        ck = s.track("fx:click", 0.9)
        ck.note(rate_pitch(8), 0, 0.38, 0.9)
        ck.note(rate_pitch(12), 0.38, 0.32, 0.9)
        ck.note(rate_pitch(18), 0.7, 0.28, 0.9)
        s.track("fx:whoosh", 0.8).note("A5", 1.0, 0.55, 0.9)
        s.track("syn:calliope", 0.7).note("G5", 1.0, 0.45, bend=12)
        return s

    def flip(self):                                  # loop-the-loop
        s = self.score()
        s.track("fx:scream", 0.9).note("E5", 0, 1.1, 0.9)
        s.track("fx:whoosh", 0.6).note("C5", 0.05, 0.9, 0.8)
        return s

    def land(self):                                  # brakes hiss into the station
        s = self.score()
        s.track("fx:whoosh", 0.8).note("G5", 0, 0.5, 0.8)
        s.track("syn:calliope").seq("G6 D6 B5 G5*3", 0.09, 0.4)
        s.track("gm:58", 0.8).note("G2", 0.76, 0.3)
        return s

    def home(self):
        s = self.score()
        s.track("fx:crowd", 0.6).note("E5", 0.3, 1.2, 0.7)
        s.track("syn:calliope").seq("G5 C6 E6 G6*2 E6 G6*4", 0.09)
        self.oompah(s, [("C3", "G3"), ("C3", "G3")], 0, 0.18)
        return s

    def error(self):                                 # ride breakdown
        s = self.score()
        s.track("fx:sim_dozer", 0.7).note("C2", 0, 0.5, 0.8)
        s.track("gm:58").note("Eb2", 0.1, 0.4, 0.9, bend=-3)
        return s


# ---------------------------------------------------------------- City Planner 2000

class CityPlanner2000(Theme):
    """Late-90s fusion: rhodes, fretless, soft tenor sax, ride cymbal."""
    id = "city-planner-2000"
    name = "City Planner 2000"
    category = "sim"
    tagline = "Zoned, funded and grooving in Eb."
    blurb = ("Smooth late-90s MIDI fusion for the mayor of the airfield: rhodes and fretless bass, "
             "a zoning plop for every switch, a bulldozer on disarm and sirens when it matters.")
    skin = {"bg": "#0f2a44", "surface": "#173a5e", "ink": "#e8f1fa", "muted": "#8fb0cf",
            "accent": "#f2b134", "font": "Orbitron"}
    root, scale, step = "Eb5", MAJOR, 0.1
    lead, alt, bass, kit = "fm:epiano", "gm:66", "gm:35", "kit:909"
    master = [("chorus", {"mix_": 0.25}), ("reverb", {"size": 0.9, "wet": 0.2})]

    def plop(self, s, p="C5", t=0.0, vol=1.0):
        return s.track("syn:sine", vol).note(p, t, 0.09, 0.95, bend=-11, decay=0.05)

    def chord(self, s, notes, t, dur, vol=0.45):
        tr = s.track("fm:epiano", vol)
        for i, p in enumerate(notes.split()):
            tr.note(p, t + i * 0.012, dur, 0.75)

    def startup(self):
        s = self.score()
        self.chord(s, "Eb4 G4 Bb4 D5 F5", 0, 0.55)          # Ebmaj9
        self.chord(s, "Ab3 C4 Eb4 G4 D5", 0.6, 0.45)        # Abmaj7#11
        self.chord(s, "Bb3 Eb4 F4 Ab4 C5", 1.05, 0.7)       # Bb9sus
        s.track("gm:35", 0.9).seq("Eb2*5 Ab2*4 Bb2*6", 0.1, vel=0.85)
        s.track("gm:66", 0.7).seq("R*3 Bb5 C6 Eb6 F6 G6*3 F6 Eb6 G6*4", 0.08, vel=0.8)
        s.track("kit:909", 0.25).beat({"ride": "x.xx.xx.xx.xx.xx", "kick": "x.......x......."}, 0.1)
        return s

    def arm(self):                                   # zone it, build it
        s = self.score()
        for i, p in enumerate(("G5", "C6", "Eb6")):
            self.plop(s, p, i * 0.1)
        self.chord(s, "Eb4 G4 Bb4 D5 F5", 0.3, 0.7, 0.55)
        s.track("gm:66", 0.6).seq("Bb5 Eb6*4", 0.08, 0.32)
        return s

    def disarm(self):                                # bulldozed
        s = self.score()
        s.track("fx:sim_dozer").note("A1", 0, 1.0, 0.9)
        self.chord(s, "C4 Eb4 Gb4 Bb4", 0.05, 0.5, 0.3)
        return s

    def yes(self):
        s = self.score()
        self.plop(s, "G5")
        self.chord(s, "Bb4 D5 F5", 0.08, 0.3, 0.45)
        return s

    def no(self):
        s = self.score()
        s.track("gm:35").note("Bb2", 0, 0.3, 0.9, bend=-5)
        self.plop(s, "C4", 0.02, 0.8)
        return s

    def found(self):                                 # tax revenue
        s = self.score()
        s.track("fx:kaching", 0.9).note("Bb6", 0, 0.6, 0.9)
        s.track("gm:66", 0.6).seq("Eb6 G6 Bb6*3", 0.07, 0.2)
        return s

    def lost(self):
        s = self.score()
        s.track("gm:66").seq("G5 F5", 0.16, vel=0.85)
        s.track("gm:66").note("D5", 0.32, 0.45, 0.85, bend=-3)
        return s

    def lowbat(self):
        s = self.score()
        s.track("fm:epiano").seq("C6 Ab5 C6 Ab5 R C6 Ab5 C6 Ab5", 0.085, vel=0.95)
        return s

    def critbat(self):
        s = self.score(fx=[])
        for i in range(3):
            s.track("fx:siren").note("A5", i * 0.34, 0.24, 1.0)
        return s

    def signal_crit(self):
        s = self.score(fx=[])
        for i in range(4):
            s.track("fx:siren").note("D6", i * 0.26, 0.17, 1.0)
        return s

    def signal_warn(self):
        s = self.score()
        s.track("fm:epiano").seq("G5 Eb5 R G5 Eb5", 0.1)
        return s

    def error(self):                                 # brownout
        s = self.score()
        tr = s.track("fm:epiano")
        for p in ("Eb4", "G4", "Bb4", "D5"):
            tr.note(p, 0, 0.7, 0.8, bend=-7, glide=0.6)
        return s

    def home(self):
        s = self.score()
        self.chord(s, "Ab3 C4 Eb4 G4", 0, 0.4)
        self.chord(s, "Bb3 D4 F4 Ab4", 0.4, 0.4)
        self.chord(s, "Eb4 G4 Bb4 D5 F5", 0.8, 0.8)
        s.track("gm:66", 0.7).seq("Eb6 F6 G6*2 Bb6 G6*2 Eb7*4", 0.08, 0.1)
        return s

    def cut(self):
        s = self.score()
        s.track("fx:sim_dozer", 0.8).note("A1", 0, 0.35, 0.8)
        return s


# ---------------------------------------------------------------- Elevator Bossa

class ElevatorBossa(Theme):
    """Muzak bossa nova: nylon guitar, flute, rhodes, shaker, the elevator ding."""
    id = "elevator-bossa"
    name = "Elevator Bossa"
    category = "meme"
    tagline = "Going up. Please enjoy the flute."
    blurb = ("Waiting-room bossa nova with nylon guitar, breathy flute and a shaker that never stops. "
             "Every event arrives with an elevator ding, and flight modes are floor chimes.")
    skin = {"bg": "#f4ecdf", "surface": "#fffaf2", "ink": "#3b3024", "muted": "#8c7a66",
            "accent": "#b08d57", "font": "Playfair Display"}
    root, scale, step = "F5", MAJOR, 0.12
    lead, alt, bass, kit = "gm:73", "fm:epiano", "gm:32", "kit:acoustic"
    master = [("reverb", {"size": 1.0, "wet": 0.22})]

    def ding(self, s, notes="A6 F6", t=0.0, vol=1.0, step=0.22):
        return s.track("fm:bell", vol).seq(notes, step, t, vel=0.9, gap=0.0)

    def comp(self, s, voicing, t, vol=0.55):
        g = s.track("gm:24", vol)
        for i, p in enumerate(voicing.split()):
            g.note(p, t + i * 0.015, 0.3, 0.7)

    def startup(self):
        s = self.score()
        st = 0.12
        for t in (0, 0.36, 0.72, 1.08):
            self.comp(s, "F3 A3 C4 E4" if t < 0.7 else "G3 Bb3 D4 F4", t)
        s.track("gm:32", 0.8).seq("F2*3 C3*3 G2*3 D3*3", st)
        s.track("gm:73", 0.8).seq("R*2 A5 C6 E6*3 D6 C6*3 A5*2", st, vel=0.75)
        k = s.track("kit:acoustic", 0.35)
        k.beat({"shaker": "xxxxxxxxxxxxxx", "clave": "x..x..x...x.x."}, st)
        return s

    def arm(self):                                   # going up
        s = self.score()
        self.ding(s, "F6 A6")
        self.comp(s, "F3 A3 C4 E4 G4", 0.44)
        return s

    def disarm(self):                                # doors closing
        s = self.score()
        self.ding(s, "A6 F6")
        s.track("fx:whoosh", 0.6).note("C4", 0.35, 0.6, 0.7)
        s.track("kit:acoustic", 0.6).hit("floor", 0.95, 0.8)
        return s

    def yes(self):
        s = self.score()
        self.ding(s, "A6")
        return s

    def no(self):
        s = self.score()
        self.ding(s, "D6 Bb5", step=0.18)
        return s

    def count(self, n, base=0):                      # floor chimes
        s = self.score()
        tr = s.track("fm:bell")
        for i in range(n):
            tr.note(self.deg(base + i, 1), i * 0.13, 0.1, 0.9, decay=0.1)
        return s

    def found(self):
        s = self.score()
        s.track("gm:73").seq("C6 E6 G6 A6*3", 0.07, vel=0.8)
        self.ding(s, "A6", 0.35, 0.8)
        return s

    def lost(self):
        s = self.score()
        fl = s.track("gm:73")
        fl.seq("E6 D6 C6", 0.14, vel=0.8)
        fl.note("A5", 0.42, 0.45, 0.8, bend=-1, vib=0.3)
        return s

    def lowbat(self):
        s = self.score()
        s.track("fm:epiano").seq("E6 C6 E6 C6 R E6 C6 E6 C6", 0.085, vel=0.95)
        return s

    def critbat(self):
        s = self.score(fx=[])
        b = s.track("fm:bell")
        for i in range(4):
            b.note("A6", i * 0.2, 0.08, 1.0, decay=0.04)
            b.note("E7", i * 0.2 + 0.05, 0.06, 0.8, decay=0.03)
        return s

    def signal_crit(self):
        s = self.score(fx=[])
        b = s.track("fm:bell")
        for i in range(5):
            b.note("C7", i * 0.17, 0.07, 1.0, decay=0.035)
        return s

    def home(self):
        s = self.score()
        s.track("gm:73", 0.8).seq("A5 C6 F6 E6 C6 A5 F6*4", 0.1, vel=0.8)
        for i, t in enumerate((0, 0.4, 0.8)):
            self.comp(s, ["F3 A3 C4 E4", "G3 Bb3 D4 F4", "C3 E3 Bb3 D4"][i], t)
        self.ding(s, "F6 A6", 0.9, 0.7)
        return s

    def idle(self):                                  # anyone there?
        s = self.score()
        s.track("gm:73", 0.8).seq("C6 A5 R*3 C6 A5", 0.15, vel=0.7)
        return s


# ---------------------------------------------------------------- Lo-fi Study

LOFI_MASTER = [("lp", {"fc": 3800}), ("wobble", {"depth": 0.003, "rate": 0.5}),
               ("crackle", {"level": 0.12, "density": 18})]


class LofiStudy(Theme):
    """Dusty rhodes 9ths, lazy swung boom-bap, vinyl and rain."""
    id = "lofi-study"
    name = "Lo-fi Study"
    category = "meme"
    tagline = "Beats to arm and relax to."
    blurb = ("Dusty rhodes ninth chords over a lazy swung boom-bap, with tape wobble, vinyl crackle and a "
             "little rain on the window. Critical alerts skip the haze and ring through clean.")
    skin = {"bg": "#2b2238", "surface": "#3a2f4a", "ink": "#f3e9dc", "muted": "#b3a4c2",
            "accent": "#ffb27a", "font": "Caveat"}
    root, scale, step = "D5", DORIAN, 0.14
    lead, alt, bass, kit = "fm:epiano", "fm:kalimba", "syn:sub", "kit:808"
    master = LOFI_MASTER

    def keys(self, s, notes, t, dur=0.6, vol=0.5, **kw):
        tr = s.track("fm:epiano", vol)
        for i, p in enumerate(notes.split()):
            tr.note(p, t + i * 0.02, dur, 0.7, **kw)

    def swing(self, i, st):
        return i * st + (st * 0.28 if i % 2 else 0)

    def startup(self):
        s = self.score()
        st = 0.11
        self.keys(s, "D3 F4 A4 C5 E5", 0, 0.85)            # Dm9
        self.keys(s, "G3 F4 B4 E5 A5", 0.88, 0.8)          # G13
        s.track("syn:sub", 0.7).seq("D2*8 G2*7", st)
        dr = s.track("kit:808", 0.7)
        for i in range(16):
            t = self.swing(i, st)
            if i in (0, 5, 10):
                dr.hit("kick", t, 0.9)
            if i in (4, 12):
                dr.hit("snare", t, 0.8)
            dr.hit("shaker", t, 0.5 if i % 2 else 0.8)
        s.track("fx:sim_rain", 0.18).note("C5", 0, 1.7, 0.6)
        s.track("fm:kalimba", 0.4).seq("R*9 A5 C6 E6", st)
        return s

    def arm(self):
        s = self.score()
        self.keys(s, "C4 E4 G4 B4 D5", 0, 0.9, 0.55)        # Cmaj9, rolled
        s.track("fm:kalimba", 0.6).seq("G5 B5 D6 G6", 0.07, 0.25)
        s.track("kit:808", 0.6).hit("kick", 0)
        return s

    def disarm(self):                                # vinyl stop
        s = self.score()
        self.keys(s, "D4 F4 A4 C5 E5", 0, 0.9, 0.6, bend=-12, glide=0.8)
        s.track("syn:sub", 0.7).note("D2", 0, 0.8, 0.9, bend=-12, glide=0.8)
        return s

    def yes(self):
        s = self.score()
        s.track("fx:sim_tap").note("F#6", 0, 0.08, 0.9)
        s.track("fx:sim_tap").note("F#6", 0.11, 0.08, 0.8)
        s.track("fm:kalimba", 0.7).note("A6", 0.2, 0.3, 0.8)
        return s

    def no(self):
        s = self.score()
        s.track("fx:sim_page", 0.9).note("C5", 0, 0.28, 0.9)
        s.track("fm:epiano", 0.6).note("F3", 0.12, 0.35, 0.8)
        return s

    def found(self):
        s = self.score()
        s.track("fm:kalimba").seq("D6 F6 A6 C7 E7", 0.06)
        self.keys(s, "F4 A4 C5 E5", 0.1, 0.5, 0.4)
        return s

    def lost(self):
        s = self.score()
        tr = s.track("fm:epiano", 0.7)
        tr.seq("E5 C5 A4", 0.13, vel=0.8)
        tr.note("F4", 0.39, 0.5, 0.8, bend=-5, glide=0.45)
        return s

    def lowbat(self):
        s = self.score(fx=[("lp", {"fc": 6000}), ("wobble", {"depth": 0.002})])
        s.track("fm:epiano").seq("A5 F5 A5 F5 R A5 F5 A5 F5", 0.09, vel=1.0)
        return s

    def critbat(self):                               # clean, bright, no haze
        s = self.score(fx=[])
        b = s.track("fm:bell")
        for i in range(4):
            b.note("E7", i * 0.2, 0.07, 1.0, decay=0.035)
            b.note("A6", i * 0.2 + 0.06, 0.05, 0.8, decay=0.03)
        return s

    def signal_crit(self):
        s = self.score(fx=[])
        b = s.track("fm:bell")
        for i in range(5):
            b.note("D7", i * 0.16, 0.06, 1.0, decay=0.03)
        return s

    def signal_warn(self):
        s = self.score()
        s.track("fm:kalimba").seq("A6 F6 R A6 F6", 0.1)
        return s

    def home(self):
        s = self.score()
        self.keys(s, "Bb3 D4 F4 A4 C5", 0, 0.5)
        self.keys(s, "C4 E4 G4 B4 D5", 0.5, 1.0)
        s.track("fm:kalimba", 0.5).seq("D6 E6 G6 B6*4", 0.1, 0.5)
        s.track("kit:808", 0.6).hit("kick", 0.5)
        return s

    def idle(self):
        s = self.score()
        s.track("fx:sim_page", 0.7).note("C5", 0, 0.3, 0.8)
        s.track("fm:kalimba", 0.6).seq("R*3 A6 F6", 0.13)
        return s
