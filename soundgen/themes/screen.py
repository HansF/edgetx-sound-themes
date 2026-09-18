"""Screen & story: cinematic themes. All melodies are original."""
import numpy as np

from .. import synth as S
from ..render import inst
from ..theme import Theme, HARM_MINOR, MINOR, MAJOR, DORIAN, MIXOLYDIAN, WHOLE, PHRYGIAN

# ---------------------------------------------------------------- local instruments & fx


def _rotor(dur, f, vel):
    """Helicopter rotor: low filtered noise pulses at ~12 Hz."""
    n = S.n_samples(dur)
    t = S.t_axis(n)
    rate = 12.0
    ph = (t * rate) % 1.0
    pulses = np.exp(-ph / 0.18)
    x = S.lp(S.noise(n), 220) * 5 * pulses + S.sine(np.full(n, 42.0)) * pulses * 0.5
    return x * S.adsr(n, 0.05, release=0.08) * vel


def _shimmer(dur, f, vel):
    """Transporter-style shimmer: many high sines with random AM + rising noise sheen."""
    n = S.n_samples(dur)
    t = S.t_axis(n)
    x = np.zeros(n)
    for k in range(10):
        fk = f * S.rng.uniform(1.0, 4.0)
        am = 0.5 + 0.5 * np.sin(2 * np.pi * S.rng.uniform(15, 40) * t + S.rng.uniform(0, 6))
        x += np.sin(2 * np.pi * fk * t) * am
    x = x / 5 + S.bp(S.noise(n), 5000, 1.2) * 0.6
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.2
    return x * env * vel


def _chirp(dur, f, vel):
    """Communicator chirp: fast up-down FM warble."""
    n = S.n_samples(dur)
    t = S.t_axis(n) / dur
    ff = f * (1 + 1.2 * np.sin(np.pi * t) ** 2)
    return S.fm(ff, 2.0, 1.5) * np.sin(np.pi * t) ** 0.5 * vel


def _hum(dur, f, vel):
    """Viewscreen / engine hum: detuned low sines + filtered noise."""
    n = S.n_samples(dur)
    x = S.sine(np.full(n, f)) + 0.6 * S.sine(np.full(n, f * 1.503)) + 0.3 * S.sine(np.full(n, f * 2.01))
    x += S.lp(S.noise(n), 300) * 0.8
    return x * S.adsr(n, 0.15, release=0.2) * vel


def _thunder(dur, f, vel):
    n = S.n_samples(max(dur, 1.0))
    t = S.t_axis(n)
    crack = S.hp(S.noise(n), 2000) * np.exp(-t / 0.03)
    roll = S.lp(S.noise(n), 180) * 6 * (np.exp(-t / 0.5)) * (0.6 + 0.4 * np.sin(2 * np.pi * 3 * t) ** 2)
    return S.drive(crack * 0.8 + roll, 1.5) * vel


def _creak(dur, f, vel):
    """Creaky door: slow stick-slip pulses through resonances."""
    n = S.n_samples(dur)
    t = S.t_axis(n) / dur
    rate = 25 + 60 * np.sin(np.pi * t)
    clicks = (np.diff(np.concatenate([[0], np.floor(np.cumsum(rate / S.SR))])) > 0).astype(float)
    src = S.lp(clicks, 6000) * 8 + S.noise(n) * 0.02
    x = S.bp(src, f, 12) + S.bp(src, f * 2.7, 10) * 0.6 + S.bp(src, f * 5.1, 8) * 0.3
    return x * np.sin(np.pi * t) ** 0.4 * vel


S.FX["scr_rotor"] = _rotor
S.FX["scr_shimmer"] = _shimmer
S.FX["scr_chirp"] = _chirp
S.FX["scr_hum"] = _hum
S.FX["scr_thunder"] = _thunder
S.FX["scr_creak"] = _creak

inst("syn:scr-blip", env=(0.002, 0, 1, 0.012), gm=80)(lambda f, n, note: S.sine(f) + 0.2 * S.tri(f * 2))
inst("syn:scr-stab", env=(0.002, 0.18, 0.0, 0.03), gm=81)(
    lambda f, n, note: S.bitcrush(S.drive(S.supersaw(f, 0.01, 5), 2.5), 6, 3))
inst("syn:scr-arp", env=(0.002, 0.09, 0.0, 0.02), gm=81)(
    lambda f, n, note: S.lp(S.supersaw(f, 0.008, 3), 3800, 1.4))
inst("syn:scr-pad", env=(0.03, 0, 1, 0.08), gm=89)(
    lambda f, n, note: S.lp(S.supersaw(f, 0.01, 5), 1600) * (0.35 + 0.65 * np.clip((S.t_axis(n) % 0.25) / 0.12, 0, 1)))
inst("syn:scr-power", env=(0.003, 0.25, 0.3, 0.05), gm=30)(
    lambda f, n, note: S.lp(S.drive(S.saw(f) + S.saw(f * 1.498) + S.saw(f * 0.5), 4), 3200))
inst("syn:scr-klax", env=(0.004, 0, 1, 0.012), gm=81)(
    lambda f, n, note: S.bp(S.pulse(f, 0.5) + 0.6 * S.saw(f * 1.498), 1100, 0.9) * 2.2)
inst("syn:scr-ghost", env=(0.25, 0, 1, 0.35), gm=91)(
    lambda f, n, note: S.formant(S.supersaw(f, 0.012, 3), "o", 5) * 3 + 0.2 * S.sine(f * 2))
inst("syn:scr-bell", env=(0.001, 0.5, 0, 0.02), gm=14)(
    lambda f, n, note: S.fm(f, 3.5, 2.0 * np.exp(-S.t_axis(n) / 0.3)))


# ---------------------------------------------------------------- Wizard Academy

class WizardAcademy(Theme):
    id = "wizard-academy"
    name = "Wizard Academy"
    category = "screen"
    tagline = "Celesta, candlelight and a moving staircase."
    blurb = ("A minor-key waltz for celesta, harp, strings and horns, the sound of an old castle school "
             "at night. Sparkling glissandi when you arm, a hushed choir when the link drops.")
    skin = {"bg": "#1b1426", "surface": "#2a2038", "ink": "#f3e9d2", "muted": "#b9a98a",
            "accent": "#d4a64a", "font": "Cinzel"}
    root, scale, step = "E5", HARM_MINOR, 0.14
    lead, alt, bass, kit = "gm:8", "gm:46", "gm:48", "kit:acoustic"
    master = [("reverb", {"size": 1.6, "wet": 0.35, "predelay": 0.02})]

    def sparkle(self, s, t, up=True, n=10, vol=0.45):
        pitches = [self.deg(i, 1) for i in range(n)]
        if not up:
            pitches = pitches[::-1]
        s.track("gm:46", vol).arp(pitches, 0.028, t, vel=0.6)

    def startup(self):
        s = self.score()
        st = 0.16  # 3/8 waltz feel
        cel = s.track("gm:8")
        cel.seq("B4 E5 G5 F#5*2 E5 D#5 E5 B5*3", st, vel=0.8)
        strings = s.track("gm:48", 0.5)
        strings.chord("E3+B3+G4", 0, st * 3, 0.6)
        strings.chord("D#3+B3+F#4", st * 3, st * 3, 0.6)
        strings.chord("E3+B3+E4+G4", st * 6, st * 4, 0.65)
        s.track("gm:60", 0.45).note("B3", st * 6, st * 4, 0.6)
        self.sparkle(s, st * 7.5, n=12, vol=0.35)
        return s

    def arm(self):
        s = self.score()
        self.sparkle(s, 0, n=14, vol=0.6)
        s.track("gm:8").seq("E6 G6 B6*3", 0.11, 0.35, vel=0.9)
        s.track("gm:48", 0.55).chord("E4+G4+B4", 0.35, 0.8, 0.7)
        s.track("gm:60", 0.5).chord("E3+B3", 0.35, 0.8, 0.7)
        return s

    def disarm(self):
        s = self.score()
        self.sparkle(s, 0, up=False, n=10, vol=0.45)
        s.track("gm:8").seq("B5 G5 F#5 E5*3", 0.12, 0.25, vel=0.7)
        s.track("gm:48", 0.5).chord("E3+B3+G4", 0.25, 0.9, 0.5)
        return s

    def yes(self):
        s = self.score()
        s.track("gm:8").arp(["B5", "E6"], 0.09, vel=0.85)
        s.track("gm:46", 0.4).chord("E5+B5", 0, 0.4, 0.6)
        return s

    def no(self):
        s = self.score()
        s.track("gm:8").arp(["G5", "D#5"], 0.12, vel=0.75)
        s.track("gm:48", 0.45).chord("C4+D#4", 0, 0.35, 0.5)
        return s

    def found(self):
        s = self.score()
        self.sparkle(s, 0, n=8, vol=0.5)
        s.track("gm:8").seq("E6 F#6 G6 B6*2", 0.07, 0.22)
        s.track("gm:48", 0.45).chord("E4+G4+B4", 0.22, 0.5)
        return s

    def lost(self):
        s = self.score()
        s.track("gm:52", 0.7).chord("E4+G4+C5", 0, 0.7, 0.6)
        s.track("gm:8").seq("C6 B5 Bb5 A5", 0.13, vel=0.7)
        return s

    def lowbat(self):
        s = self.score(fx=[("reverb", {"size": 0.8, "wet": 0.2})])
        s.track("gm:8").seq("E6 D#6 E6 R C6 B5 C6 R", 0.075, gap=0.25)
        s.track("gm:48", 0.4).chord("A3+C4+E4", 0, 0.6, 0.5)
        return s

    def critbat(self):
        s = self.score(fx=[])
        cel = s.track("fm:celesta")
        for i, p in enumerate(["E7", "D#7", "E7", "D#7"]):
            cel.note(p, i * 0.19, 0.07, 1.0, decay=0.04)
        s.track("syn:scr-bell", 0.5).arp(["B6", "B6", "B6", "B6"], 0.19, gap=0.65, decay=0.04)
        return s

    def signal_warn(self):
        s = self.score(fx=[("reverb", {"size": 0.8, "wet": 0.2})])
        s.track("gm:8").seq("B5 G5 B5 G5", 0.1, gap=0.3)
        return s

    def signal_crit(self):
        s = self.score(fx=[])
        tr = s.track("fm:celesta")
        for i in range(4):
            tr.note("F#6", i * 0.16, 0.05, 1.0, decay=0.03)
            tr.note("C7", i * 0.16 + 0.05, 0.04, 0.9, decay=0.03)
        return s

    def warn_a(self):
        s = self.score()
        s.track("gm:46", 0.8).arp([self.deg(i) for i in range(0, 8)], 0.02)
        s.track("gm:8").note("B5", 0.16, 0.25)
        return s

    def warn_b(self):
        s = self.score()
        s.track("gm:46", 0.8).arp([self.deg(i) for i in range(7, -1, -1)], 0.02)
        s.track("gm:8").arp(["D#6", "E6"], 0.1, 0.16)
        return s

    def error(self):
        s = self.score()
        s.track("gm:48", 0.8).chord("C3+F#3", 0, 0.45, 0.7)
        s.track("gm:60", 0.6).note("C3", 0, 0.45, 0.7)
        return s

    def home(self):
        s = self.score()
        s.track("gm:60").seq("B3 E4 G4 B4*3", 0.15)
        s.track("gm:48", 0.5).chord("E3+B3+G4", 0.0, 1.2, 0.6)
        self.sparkle(s, 0.45, n=10, vol=0.35)
        return s

    def idle(self):
        s = self.score()
        s.track("syn:musicbox", 0.8).seq("E6 B5 G5 R E6 B5 G5", 0.14)
        return s

    def launch(self):
        s = self.score()
        self.sparkle(s, 0, n=21, vol=0.6)
        s.track("gm:48", 0.5).chord("B3+E4+G4", 0.2, 0.7, 0.5)
        s.track("gm:48", 0.5).note("B3", 0.0, 0.9, 0.5, bend=12)
        return s

    def land(self):
        s = self.score()
        self.sparkle(s, 0, up=False, n=18, vol=0.55)
        s.track("gm:47", 0.8).note("E2", 0.55, 0.3)
        return s


# ---------------------------------------------------------------- Chopper Command '84

class ChopperCommand(Theme):
    id = "chopper-command-84"
    name = "Chopper Command '84"
    category = "screen"
    tagline = "Rotor wash, synth brass, a mission briefing at dusk."
    blurb = ("Heroic analog brass over a driving octave bass and gated drums, straight from a Sunday-night "
             "action series about a stealth helicopter. The rotor spins up when you arm.")
    skin = {"bg": "#0d1b2a", "surface": "#16283d", "ink": "#e8eef5", "muted": "#8fa3b8",
            "accent": "#f2a900", "font": "Audiowide"}
    root, scale, step = "D5", DORIAN, 0.1
    lead, alt, bass, kit = "syn:brass", "syn:lead", "syn:bass", "kit:909"
    master = []

    GATED = [("reverb", {"size": 0.8, "wet": 0.5, "gate": 0.18})]

    def drums(self, s, pattern, st, t=0.0, vol=0.8):
        s.track("kit:909", vol, self.GATED).beat(pattern, st, t)

    def octbass(self, s, notes, st, t=0.0, vol=0.7):
        tr = s.track("syn:bass", vol)
        for i, p in enumerate(notes):
            tr.note(p, t + 2 * i * st, st * 0.8, 0.85)
            tr.note(p + 12, t + (2 * i + 1) * st, st * 0.8, 0.7)

    def startup(self):
        s = self.score()
        st = 0.08
        s.track("fx:scr_rotor", 0.5).note("C3", 0, 1.9, 0.8)
        self.octbass(s, [38] * 4 + [36] * 2 + [41] * 2, st * 1.0)
        br = s.track("syn:brass")
        br.seq("D5*2 A5*2 G5 F5 G5*2 R", st * 1.3, 0.2)
        br.chord("A5+D6", 1.05, 0.7, 0.9)
        s.track("syn:brass", 0.6).chord("F4+A4", 1.05, 0.7, 0.8)
        self.drums(s, {"kick": "x...x...x...x...", "snare": "....x.......x..X"}, st, 0.0)
        return s

    def arm(self):
        s = self.score()
        s.track("fx:scr_rotor", 0.6).note("C3", 0, 1.1, 0.9)
        s.track("syn:scr-power", 0.9).chord("D3+A3+D4", 0, 0.16)
        s.track("syn:scr-power", 0.9).chord("F3+C4+F4", 0.18, 0.16)
        s.track("syn:scr-power", 0.9).chord("G3+D4+G4", 0.36, 0.5)
        s.track("syn:brass").seq("A5 C6 D6*4", 0.12, 0.36)
        self.drums(s, {"kick": "x.x.x", "snare": "....X"}, 0.09)
        return s

    def disarm(self):
        s = self.score()
        s.track("fx:scr_rotor", 0.5).note("C3", 0, 0.9, 0.7)
        s.track("syn:brass").seq("D6 A5 F5 D5*4", 0.12)
        s.track("syn:bass", 0.7).note("D3", 0.36, 0.5, bend=-12)
        return s

    def yes(self):
        s = self.score()
        s.track("syn:scr-power", 0.9).chord("D4+A4+D5", 0, 0.1)
        s.track("syn:scr-power", 0.9).chord("G4+D5+G5", 0.12, 0.2)
        s.track("kit:909", 0.7, self.GATED).hit("snare", 0.12)
        return s

    def no(self):
        s = self.score()
        s.track("syn:scr-power", 0.9).chord("G3+D4+G4", 0, 0.1)
        s.track("syn:scr-power", 0.9).chord("D3+A3+D4", 0.12, 0.22)
        s.track("kit:909", 0.7).hit("kick", 0.12)
        return s

    def found(self):
        s = self.score()
        s.track("syn:brass").seq("D5 F5 A5 D6*3", 0.09)
        self.octbass(s, [38, 38], 0.06)
        return s

    def lost(self):
        s = self.score()
        s.track("syn:brass").seq("A5 G5 F5 E5*3", 0.1)
        s.track("fx:scr_rotor", 0.5).note("C3", 0.1, 0.6, 0.6)
        return s

    def lowbat(self):
        s = self.score()
        br = s.track("syn:scr-power", 0.8)
        for i, p in enumerate(["A3+E4", "G3+D4", "F3+C4"]):
            br.chord(p, i * 0.2, 0.12)
        s.track("kit:909", 0.7).beat({"kick": "x.x.x."}, 0.1)
        return s

    def critbat(self):
        s = self.score(fx=[])
        tr = s.track("syn:lead")
        for i in range(4):
            tr.note("A6", i * 0.2, 0.06, 1.0)
            tr.note("D7", i * 0.2 + 0.07, 0.06, 1.0)
        s.track("kit:909", 0.6).beat({"kick": "x.x.x.x."}, 0.1)
        return s

    def signal_warn(self):
        s = self.score()
        s.track("syn:lead").seq("D6 R A5 R D6 R A5", 0.07, gap=0.2)
        return s

    def signal_crit(self):
        s = self.score(fx=[])
        s.track("syn:lead").seq("E6 A6 R " * 4, 0.05, gap=0.1)
        return s

    def launch(self):
        s = self.score()
        s.track("fx:scr_rotor", 0.8).note("C3", 0, 1.5, 1.0)
        s.track("syn:brass").note("D4", 0.1, 1.0, bend=12, glide=0.7)
        s.track("syn:brass", 0.6).note("A4", 0.1, 1.0, bend=12, glide=0.7)
        self.drums(s, {"tom1": "x.", "tom2": "..x.", "tom3": "....x.", "crash": "......X"}, 0.12, 0.2)
        return s

    def land(self):
        s = self.score()
        s.track("fx:scr_rotor", 0.8).note("C3", 0, 1.3, 1.0)
        s.track("syn:brass").note("A5", 0, 1.0, bend=-12, glide=0.9)
        s.track("kit:909", 0.8, self.GATED).hit("kick", 1.05)
        return s

    def home(self):
        s = self.score()
        s.track("syn:brass").seq("D5 A5 G5*2 A5 D6*4", 0.1)
        self.octbass(s, [38, 38, 36, 38], 0.1)
        self.drums(s, {"kick": "x...x...", "snare": "..x...X."}, 0.1)
        return s

    def flip(self):
        s = self.score()
        s.track("fx:whoosh", 0.8).note("A5", 0, 0.45)
        s.track("syn:scr-power").chord("D4+A4", 0.3, 0.2)
        return s

    def cut(self):
        s = self.score()
        s.track("kit:909", 0.9, self.GATED).hit("snare", 0)
        s.track("syn:scr-power").chord("D3+A3", 0, 0.25)
        return s

    def thr_on(self):
        s = self.score()
        s.track("fx:scr_rotor", 0.8).note("C3", 0, 0.5)
        s.track("syn:brass", 0.7).note("A4", 0.05, 0.3, bend=5)
        return s


# ---------------------------------------------------------------- Starship Bridge

class StarshipBridge(Theme):
    id = "starship-bridge"
    name = "Starship Bridge"
    category = "screen"
    tagline = "Computer working. Please state the nature of your emergency."
    blurb = ("Burbling bridge computers, communicator chirps and a whooping alert klaxon from a sixties "
             "TV starship. Arming sounds like the warp core coming online.")
    skin = {"bg": "#101418", "surface": "#1b2229", "ink": "#e6f1ff", "muted": "#8aa0b4",
            "accent": "#ff9c1a", "font": "Orbitron"}
    root, scale, step = "A5", MAJOR, 0.06
    lead, alt, bass, kit = "syn:scr-blip", "syn:sine", "syn:sub", "kit:808"

    def computer(self, s, t, n=8, seed=0, vol=0.8):
        r = np.random.default_rng(seed)
        tr = s.track("syn:scr-blip", vol)
        for i in range(n):
            tr.note(float(r.choice([81, 84, 86, 88, 91, 93, 96])), t + i * 0.045, 0.035, 0.8)
        return t + n * 0.045

    def startup(self):
        s = self.score()
        s.track("fx:scr_hum", 0.6).note("A2", 0, 1.8, 0.9)
        t = self.computer(s, 0.15, 10, seed=3)
        s.track("fx:scr_shimmer", 0.5).note("A6", 0.3, 1.0)
        s.track("syn:sine", 0.8).seq("E6 A6*2 C#7*4", 0.1, t + 0.1)
        return s

    def arm(self):                            # warp core online
        s = self.score()
        s.track("fx:scr_hum", 0.8).note("A2", 0, 1.3, 1.0)
        s.track("syn:sine", 0.7).note("A3", 0, 1.0, bend=24, glide=0.8)
        s.track("syn:sine", 0.5).note("E4", 0, 1.0, bend=24, glide=0.8)
        s.track("fx:whoosh", 0.7).note("A5", 0.7, 0.6)
        return s

    def disarm(self):                         # powering down
        s = self.score()
        s.track("fx:scr_hum", 0.8).note("A2", 0, 1.0, 1.0)
        s.track("syn:sine", 0.7).note("A5", 0, 0.9, bend=-24, glide=0.8)
        s.track("syn:scr-blip", 0.8).seq("E6 C6 A5", 0.08, 0.6)
        return s

    def yes(self):                            # communicator chirp
        s = self.score()
        s.track("fx:scr_chirp", 0.9).note("C#6", 0, 0.14)
        s.track("syn:scr-blip", 0.6).note("A6", 0.15, 0.06)
        return s

    def no(self):
        s = self.score()
        s.track("syn:scr-blip").seq("E5 R A4*2", 0.07)
        return s

    def found(self):
        s = self.score()
        self.computer(s, 0, 6, seed=7)
        s.track("fx:scr_chirp", 0.8).note("A6", 0.3, 0.16)
        return s

    def lost(self):
        s = self.score()
        s.track("fx:static", 0.6).note("C5", 0, 0.3)
        s.track("syn:sine").note("E6", 0.3, 0.5, bend=-12)
        return s

    def lowbat(self):
        s = self.score()
        k = s.track("syn:scr-klax", 0.8)
        k.note("A4", 0, 0.28, bend=5, glide=0.2)
        self.computer(s, 0.4, 5, seed=11, vol=0.6)
        return s

    def critbat(self):                        # red alert, x3
        s = self.score()
        k = s.track("syn:scr-klax")
        for i in range(3):
            k.note("F4", i * 0.37, 0.28, 1.0, bend=7, glide=0.22)
        return s

    def signal_warn(self):
        s = self.score()
        s.track("syn:scr-blip").seq("C#7 A6 C#7 A6", 0.09, gap=0.4)
        return s

    def signal_crit(self):
        s = self.score()
        k = s.track("syn:scr-klax", 0.9)
        for i in range(4):
            k.note("A4", i * 0.24, 0.16, 1.0, bend=5, glide=0.12)
        return s

    def warn_a(self):
        s = self.score()
        self.computer(s, 0, 6, seed=5)
        return s

    def warn_b(self):
        s = self.score()
        self.computer(s, 0, 4, seed=9)
        s.track("syn:scr-klax", 0.7).note("A4", 0.2, 0.25, bend=5)
        return s

    def error(self):
        s = self.score()
        s.track("fx:static", 0.6).note("C5", 0, 0.2)
        s.track("syn:scr-blip").seq("C5 R C5", 0.1, 0.22)
        return s

    def launch(self):                         # warp jump
        s = self.score()
        s.track("fx:riser", 0.7).note("A3", 0, 0.9)
        s.track("fx:whoosh", 1.0).note("C6", 0.85, 0.5)
        s.track("syn:sine", 0.6).note("A6", 0.85, 0.4, bend=12)
        return s

    def land(self):
        s = self.score()
        s.track("fx:scr_shimmer", 0.8).note("A6", 0, 1.2)
        s.track("syn:sine", 0.6).note("A6", 0.1, 1.0, bend=-12)
        return s

    def home(self):
        s = self.score()
        s.track("fx:scr_shimmer", 0.7).note("E6", 0, 1.2)
        s.track("syn:sine").seq("A5 E6 A6*4", 0.12, 0.2)
        return s

    def idle(self):
        s = self.score()
        self.computer(s, 0, 5, seed=21, vol=0.6)
        self.computer(s, 0.6, 5, seed=22, vol=0.6)
        return s

    def count(self, n, base=0):
        s = self.score()
        s.track("syn:scr-blip").arp([self.deg(base + i, 1) for i in range(n)], 0.1, gap=0.4)
        return s

    def flip(self):
        s = self.score()
        s.track("fx:scr_chirp").note("E6", 0, 0.12)
        s.track("fx:scr_chirp").note("E6", 0.14, 0.12)
        s.track("fx:scr_chirp").note("E6", 0.28, 0.12)
        return s

    def thr_on(self):
        s = self.score()
        s.track("fx:scr_hum", 0.7).note("A2", 0, 0.5)
        s.track("syn:sine", 0.5).note("A4", 0, 0.4, bend=7)
        return s

    def cut(self):
        s = self.score()
        s.track("fx:scr_hum", 0.7).note("A2", 0, 0.35, bend=-7)
        s.track("syn:scr-blip").note("A4", 0.05, 0.1)
        return s


# ---------------------------------------------------------------- Imperial Fleet

class ImperialFleet(Theme):
    id = "imperial-fleet"
    name = "Imperial Fleet"
    category = "screen"
    tagline = "Brass, timpani and a very large ship overhead."
    blurb = ("A full space-opera orchestra: marching snare, timpani rolls, trumpets and trombones. Heroic "
             "major fanfares when things go right, dark minor brass when they don't.")
    skin = {"bg": "#0a0a0f", "surface": "#15151d", "ink": "#f4f1ea", "muted": "#9c9aa6",
            "accent": "#c8102e", "font": "Oswald"}
    root, scale, step = "C5", MAJOR, 0.13
    lead, alt, bass, kit = "gm:56", "gm:57", "gm:48", "kit:acoustic"
    master = [("reverb", {"size": 1.4, "wet": 0.28, "predelay": 0.02})]

    def timp(self, s, notes, t=0.0, vol=0.9):
        tr = s.track("gm:47", vol)
        for i, (p, dt) in enumerate(notes):
            tr.note(p, t + dt, 0.3, 0.9)

    def roll(self, s, t, dur, vol=0.6):
        tr = s.track("kit:acoustic", vol)
        k = int(dur / 0.035)
        for i in range(k):
            tr.hit("snare", t + i * 0.035, 0.35 + 0.6 * i / k)

    def startup(self):
        s = self.score()
        self.roll(s, 0, 0.35)
        br = s.track("gm:56")
        br.seq("G4. G4. C5*2 G5*3", 0.12, 0.35, vel=0.9)
        s.track("gm:57", 0.8).chord("C4+E4+G4", 0.35 + 0.12 * 4, 0.7, 0.85)
        s.track("gm:48", 0.7).chord("C3+G3+C4", 0.35 + 0.12 * 4, 0.8, 0.8)
        self.timp(s, [("C3", 0.35 + 0.12 * 4), ("G2", 0.35 + 0.12 * 6)])
        return s

    def arm(self):
        s = self.score()
        self.roll(s, 0, 0.25)
        s.track("gm:56").seq("C5 E5 G5 C6*4", 0.1, 0.25, vel=1.0)
        s.track("gm:57", 0.8).chord("C4+G4+C5", 0.55, 0.6, 0.9)
        s.track("gm:61", 0.6).chord("E4+G4", 0.55, 0.6, 0.8)
        self.timp(s, [("C3", 0.55)])
        return s

    def disarm(self):
        s = self.score()
        s.track("gm:57").seq("G3 Eb3 C3*4", 0.16, vel=0.9)
        s.track("gm:48", 0.7).chord("C2+G2+Eb3", 0.3, 0.8, 0.8)
        self.timp(s, [("C3", 0.0), ("C3", 0.32)])
        return s

    def yes(self):
        s = self.score()
        s.track("gm:56").seq("G5. C6*2", 0.1, vel=0.9)
        return s

    def no(self):
        s = self.score()
        s.track("gm:57").seq("Eb4. C4*2", 0.12, vel=0.85)
        self.timp(s, [("C3", 0.12)], vol=0.6)
        return s

    def found(self):
        s = self.score()
        s.track("gm:56").seq("C5. E5. G5. C6*3", 0.09, vel=0.95)
        s.track("gm:61", 0.6).chord("C4+G4", 0.27, 0.4, 0.8)
        return s

    def lost(self):
        s = self.score()
        s.track("gm:57").seq("C4 Ab3 F3 Db3*3", 0.13, vel=0.85)
        s.track("gm:48", 0.6).chord("F2+C3", 0.1, 0.6, 0.7)
        return s

    def lowbat(self):                         # low brass ostinato
        s = self.score(fx=[("reverb", {"size": 0.8, "wet": 0.2})])
        s.track("gm:57").seq("C3. C3. C3. Ab2*2 R Eb3. C3*2", 0.09, vel=0.9)
        return s

    def critbat(self):
        s = self.score(fx=[])
        tr = s.track("kit:acoustic")
        br = s.track("syn:brass", 0.9)
        for i in range(4):
            t = i * 0.22
            br.chord("C5+F#5", t, 0.09, 1.0)
            tr.hit("snare", t, 1.0)
        return s

    def signal_warn(self):
        s = self.score(fx=[("reverb", {"size": 0.6, "wet": 0.15})])
        s.track("gm:56").seq("G5. R E5. R G5. R E5.", 0.08, vel=0.85)
        return s

    def signal_crit(self):
        s = self.score(fx=[])
        br = s.track("syn:brass")
        for i in range(4):
            br.chord("A5+Eb6", i * 0.2, 0.08, 1.0)
        s.track("kit:acoustic", 0.8).beat({"snare": "x....x....x....x"}, 0.05)
        return s

    def warn_a(self):
        s = self.score()
        self.roll(s, 0, 0.3, 0.8)
        s.track("gm:56").note("G5", 0.3, 0.2, 0.9)
        return s

    def warn_b(self):
        s = self.score()
        self.roll(s, 0, 0.3, 0.8)
        s.track("gm:56").seq("G5. D6*2", 0.1, 0.3)
        return s

    def error(self):
        s = self.score()
        s.track("gm:57").chord("C3+F#3", 0, 0.4, 0.9)
        self.timp(s, [("C3", 0.0)])
        return s

    def home(self):
        s = self.score()
        self.roll(s, 0, 0.3)
        s.track("gm:56").seq("G4 C5 E5 G5*2 E5 G5 C6*4", 0.1, 0.3)
        s.track("gm:48", 0.6).chord("C3+G3+E4", 0.3, 1.1, 0.7)
        self.timp(s, [("C3", 0.3), ("G2", 0.9)])
        return s

    def launch(self):
        s = self.score()
        self.roll(s, 0, 0.8, 0.7)
        s.track("gm:48", 0.7).note("C3", 0, 0.9, 0.8, bend=12, glide=0.8)
        s.track("gm:56").chord("C5+G5", 0.8, 0.6, 1.0)
        s.track("kit:acoustic", 0.8).hit("crash", 0.8)
        return s

    def land(self):
        s = self.score()
        s.track("gm:57").seq("G4 E4 C4*4", 0.15)
        self.timp(s, [("G2", 0.3), ("C3", 0.45)])
        return s

    def cut(self):
        s = self.score()
        self.timp(s, [("C3", 0.0)])
        s.track("gm:57").note("C3", 0, 0.25)
        return s

    def thr_on(self):
        s = self.score()
        self.roll(s, 0, 0.25, 0.7)
        s.track("gm:56").note("C5", 0.25, 0.15)
        return s


# ---------------------------------------------------------------- Neon Grid

class NeonGrid(Theme):
    id = "neon-grid"
    name = "Neon Grid"
    category = "screen"
    tagline = "Chrome, rain, and a bassline that bites."
    blurb = ("Darksynth for night flights: detuned reese bass, pumping supersaw pads, distorted kicks "
             "and bitcrushed stabs. Glitches when the link breaks.")
    skin = {"bg": "#07060d", "surface": "#140f24", "ink": "#e9f7ff", "muted": "#8a86a8",
            "accent": "#ff2a6d", "font": "Share Tech Mono"}
    root, scale, step = "F#4", PHRYGIAN, 0.07
    lead, alt, bass, kit = "syn:scr-arp", "syn:scr-stab", "syn:reese", "kit:phonk"

    def kick(self, s, times, vol=0.9):
        tr = s.track("kit:phonk", vol, [("drive", {"amount": 2.5})])
        for t in times:
            tr.hit("kick", t)

    def startup(self):
        s = self.score(fx=[("reverb", {"size": 1.0, "wet": 0.2})])
        st = 0.07
        s.track("syn:scr-pad", 0.6).chord("F#3+A3+C#4+E4", 0, 1.6, 0.8)
        s.track("syn:reese", 0.8).note("F#2", 0, 1.6, 0.9)
        s.track("syn:scr-arp", 0.8).arp([66, 69, 73, 76, 78, 76, 73, 69] * 2, st, 0.0)
        self.kick(s, [0, 0.56, 1.12])
        s.track("syn:scr-stab", 0.8).chord("F#4+C#5", 1.12, 0.2)
        return s

    def arm(self):
        s = self.score()
        s.track("fx:riser", 0.6).note("F#3", 0, 0.5)
        self.kick(s, [0.5])
        s.track("syn:scr-stab").chord("F#4+A4+C#5", 0.5, 0.3)
        s.track("syn:reese", 0.9).note("F#2", 0.5, 0.6)
        return s

    def disarm(self):
        s = self.score()
        s.track("syn:reese", 0.9).note("F#2", 0, 0.8, bend=-12, glide=0.7)
        s.track("fx:glitch", 0.5).note("C5", 0.0, 0.3)
        s.track("syn:scr-stab", 0.7).chord("C#4+G4", 0.0, 0.15)
        return s

    def yes(self):
        s = self.score()
        s.track("syn:scr-stab").arp(["C#5", "F#5"], 0.08)
        return s

    def no(self):
        s = self.score()
        s.track("syn:scr-stab").arp(["G4", "F#3"], 0.08)
        self.kick(s, [0.08], 0.6)
        return s

    def found(self):
        s = self.score()
        s.track("syn:scr-arp").arp([66, 69, 73, 78, 81, 85], 0.05)
        self.kick(s, [0.3], 0.7)
        return s

    def lost(self):
        s = self.score()
        s.track("fx:glitch", 0.9).note("A4", 0, 0.45)
        s.track("syn:reese", 0.8).note("F#2", 0.2, 0.5, bend=-7)
        return s

    def lowbat(self):
        s = self.score()
        tr = s.track("syn:scr-stab", 0.9)
        for i, p in enumerate(["C#5+G5", "C5+F#5", "B4+F5"]):
            tr.chord(p, i * 0.22, 0.1)
        self.kick(s, [0, 0.22, 0.44], 0.6)
        return s

    def critbat(self):
        s = self.score()
        tr = s.track("syn:lead")
        stab = s.track("syn:scr-stab", 0.7)
        for i in range(4):
            tr.note("G6", i * 0.2, 0.08, 1.0)
            stab.chord("G4+C#5", i * 0.2, 0.08, 1.0)
        return s

    def signal_warn(self):
        s = self.score()
        s.track("syn:scr-stab").seq("F#5 R C#5 R F#5 R C#5", 0.06, gap=0.2)
        return s

    def signal_crit(self):
        s = self.score()
        tr = s.track("syn:lead")
        for i in range(4):
            tr.note("A6", i * 0.18, 0.05, 1.0)
            tr.note("G6", i * 0.18 + 0.055, 0.05, 1.0)
        return s

    def error(self):
        s = self.score()
        s.track("fx:glitch").note("C4", 0, 0.5)
        return s

    def warn_a(self):
        s = self.score()
        s.track("syn:scr-stab").chord("F#4+C5", 0, 0.12, bend=12, glide=0.12)
        return s

    def warn_b(self):
        s = self.score()
        s.track("fx:glitch", 0.6).note("C5", 0, 0.15)
        s.track("syn:scr-stab").chord("F#4+C5", 0.15, 0.2, bend=12)
        return s

    def launch(self):
        s = self.score()
        s.track("fx:riser").note("F#3", 0, 0.9)
        self.kick(s, [0.9])
        s.track("syn:scr-stab").chord("F#4+A4+C#5+E5", 0.9, 0.35)
        return s

    def land(self):
        s = self.score()
        s.track("syn:reese").note("F#3", 0, 0.9, bend=-12)
        s.track("fx:scr_hum", 0.4).note("F#2", 0, 0.9)
        self.kick(s, [0.9])
        return s

    def home(self):
        s = self.score()
        s.track("syn:scr-arp").arp([66, 73, 78, 81, 78, 73, 66, 73, 78, 85], 0.07)
        s.track("syn:scr-pad", 0.5).chord("F#3+C#4+A4", 0, 0.75)
        return s

    def cut(self):
        s = self.score()
        self.kick(s, [0])
        s.track("syn:reese", 0.8).note("F#2", 0, 0.25)
        return s

    def thr_on(self):
        s = self.score()
        s.track("syn:reese").note("F#2", 0, 0.35, bend=12, glide=0.2)
        s.track("kit:phonk", 0.6).hit("hat", 0)
        return s

    def flip(self):
        s = self.score()
        s.track("fx:laser", 0.9).note("C6", 0, 0.12)
        s.track("fx:laser", 0.9).note("C6", 0.14, 0.12)
        s.track("fx:glitch", 0.6).note("C5", 0.28, 0.15)
        return s

    def powerdown(self):
        s = self.score()
        s.track("syn:scr-pad", 0.7).chord("F#3+A3+C#4", 0, 0.8, bend=-24, glide=0.8)
        return s


# ---------------------------------------------------------------- Signal from Beyond

class SignalFromBeyond(Theme):
    id = "signal-from-beyond"
    name = "Signal from Beyond"
    category = "screen"
    tagline = "Something up there is answering."
    blurb = ("Theremin glides, whole-tone clusters and five-note signals from the night sky, with radio "
             "static and sonar pings. The truth is somewhere over the next hill.")
    skin = {"bg": "#0b1410", "surface": "#132219", "ink": "#d9f7e4", "muted": "#7fa38d",
            "accent": "#6dff9e", "font": "VT323"}
    root, scale, step = "C5", WHOLE, 0.14
    lead, alt, bass, kit = "syn:theremin", "syn:sine", "syn:sub", "kit:808"
    master = [("reverb", {"size": 1.5, "wet": 0.35, "predelay": 0.03})]

    SIGNAL = ["G5", "C#6", "A5", "D#5", "F6"]     # original five-note call

    def startup(self):
        s = self.score()
        s.track("fx:static", 0.35).note("C5", 0, 0.3)
        s.track("syn:sine", 0.8).arp(self.SIGNAL, 0.16, 0.3, gap=0.15)
        s.track("syn:theremin", 0.8).note("C5", 0.3, 1.1, bend=7, glide=0.9)
        s.track("syn:pad", 0.4).chord("C4+E4+G#4+A#4", 0.3, 1.2)
        return s

    def arm(self):
        s = self.score()
        s.track("syn:sine").arp(self.SIGNAL, 0.11, gap=0.1)
        s.track("syn:theremin", 0.6).note("F6", 0.55, 0.6, bend=5)
        return s

    def disarm(self):
        s = self.score()
        s.track("syn:sine").arp(self.SIGNAL[::-1], 0.11, gap=0.1)
        s.track("syn:theremin", 0.6).note("G4", 0.55, 0.6, bend=-7)
        return s

    def yes(self):
        s = self.score()
        s.track("fx:ping", 0.9).note("E6", 0, 0.1)
        s.track("syn:sine", 0.5).note("A#6", 0.08, 0.1)
        return s

    def no(self):
        s = self.score()
        s.track("syn:theremin").note("D5", 0, 0.35, bend=-5)
        return s

    def found(self):
        s = self.score()
        s.track("fx:static", 0.4).note("C5", 0, 0.15)
        s.track("syn:sine").arp(self.SIGNAL[:3], 0.1, 0.15)
        s.track("fx:ping", 0.7).note("A6", 0.45, 0.1)
        return s

    def lost(self):
        s = self.score()
        s.track("syn:theremin").note("F6", 0, 0.8, bend=-19, vib=0.5)
        s.track("fx:static", 0.5).note("C5", 0.5, 0.4)
        return s

    def lowbat(self):
        s = self.score(fx=[("reverb", {"size": 0.8, "wet": 0.2})])
        s.track("syn:theremin").seq("E5 R D5 R C5*2", 0.13, gap=0.2)
        return s

    def critbat(self):
        s = self.score(fx=[])
        tr = s.track("syn:sine")
        for i in range(4):
            tr.note("F#6", i * 0.18, 0.07, 1.0)
            tr.note("C7", i * 0.18 + 0.07, 0.05, 0.9)
        return s

    def signal_warn(self):
        s = self.score()
        s.track("fx:ping").note("C6", 0, 0.1)
        s.track("fx:ping").note("C6", 0.35, 0.1)
        return s

    def signal_crit(self):
        s = self.score(fx=[])
        tr = s.track("fx:static")
        for i in range(4):
            tr.note("C5", i * 0.2, 0.09, 1.0)
        s.track("syn:sine", 0.8).arp(["A#6"] * 4, 0.2, gap=0.6)
        return s

    def warn_a(self):
        s = self.score()
        s.track("syn:theremin").note("C5", 0, 0.3, bend=12, glide=0.25)
        return s

    def warn_b(self):
        s = self.score()
        s.track("syn:theremin").note("C5", 0, 0.45, bend=18, glide=0.35, vib=0.6)
        return s

    def error(self):
        s = self.score()
        s.track("fx:static").note("C5", 0, 0.4)
        s.track("syn:sub", 0.8).note("C3", 0, 0.4, vib=0.8, vib_rate=20)
        return s

    def idle(self):
        s = self.score()
        s.track("fx:ping").note("G5", 0, 0.1)
        s.track("fx:ping").note("C#6", 0.6, 0.1)
        return s

    def launch(self):
        s = self.score()
        s.track("syn:theremin").note("C4", 0, 1.1, bend=24, glide=0.9, vib=0.3)
        s.track("syn:pad", 0.4).chord("C4+E4+G#4", 0.2, 0.9)
        return s

    def land(self):
        s = self.score()
        s.track("syn:theremin").note("C6", 0, 1.0, bend=-24, glide=0.9)
        s.track("fx:ping", 0.7).note("C5", 1.0, 0.1)
        return s

    def home(self):
        s = self.score()
        s.track("syn:sine").arp(self.SIGNAL + ["G6"], 0.12)
        s.track("syn:pad", 0.4).chord("C4+E4+A#4", 0.2, 0.8)
        return s

    def flip(self):
        s = self.score()
        for i in range(3):
            s.track("syn:theremin", 0.8).note("C5", i * 0.14, 0.12, bend=12)
        return s

    def count(self, n, base=0):
        s = self.score(fx=[("reverb", {"size": 0.6, "wet": 0.15})])
        s.track("syn:sine").arp([self.deg(base + i, 0) for i in range(n)], 0.12, decay=0.1)
        return s


# ---------------------------------------------------------------- Haunted Manor

class HauntedManor(Theme):
    id = "haunted-manor"
    name = "Haunted Manor"
    category = "screen"
    tagline = "The music box is playing again. Nobody wound it."
    blurb = ("A minor-key music box, a wheezing pipe organ and a choir that isn't there. Thunder when "
             "you arm, a heartbeat when the battery runs low.")
    skin = {"bg": "#120c10", "surface": "#1f151b", "ink": "#efe3e8", "muted": "#a3909a",
            "accent": "#9dff5c", "font": "Creepster"}
    root, scale, step = "D5", HARM_MINOR, 0.16
    lead, alt, bass, kit = "syn:musicbox", "gm:19", "syn:organ", "kit:acoustic"
    master = [("reverb", {"size": 1.8, "wet": 0.4, "predelay": 0.03})]

    def startup(self):
        s = self.score()
        s.track("syn:musicbox").seq("A5 D6 F6 E6 D6 C#6 D6 A5*2", 0.15)
        s.track("syn:musicbox", 0.5).seq("D5*3 A4*3 D5*3", 0.15)
        s.track("syn:scr-ghost", 0.35).chord("D4+F4+A4", 0.3, 1.2)
        return s

    def arm(self):
        s = self.score()
        s.track("fx:scr_thunder", 0.9).note("C3", 0, 1.2)
        s.track("gm:19", 0.7).chord("D3+A3+D4+F4", 0.1, 1.0)
        return s

    def disarm(self):
        s = self.score()
        s.track("fx:scr_creak", 0.8).note("C5", 0, 0.8)
        s.track("syn:musicbox").seq("F5 E5 D5 C#5", 0.12, 0.2)
        return s

    def yes(self):
        s = self.score()
        s.track("syn:musicbox").arp(["A5", "D6"], 0.1)
        return s

    def no(self):
        s = self.score()
        s.track("syn:organ", 0.8).chord("D3+G#3", 0, 0.35)
        return s

    def found(self):
        s = self.score()
        s.track("syn:scr-ghost", 0.6).chord("D5+F5+A5", 0, 0.7)
        s.track("syn:musicbox").arp(["D6", "F6", "A6"], 0.1)
        return s

    def lost(self):
        s = self.score()
        s.track("syn:theremin", 0.8).note("A5", 0, 0.8, bend=-13, vib=0.7)
        return s

    def lowbat(self):
        s = self.score(fx=[("reverb", {"size": 0.8, "wet": 0.2})])
        s.track("fx:heartbeat").note("C2", 0, 0.5)
        s.track("fx:heartbeat").note("C2", 0.55, 0.5)
        return s

    def critbat(self):
        s = self.score(fx=[])
        tr = s.track("fx:heartbeat")
        for i in range(3):
            tr.note("C2", i * 0.33, 0.3, 1.0)
        s.track("syn:musicbox", 0.8).arp(["G#6", "G#6", "G#6"], 0.33, 0.02, gap=0.7, decay=0.06)
        return s

    def signal_warn(self):
        s = self.score()
        s.track("syn:musicbox").seq("D6 R G#5 R D6", 0.1)
        return s

    def signal_crit(self):
        s = self.score(fx=[])
        tr = s.track("syn:organ")
        for i in range(4):
            tr.chord("D5+G#5", i * 0.2, 0.09, 1.0)
        return s

    def warn_a(self):
        s = self.score()
        s.track("fx:scr_creak", 0.9).note("C5", 0, 0.5)
        return s

    def warn_b(self):
        s = self.score()
        s.track("fx:scr_creak", 0.9).note("E5", 0, 0.4)
        s.track("syn:musicbox").note("G#6", 0.4, 0.2)
        return s

    def error(self):
        s = self.score()
        s.track("syn:organ").chord("D3+Eb3+A3", 0, 0.5)
        return s

    def idle(self):
        s = self.score()
        s.track("syn:scr-ghost", 0.8).note("A4", 0, 1.2, bend=-2, vib=0.4)
        return s

    def launch(self):
        s = self.score()
        s.track("fx:whoosh", 0.8).note("A5", 0, 0.8)
        s.track("syn:scr-ghost", 0.6).note("D4", 0, 1.0, bend=12)
        return s

    def land(self):
        s = self.score()
        s.track("fx:scr_creak", 0.7).note("C5", 0, 0.6)
        s.track("fx:scr_thunder", 0.8).note("C3", 0.55, 1.0)
        return s

    def home(self):
        s = self.score()
        s.track("gm:19").seq("D4 F4 A4 D5*3", 0.15)
        s.track("gm:19", 0.6).chord("D3+A3", 0, 0.9)
        return s

    def flip(self):
        s = self.score()
        s.track("fx:whoosh").note("C6", 0, 0.35)
        s.track("syn:musicbox").note("D7", 0.3, 0.15)
        return s

    def cut(self):
        s = self.score()
        s.track("fx:impact", 0.8).note("C2", 0, 0.5)
        return s

    def powerdown(self):
        s = self.score()
        s.track("syn:musicbox").note("A5", 0, 1.2, bend=-12, glide=1.2)
        return s


# ---------------------------------------------------------------- Medieval Bard

class MedievalBard(Theme):
    id = "medieval-bard"
    name = "Medieval Bard"
    category = "screen"
    tagline = "Lute, recorder, and a round for the whole tavern."
    blurb = ("Modal jigs on lute and recorder with a reedy shawm and a frame drum. The tavern cheers "
             "when you arm, and the drum slows when the battery fades.")
    skin = {"bg": "#2b1d12", "surface": "#3a2819", "ink": "#f5e6c8", "muted": "#c1a77f",
            "accent": "#d9482b", "font": "IM Fell English"}
    root, scale, step = "D5", DORIAN, 0.12
    lead, alt, bass, kit = "gm:74", "gm:24", "syn:lute", "kit:acoustic"
    master = [("reverb", {"size": 0.9, "wet": 0.22})]

    def drum(self, s, pattern, st, t=0.0, vol=0.6):
        tr = s.track("kit:acoustic", vol)
        for i, c in enumerate(pattern):
            if c == "x":
                tr.hit("floor", t + i * st, 0.9)
            elif c == "t":
                tr.hit("tamb", t + i * st, 0.6)

    def startup(self):
        s = self.score()
        st = 0.11
        s.track("gm:74").seq("D5 E5 F5 G5 A5*2 C6 A5 G5 A5*3", st)
        s.track("gm:24", 0.8).seq("D4+A4*3 C4+G4*3 D4+A4*6", st)
        self.drum(s, "x.tx.tx.tx.t", st)
        return s

    def arm(self):                             # tavern cheer
        s = self.score()
        s.track("fx:crowd", 0.5).note("A4", 0.25, 0.9)
        s.track("gm:68", 0.9).seq("D5 F#5 A5 D6*3", 0.1)
        self.drum(s, "x.x.x", 0.1)
        return s

    def disarm(self):
        s = self.score()
        s.track("gm:74").seq("A5 G5 F5 E5 D5*3", 0.12)
        s.track("gm:24", 0.7).chord("D3+A3", 0.36, 0.6)
        return s

    def yes(self):
        s = self.score()
        s.track("gm:24").arp(["A4", "D5"], 0.09)
        return s

    def no(self):
        s = self.score()
        s.track("gm:24").arp(["C5", "D4"], 0.1)
        return s

    def found(self):
        s = self.score()
        s.track("gm:74").seq("D5 F5 A5 D6*2", 0.07)
        return s

    def lost(self):
        s = self.score()
        s.track("gm:68", 0.8).seq("A4 G4 F4 D4*3", 0.12)
        return s

    def lowbat(self):
        s = self.score()
        self.drum(s, "x..x...x", 0.13, vol=0.8)
        s.track("gm:24", 0.7).seq("F4 R E4 R D4*2", 0.13)
        return s

    def critbat(self):
        s = self.score(fx=[])
        tr = s.track("gm:109", 0.9)
        for i in range(4):
            tr.note("A5", i * 0.22, 0.08, 1.0)
        self.drum(s, "x...x...x...x", 0.055, vol=0.9)
        return s

    def signal_warn(self):
        s = self.score()
        s.track("gm:74").seq("A5 R F5 R A5", 0.08)
        return s

    def signal_crit(self):
        s = self.score(fx=[])
        tr = s.track("gm:109")
        for i in range(4):
            tr.note("G5", i * 0.2, 0.07, 1.0)
        return s

    def warn_a(self):
        s = self.score()
        s.track("gm:74").seq("D5 A5", 0.09)
        return s

    def warn_b(self):
        s = self.score()
        s.track("gm:74").seq("D5 F5 A5 D6", 0.06)
        return s

    def error(self):
        s = self.score()
        s.track("gm:68").chord("D4+Eb4", 0, 0.4)
        return s

    def home(self):
        s = self.score()
        s.track("gm:74").seq("A4 D5 E5 F5 E5 D5*3", 0.1)
        s.track("gm:24", 0.7).chord("D3+A3+D4", 0, 0.9)
        self.drum(s, "x..x..x", 0.1)
        return s

    def launch(self):
        s = self.score()
        s.track("gm:74").arp([self.deg(i) for i in range(10)], 0.05)
        s.track("fx:crowd", 0.4).note("A4", 0.3, 0.7)
        return s

    def land(self):
        s = self.score()
        s.track("gm:74").arp([self.deg(i) for i in range(9, -1, -1)], 0.05)
        self.drum(s, "x", 0.1, 0.52, vol=0.9)
        return s

    def idle(self):
        s = self.score()
        s.track("gm:24", 0.8).seq("D5 A4 F4 R D5 A4 F4", 0.14)
        return s

    def count(self, n, base=0):
        s = self.score()
        s.track("gm:24").arp([self.deg(base + i) for i in range(n)], 0.12)
        return s

    def flip(self):
        s = self.score()
        s.track("gm:74").arp(["D5", "A5", "D6", "A6"], 0.05)
        self.drum(s, "t.t.t", 0.05)
        return s
