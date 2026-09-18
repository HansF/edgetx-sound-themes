"""Gen Z, Gen Alpha & weird: meme edits, drift phonk, hyperpop, kazoos, cats, ducks, NPCs.

Sound effects only (no voices). Everything is synthesised; every melody is original.
Custom instruments / effects are registered here with a "meme" prefix.
"""
import numpy as np

from .. import synth as S
from ..render import inst
from ..theme import Theme, MAJOR, MINOR, PHRYGIAN, LYDIAN

# ---------------------------------------------------------------- custom instruments

inst("syn:meme-ping", env=(0.001, 0.2, 0.0, 0.05), gm=9)(
    lambda f, n, note: S.sine(f) + 0.35 * S.sine(2 * f) * np.exp(-S.t_axis(n) / 0.05)
    + 0.1 * S.sine(3.01 * f) * np.exp(-S.t_axis(n) / 0.02))

inst("syn:meme-cowbell", env=(0.001, 0.16, 0.0, 0.03), gm=113)(
    lambda f, n, note: S.bp(S.pulse(f, 0.5) + S.pulse(f * 1.44, 0.5), float(np.mean(f)) * 1.2, 1.4) * 2.2)

inst("syn:meme-hyper", env=(0.002, 0.0, 1.0, 0.03), gm=81)(
    lambda f, n, note: S.bitcrush(S.lp(S.supersaw(f, 0.02, 5), 7000), 6, 2))


# ---------------------------------------------------------------- custom effects

def _hiss(dur, f, vel):
    """Angry cat hiss: breathy band of noise with a spitty onset."""
    n = S.n_samples(dur)
    t = S.t_axis(n)
    x = S.bp(S.noise(n), 4200, 1.3) + 0.6 * S.hp(S.noise(n), 6500)
    spit = S.bp(S.noise(n), 2000, 2) * np.exp(-t / 0.012) * 2
    return (x + spit) * S.adsr(n, 0.004, release=0.03) * vel


def _mrrp(dur, f, vel):
    """Cat trill: rolled 'r' (fast AM) on a rising little meow."""
    n = S.n_samples(dur)
    t = S.t_axis(n) / dur
    ff = f * (1 + 0.25 * t)
    x = S.formant_morph(S.saw(ff) * 0.7 + S.pulse(ff, 0.25) * 0.3, ["u", "e", "i"], 6)
    roll = 0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 32 * S.t_axis(n)))
    return x * roll * np.sin(np.pi * t) ** 0.6 * vel * 1.8


def _splash(dur, f, vel):
    n = S.n_samples(max(dur, 0.3))
    t = S.t_axis(n)
    body = S.lp(S.noise(n), 2500) * np.exp(-t / 0.09) + S.bp(S.noise(n), 5000, 1) * np.exp(-t / 0.05) * 0.6
    out = body
    for k in range(5):
        o = S.n_samples(0.04 + 0.05 * k)
        b = S.FX["bubble"](0.05, f * S.rng.uniform(0.8, 1.6), 0.4)
        out[o:o + len(b)] += b[: n - o]
    return out * vel


def _honk(dur, f, vel):
    """Goose-grade honk: nasal pulse through an 'a'/'o' formant, driven."""
    n = S.n_samples(dur)
    ff = np.full(n, float(f)) * (1 - 0.06 * S.t_axis(n) / dur)
    x = S.pulse(ff, 0.3) + 0.3 * S.saw(ff * 2)
    x = S.formant(x, "a", 5) * 1.2 + S.formant(x, "o", 5)
    return S.drive(x * 3, 2.5) * S.adsr(n, 0.004, release=0.025) * vel


def _sparkle(dur, f, vel):
    """'Anime wow' shimmer: a shower of rising high bell pings."""
    n = S.n_samples(dur)
    out = np.zeros(n + S.n_samples(0.15))
    k = max(4, int(dur / 0.03))
    for i in range(k):
        o = S.n_samples(i * dur / k)
        fr = f * 2 ** ((i / k) * 1.5 + S.rng.uniform(0, 0.15))
        m = S.n_samples(0.12)
        tt = S.t_axis(m)
        out[o:o + m] += (np.sin(2 * np.pi * fr * tt) + 0.4 * np.sin(2 * np.pi * fr * 2.76 * tt)) * np.exp(-tt / 0.035)
    return out * vel * 0.6


def _click(dur, f, vel):
    """Keyboard / mouse click."""
    n = S.n_samples(0.03)
    t = S.t_axis(n)
    return (S.bp(S.noise(n), f * 4, 2.5) * np.exp(-t / 0.003) * 1.5
            + np.sin(2 * np.pi * f * t) * np.exp(-t / 0.006)) * vel


def _buzz(dur, f, vel):
    """Controller / phone vibration motor rattle."""
    n = S.n_samples(dur)
    t = S.t_axis(n)
    motor = S.pulse(np.full(n, 150.0), 0.4) * (0.6 + 0.4 * np.sin(2 * np.pi * 23 * t))
    rattle = S.bp(S.noise(n), 900, 2) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 75 * t)))
    return S.lp(motor + rattle * 0.8, 1800) * S.adsr(n, 0.01, release=0.02) * vel * 1.5


def _screech(dur, f, vel):
    """Drift tyre screech: whistling rubber over tarmac hiss."""
    n = S.n_samples(dur)
    t = S.t_axis(n)
    ff = f * (1 + 0.05 * np.sin(2 * np.pi * 7 * t) + 0.03 * S.lp(S.noise(n), 20) * 10)
    squeal = S.sine(ff) + 0.4 * S.sine(ff * 2.02)
    hiss = S.bp(S.noise(n), 3000, 1.2)
    env = np.minimum(1, t / 0.05) * np.minimum(1, (dur - t) / 0.12)
    return (squeal * 0.8 + hiss * 0.7) * np.clip(env, 0, 1) * vel


def _tapestop(dur, f, vel):
    """A chord slowing to a halt."""
    n = S.n_samples(dur)
    t = S.t_axis(n) / dur
    k = (1 - t) ** 1.6
    x = sum(S.saw(f * r * (0.05 + 0.95 * k)) for r in (1, 1.26, 1.5, 2))
    return S.lp(x, 400 + 5000 * k) * (1 - t) ** 0.3 * vel * 0.6


for _name, _fn in (("meme_hiss", _hiss), ("meme_mrrp", _mrrp), ("meme_splash", _splash),
                   ("meme_honk", _honk), ("meme_sparkle", _sparkle), ("meme_click", _click),
                   ("meme_buzz", _buzz), ("meme_screech", _screech), ("meme_tapestop", _tapestop)):
    S.FX[_name] = _fn


# ================================================================ Brainrot

class Brainrot(Theme):
    id = "brainrot"
    name = "Brainrot"
    category = "meme"
    tagline = "Every event is a meme edit."
    blurb = ("Vine-style booms, stuttering air horns, bonks, record scratches and a tiny sad violin. "
             "Your quad now narrates itself like a group-chat edit.")
    skin = {"bg": "#ffe600", "surface": "#ffffff", "ink": "#111111", "muted": "#4a4a4a",
            "accent": "#ff2bd6", "font": "Bungee"}
    root, scale, step = "C6", MAJOR, 0.08
    lead, alt, bass, kit = "syn:meme-ping", "fm:bell", "syn:808", "kit:808"

    def _horn(self, s, t, dur, pitch="Bb4", vol=0.8):
        s.track("fx:airhorn", vol).note(pitch, t, dur)

    def startup(self):
        s = self.score()
        for t in (0, 0.12, 0.24):
            self._horn(s, t, 0.08)
        self._horn(s, 0.36, 0.5)
        s.track("syn:808", 0.9, [("drive", {"amount": 3})]).note("C2", 0.36, 0.9, bend=-5, glide=0.8)
        s.track("fx:meme_sparkle", 0.5).note("C6", 0.9, 0.35)
        return s

    def arm(self):                       # the boom
        s = self.score()
        s.track("fx:vineboom").note("A1", 0, 0.9)
        s.track("fx:meme_sparkle", 0.35).note("E6", 0.02, 0.3)
        return s

    def disarm(self):                    # record scratch, then the air leaves the room
        s = self.score()
        s.track("fx:scratch").note("A2", 0, 0.32)
        s.track("syn:808", 0.8, [("drive", {"amount": 2.5})]).note("G2", 0.36, 0.5, bend=-12, glide=0.5)
        return s

    def yes(self):                       # anime sparkle
        s = self.score()
        s.track("fx:meme_sparkle").note("C6", 0, 0.22)
        s.track("syn:meme-ping", 0.6).note("E7", 0, 0.12)
        return s

    def no(self):
        s = self.score()
        s.track("fx:bonk").note("D4", 0, 0.3)
        return s

    def found(self):                     # riser into a boom
        s = self.score()
        s.track("fx:riser", 0.7).note("G3", 0, 0.4)
        s.track("fx:vineboom").note("A1", 0.4, 0.8)
        return s

    def lost(self):                      # tiny sad violin
        s = self.score()
        s.track("fx:sadviolin").seq("E5 D5 C5 B4*3", 0.16, gap=0.02)
        return s

    def lowbat(self):                    # three sinking bass-boosted womps
        s = self.score()
        tr = s.track("syn:808", 1.0, [("drive", {"amount": 3.5})])
        for i, p in enumerate(("C3", "A2", "F2")):
            tr.note(p, i * 0.3, 0.24, bend=-4)
        return s

    def critbat(self):                   # air horn alarm
        s = self.score()
        for i in range(4):
            self._horn(s, i * 0.18, 0.1, "C5", 1.0)
        return s

    def signal_warn(self):
        s = self.score()
        s.track("syn:meme-ping").seq("B6 R E7", 0.1, gap=0.2)
        return s

    def signal_crit(self):               # notification spam
        s = self.score()
        s.track("syn:meme-ping").seq("E7 B6 R " * 4, 0.05, gap=0.2)
        return s

    def warn_a(self):
        s = self.score()
        s.track("fx:boing").note("G3", 0, 0.45)
        return s

    def warn_b(self):
        s = self.score()
        self._horn(s, 0, 0.12)
        s.track("fx:boing").note("C4", 0.16, 0.4)
        return s

    def error(self):                     # womp womp, bass boosted
        s = self.score()
        tr = s.track("syn:808", 1.0, [("drive", {"amount": 4})])
        tr.note("E2", 0, 0.3, bend=-2)
        tr.note("C2", 0.35, 0.45, bend=-3)
        return s

    def idle(self):                      # the one allowed fart joke, then a boing
        s = self.score()
        s.track("fx:fart", 0.9).note("F#2", 0, 0.45)
        s.track("fx:boing", 0.8).note("G3", 0.55, 0.4)
        return s

    def powerdown(self):
        s = self.score()
        s.track("fx:meme_tapestop").note("C4", 0, 0.8)
        return s

    def flip(self):
        s = self.score()
        s.track("fx:whoosh").note("G5", 0, 0.3)
        s.track("fx:boing", 0.8).note("C4", 0.25, 0.4)
        return s

    def launch(self):
        s = self.score()
        s.track("fx:riser", 0.8).note("G3", 0, 0.7)
        s.track("fx:vineboom").note("A1", 0.7, 0.9)
        return s

    def land(self):
        s = self.score()
        s.track("fx:boing").note("C4", 0, 0.5)
        s.track("fx:bonk").note("A3", 0.5, 0.3)
        return s

    def home(self):                      # air horn triad
        s = self.score()
        for t, p in ((0, "F4"), (0.2, "A4"), (0.4, "C5")):
            self._horn(s, t, 0.14, p)
        self._horn(s, 0.6, 0.4, "F5")
        return s

    def cut(self):
        s = self.score()
        s.track("fx:scratch").note("A2", 0, 0.18)
        return s

    def thr_on(self):
        s = self.score()
        s.track("syn:808", 1.0, [("drive", {"amount": 4})]).note("F2", 0, 0.35, bend=-7, glide=0.3)
        s.track("kit:808", 0.6).hit("clap", 0)
        return s


# ================================================================ Drift Phonk

class DriftPhonk(Theme):
    id = "drift-phonk"
    name = "Drift Phonk"
    category = "meme"
    tagline = "Cowbell melodies for sideways flying."
    blurb = ("Distorted 808s, phrygian cowbell riffs, tape saturation and tyre screech. "
             "Built for freestyle edits and power loops.")
    skin = {"bg": "#140b1f", "surface": "#221433", "ink": "#f2e9ff", "muted": "#a58fc0",
            "accent": "#c31dff", "font": "Rubik Mono One"}
    root, scale, step = "C#6", PHRYGIAN, 0.09
    lead, alt, bass, kit = "syn:meme-cowbell", "syn:meme-cowbell", "syn:808", "kit:phonk"
    master = [("drive", {"amount": 1.6}), ("wobble", {"depth": 0.0015, "rate": 0.5})]

    def _cb(self, s, vol=1.0):
        return s.track("syn:meme-cowbell", vol)

    def _808(self, s, vol=0.9):
        return s.track("syn:808", vol, [("drive", {"amount": 2.5})])

    def startup(self):
        s = self.score()
        st = 0.1
        self._cb(s).seq("C#6 C#6 E6 C#6 D6 C#6 B5 G#5 R C#6*2", st, gap=0.3)
        s.track("kit:phonk", 0.8).beat({"kick": "x..x..x...x.", "snare": "....x.......", "hat": "x.x.x.x.x.x."}, st)
        self._808(s).note("C#2", 0, 0.55)
        self._808(s).note("C#2", 0.6, 0.5, bend=-2)
        return s

    def arm(self):
        s = self.score()
        self._cb(s).seq("C#6 E6 G#6 C#7*3", 0.07, gap=0.25)
        s.track("kit:phonk", 0.9).hit("kick", 0.2)
        self._808(s).note("C#2", 0.2, 0.9, bend=12, glide=0.25)
        s.track("fx:meme_screech", 0.35).note("E7", 0.2, 0.5)
        return s

    def disarm(self):
        s = self.score()
        self._cb(s).seq("C#7 G#6 E6 D6 C#6*2", 0.08, gap=0.25)
        self._808(s).note("C#3", 0.1, 0.8, bend=-14, glide=0.7)
        return s

    def yes(self):
        s = self.score()
        self._cb(s).seq("G#6 C#7", 0.08, gap=0.35)
        return s

    def no(self):
        s = self.score()
        self._cb(s).seq("D6 C#6", 0.1, gap=0.3)
        s.track("kit:phonk", 0.8).hit("snare", 0.1)
        return s

    def found(self):
        s = self.score()
        self._cb(s).seq("C#6 E6 G#6 B6 C#7 E7", 0.05, gap=0.3)
        s.track("kit:phonk", 0.7).hit("clap", 0.25)
        return s

    def lost(self):                      # the riff slows to a halt
        s = self.score()
        cb = self._cb(s)
        cb.seq("C#7 B6 G#6", 0.1, gap=0.3)
        cb.note("E6", 0.3, 0.5, bend=-12, glide=0.5)
        self._808(s).note("C#2", 0.3, 0.6, bend=-7)
        return s

    def lowbat(self):
        s = self.score()
        self._cb(s).seq("E6 D6 R E6 D6 R D6 C#6*2", 0.085, gap=0.3)
        s.track("kit:phonk", 0.7).beat({"snare": "x..x..x.."}, 0.085)
        return s

    def critbat(self):
        s = self.score()
        for i in range(4):
            self._cb(s).seq("D7 D7", 0.05, t=i * 0.2, gap=0.35)
        return s

    def signal_warn(self):
        s = self.score()
        self._cb(s).seq("G#6 D6 G#6 D6", 0.1, gap=0.35)
        return s

    def signal_crit(self):
        s = self.score()
        self._cb(s).seq("E7 D7 R " * 4, 0.055, gap=0.35)
        return s

    def error(self):
        s = self.score()
        tr = self._808(s, 1.0)
        tr.note("D2", 0, 0.25, vib=1.0, vib_rate=25)
        tr.note("C#2", 0.3, 0.35, vib=1.0, vib_rate=25)
        return s

    def warn_a(self):
        s = self.score()
        s.track("fx:meme_screech", 0.8).note("E7", 0, 0.35)
        self._cb(s).note("C#7", 0.3, 0.08)
        return s

    def warn_b(self):
        s = self.score()
        s.track("fx:meme_screech", 0.8).note("A6", 0, 0.5)
        self._cb(s).seq("C#7 D7", 0.08, t=0.45, gap=0.3)
        return s

    def flip(self):                      # tyre screech through the loop
        s = self.score()
        s.track("fx:meme_screech").note("F7", 0, 0.6)
        s.track("kit:phonk", 0.8).hit("kick", 0.55)
        return s

    def launch(self):
        s = self.score()
        s.track("fx:meme_screech", 0.8).note("C#7", 0, 0.7)
        self._808(s).note("C#2", 0.1, 1.0, bend=12, glide=0.4)
        self._cb(s).seq("C#6 G#6 C#7", 0.08, t=0.6, gap=0.3)
        return s

    def land(self):
        s = self.score()
        self._808(s).note("G#2", 0, 0.7, bend=-12, glide=0.5)
        s.track("kit:phonk").hit("snare", 0.6)
        return s

    def home(self):
        s = self.score()
        self._cb(s).seq("C#6 D6 E6 C#6 G#6*2 E6 C#7*3", 0.09, gap=0.3)
        s.track("kit:phonk", 0.7).beat({"kick": "x...x...x", "hat": "..x...x.."}, 0.09)
        return s

    def cut(self):
        s = self.score()
        s.track("fx:meme_tapestop", 0.8).note("C#4", 0, 0.45)
        return s

    def thr_on(self):
        s = self.score()
        s.track("kit:phonk").hit("kick", 0)
        self._cb(s).note("C#7", 0.02, 0.08)
        return s

    def idle(self):
        s = self.score()
        self._cb(s).seq("C#6 R R G#5 R R C#6 R R G#5", 0.09, gap=0.3)
        return s


# ================================================================ Hyperpop

class Hyperpop(Theme):
    id = "hyperpop"
    name = "Hyperpop"
    category = "meme"
    tagline = "Too bright, too fast, perfect."
    blurb = ("Bit-crushed supersaw stabs, sparkly arps, gliding 808s and sudden glitch stutters, "
             "all pitched up past comfort.")
    skin = {"bg": "#ff9ad5", "surface": "#fff0fa", "ink": "#2a0038", "muted": "#7a4a8a",
            "accent": "#0077ff", "font": "Rubik Glitch"}
    root, scale, step = "E6", LYDIAN, 0.06
    lead, alt, bass, kit = "syn:meme-hyper", "syn:meme-ping", "syn:808", "kit:909"
    lead_fx = [("echo", {"delay": 0.09, "feedback": 0.3, "repeats": 2})]

    def _stab(self, s, t, chord, dur=0.1, vol=0.8, **kw):
        tr = s.track("syn:meme-hyper", vol)
        for p in chord.split("+"):
            tr.note(p, t, dur, **kw)
        return tr

    def _sparkle(self, s, pitches, step, t=0.0, vol=0.6):
        s.track("syn:meme-ping", vol, [("echo", {"delay": 0.07, "feedback": 0.35, "repeats": 3})]).arp(pitches, step, t)

    def startup(self):
        s = self.score()
        self._sparkle(s, ["E6", "B6", "G#6", "E7", "B6", "D#7", "F#7", "B7"], 0.045)
        self._stab(s, 0.36, "E5+G#5+B5+F#6", 0.12)
        self._stab(s, 0.54, "C#5+E5+G#5+D#6", 0.12)
        self._stab(s, 0.72, "A4+C#5+E5+B5", 0.35, bend=12, glide=0.3)
        s.track("syn:808", 0.9).note("E2", 0.36, 0.7, bend=12, glide=0.2)
        s.track("fx:glitch", 0.5).note("A3", 1.1, 0.2)
        return s

    def arm(self):
        s = self.score()
        s.track("syn:808", 1.0).note("E2", 0, 0.7, bend=12, glide=0.25)
        self._stab(s, 0.25, "E5+G#5+B5+D#6", 0.3)
        self._sparkle(s, ["B6", "E7", "G#7", "B7"], 0.04, 0.25)
        return s

    def disarm(self):
        s = self.score()
        s.track("fx:glitch", 0.7).note("A3", 0, 0.22)
        self._stab(s, 0.24, "E5+G#5+B5", 0.5, bend=-12, glide=0.45)
        s.track("syn:808", 0.9).note("E3", 0.24, 0.6, bend=-12, glide=0.5)
        return s

    def yes(self):
        s = self.score()
        s.track("syn:meme-hyper").seq("B6 E7", 0.06, gap=0.2)
        return s

    def no(self):
        s = self.score()
        s.track("fx:glitch", 0.7).note("A3", 0, 0.12)
        s.track("syn:meme-hyper").note("E5", 0.12, 0.12, bend=-5)
        return s

    def found(self):
        s = self.score()
        self._sparkle(s, ["E6", "G#6", "B6", "D#7", "E7", "G#7", "B7", "E8"], 0.03, vol=0.8)
        self._stab(s, 0.24, "E5+B5+E6", 0.2)
        return s

    def lost(self):
        s = self.score()
        self._stab(s, 0, "B5+D#6+F#6", 0.7, bend=-24, glide=0.7)
        s.track("syn:808", 0.8).note("B2", 0, 0.7, bend=-12)
        return s

    def lowbat(self):                    # stuttered, stepping down
        s = self.score()
        s.track("syn:meme-hyper").seq("B6 B6 B6 R G#6 G#6 G#6 R E6*3", 0.05, gap=0.3)
        return s

    def critbat(self):
        s = self.score()
        for i, ch in enumerate(("E6+B6", "D#6+A#6", "E6+B6", "D#6+A#6")):
            self._stab(s, i * 0.17, ch, 0.08, vol=1.0)
        return s

    def signal_warn(self):
        s = self.score()
        s.track("syn:meme-hyper").seq("F#7 R C#7 R", 0.08, gap=0.2)
        return s

    def signal_crit(self):
        s = self.score()
        s.track("syn:meme-hyper").seq("B7 F#7 R " * 5, 0.04, gap=0.3)
        return s

    def error(self):
        s = self.score()
        s.track("fx:glitch").note("C3", 0, 0.35)
        s.track("syn:808", 0.8).note("C2", 0.02, 0.35, vib=1.5, vib_rate=20)
        return s

    def warn_a(self):
        s = self.score()
        s.track("syn:meme-hyper").note("E6", 0, 0.2, bend=12, steps=6)
        return s

    def warn_b(self):
        s = self.score()
        s.track("syn:meme-hyper").note("B5", 0, 0.14, bend=7)
        s.track("syn:meme-hyper").note("E6", 0.18, 0.2, bend=12, steps=8)
        return s

    def flip(self):
        s = self.score()
        for i in range(3):
            s.track("syn:808", 0.9).note("E3", i * 0.1, 0.09, bend=12)
            s.track("syn:meme-hyper", 0.5).note("E6", i * 0.1, 0.08, bend=12)
        return s

    def launch(self):
        s = self.score()
        s.track("fx:riser", 0.7).note("E3", 0, 0.6)
        self._stab(s, 0.6, "E5+G#5+B5+E6", 0.4)
        s.track("kit:909").hit("crash", 0.6, 0.6)
        return s

    def land(self):
        s = self.score()
        self._stab(s, 0, "E6+B6", 0.6, bend=-24, glide=0.6)
        s.track("kit:909").hit("kick", 0.6)
        return s

    def home(self):
        s = self.score()
        s.track("syn:meme-hyper").seq("E6 F#6 G#6 B6 E7*3", 0.08, gap=0.15)
        s.track("syn:808", 0.8).note("E2", 0, 0.6, bend=12, glide=0.15)
        return s

    def thr_on(self):
        s = self.score()
        s.track("fx:glitch", 0.8).note("A3", 0, 0.1)
        s.track("syn:808", 0.9).note("E2", 0, 0.3, bend=7, glide=0.1)
        return s

    def cut(self):
        s = self.score()
        s.track("fx:glitch", 0.8).note("A3", 0, 0.08)
        s.track("kit:909").hit("kick", 0.08)
        return s


# ================================================================ Kazoo Orchestra

class KazooOrchestra(Theme):
    id = "kazoo-orchestra"
    name = "Kazoo Orchestra"
    category = "meme"
    tagline = "Forty kazoos. One conductor. No rehearsal."
    blurb = ("A full kazoo section in three-part harmony, a slide whistle soloist and a toy drum. "
             "Failure gets the traditional wah-wah-wahhh.")
    skin = {"bg": "#fff3c4", "surface": "#ffffff", "ink": "#3a2410", "muted": "#8a6a40",
            "accent": "#e8412c", "font": "Chewy"}
    root, scale, step = "C5", MAJOR, 0.1
    lead, alt, bass, kit = "fx:kazoo", "fx:kazoo", "fx:kazoo", "kit:acoustic"

    def _kz(self, s, vol=0.8):
        return s.track("fx:kazoo", vol)

    def _slide(self, s, pitch, t, dur, bend, vol=0.8):
        s.track("syn:whistle", vol).note(pitch, t, dur, bend=bend)

    def startup(self):
        s = self.score()
        st = 0.1
        self._kz(s).seq("C5 E5 G5 C6*2 G5 C6*4", st, gap=0.08)
        self._kz(s, 0.6).seq("E4 G4 E5 E5*2 E5 E5*4", st, gap=0.08)
        self._kz(s, 0.6).seq("C4*3 G3*2 C4*2 C4*4", st, gap=0.08)
        s.track("kit:acoustic", 0.6).beat({"kick": "x...x.x.x", "snare": "..x...x.."}, st)
        return s

    def arm(self):                       # slide up, ta-da!
        s = self.score()
        self._slide(s, "C5", 0, 0.28, 12)
        for p in ("C5", "E5", "G5", "C6"):
            self._kz(s, 0.55).note(p, 0.32, 0.45)
        s.track("kit:acoustic", 0.6).hit("crash", 0.32)
        return s

    def disarm(self):                    # slide down, bwomp
        s = self.score()
        self._slide(s, "C6", 0, 0.45, -14)
        self._kz(s).note("C3", 0.48, 0.3)
        self._kz(s, 0.6).note("G2", 0.48, 0.3)
        return s

    def yes(self):
        s = self.score()
        self._kz(s).seq("G5 C6", 0.1, gap=0.1)
        return s

    def no(self):
        s = self.score()
        self._kz(s).seq("E4 C4", 0.12, gap=0.1)
        return s

    def found(self):
        s = self.score()
        self._kz(s).seq("C5 E5 G5 C6*2", 0.08, gap=0.08)
        self._slide(s, "C6", 0.1, 0.3, 7, 0.5)
        return s

    def lost(self):                      # wah wah wah wahhh
        s = self.score()
        tr = self._kz(s)
        tr.seq("G4 F#4 F4", 0.17, gap=0.12)
        tr.note("E4", 0.51, 0.55, vib=0.5, vib_rate=5)
        return s

    def lowbat(self):
        s = self.score()
        self._kz(s).seq("E5 D5 R D5 C5 R C5 B4*2", 0.1, gap=0.15)
        return s

    def critbat(self):
        s = self.score()
        for i in range(4):
            for p in ("A5", "C#6", "E6"):
                self._kz(s, 0.5).note(p, i * 0.19, 0.11)
        return s

    def signal_warn(self):
        s = self.score()
        self._kz(s).seq("G5 E5 G5 E5", 0.1, gap=0.2)
        return s

    def signal_crit(self):
        s = self.score()
        self._kz(s).seq("B5 G5 R " * 4, 0.055, gap=0.2)
        return s

    def error(self):                     # the raspberry
        s = self.score()
        s.track("fx:kazoo").note("C3", 0, 0.45)
        s.track("fx:kazoo", 0.6).note("C#3", 0, 0.45)
        return s

    def warn_a(self):
        s = self.score()
        self._slide(s, "C5", 0, 0.2, 12, 1.0)
        return s

    def warn_b(self):
        s = self.score()
        self._slide(s, "G4", 0, 0.14, 5, 1.0)
        self._slide(s, "C5", 0.18, 0.25, 19, 1.0)
        return s

    def idle(self):
        s = self.score()
        self._kz(s).seq("C5 R E5 R C5 R G4", 0.12, gap=0.15)
        return s

    def powerdown(self):
        s = self.score()
        self._slide(s, "G5", 0, 0.7, -19)
        return s

    def flip(self):
        s = self.score()
        self._slide(s, "C5", 0, 0.15, 12, 1.0)
        self._slide(s, "C6", 0.15, 0.15, -12, 1.0)
        self._slide(s, "C5", 0.3, 0.2, 14, 1.0)
        return s

    def launch(self):
        s = self.score()
        self._slide(s, "C4", 0, 0.7, 24)
        self._kz(s, 0.7).seq("C6 E6 G6*3", 0.1, t=0.7, gap=0.1)
        return s

    def land(self):
        s = self.score()
        self._slide(s, "C6", 0, 0.55, -17)
        s.track("kit:acoustic").hit("kick", 0.56)
        s.track("kit:acoustic", 0.5).hit("crash", 0.56)
        return s

    def home(self):                      # a little march
        s = self.score()
        self._kz(s).seq("G4 C5 C5 D5 E5*2 C5 G5*3", 0.1, gap=0.1)
        self._kz(s, 0.5).seq("E4 E4 E4 G4 G4*2 E4 B4*3", 0.1, gap=0.1)
        s.track("kit:acoustic", 0.6).beat({"snare": "x.xx.x.xx"}, 0.1)
        return s

    def cut(self):
        s = self.score()
        s.track("kit:acoustic").hit("kick", 0)
        self._kz(s).note("C3", 0, 0.18)
        return s

    def thr_on(self):
        s = self.score()
        self._slide(s, "G5", 0, 0.12, 7, 1.0)
        return s


# ================================================================ Cat Mode

class CatMode(Theme):
    id = "cat-mode"
    name = "Cat Mode"
    category = "meme"
    tagline = "Your radio has been adopted by a cat."
    blurb = ("Chirps, trills, meows, a purr when you leave it alone and a proper hiss when something "
             "goes wrong. The cat also walks across a toy piano.")
    skin = {"bg": "#fde2e4", "surface": "#fffafa", "ink": "#3b2a2f", "muted": "#8c6f76",
            "accent": "#d9603b", "font": "Fredoka"}
    root, scale, step = "C6", MAJOR, 0.09
    lead, alt, bass, kit = "fm:celesta", "fm:celesta", "fm:marimba", "kit:acoustic"

    def _meow(self, s, pitch, t, dur, vol=1.0):
        s.track("fx:meow", vol).note(pitch, t, dur)

    def _toy(self, s, vol=0.7):
        return s.track("fm:celesta", vol)

    def startup(self):
        s = self.score()
        self._toy(s).seq("C6 E6 G6 E6 C7*2", 0.1, gap=0.1)
        self._meow(s, "D5", 0.62, 0.55)
        return s

    def arm(self):                       # excited trill + meow
        s = self.score()
        s.track("fx:meme_mrrp").note("E5", 0, 0.2)
        self._meow(s, "G5", 0.22, 0.4)
        self._toy(s, 0.5).arp(["C6", "E6", "G6", "C7"], 0.06, 0.22)
        return s

    def disarm(self):                    # settles down to purr
        s = self.score()
        self._toy(s, 0.6).seq("C7 G6 E6 C6", 0.08, gap=0.1)
        s.track("fx:purr", 1.2).note("A1", 0.3, 0.7)
        return s

    def yes(self):
        s = self.score()
        s.track("fx:meme_mrrp").note("F5", 0, 0.2)
        return s

    def no(self):
        s = self.score()
        s.track("fx:meme_hiss").note("C5", 0, 0.28)
        return s

    def found(self):
        s = self.score()
        self._meow(s, "A5", 0, 0.35)
        self._toy(s, 0.5).arp(["E6", "G6", "C7"], 0.07, 0.2)
        return s

    def lost(self):                      # long sad low meow
        s = self.score()
        self._meow(s, "G4", 0, 0.85)
        return s

    def lowbat(self):                    # hungry
        s = self.score()
        for i, p in enumerate(("C5", "A4", "F4")):
            self._meow(s, p, i * 0.33, 0.26)
        return s

    def critbat(self):                   # four hiss bursts
        s = self.score()
        for i in range(4):
            s.track("fx:meme_hiss").note("C5", i * 0.2, 0.12)
        return s

    def signal_warn(self):
        s = self.score()
        self._meow(s, "D5", 0, 0.25)
        self._meow(s, "D5", 0.35, 0.25)
        return s

    def signal_crit(self):               # yowling
        s = self.score()
        for i in range(4):
            self._meow(s, "B5" if i % 2 == 0 else "G5", i * 0.2, 0.13)
        return s

    def error(self):                     # paws on the keyboard
        s = self.score()
        toy = self._toy(s, 0.6)
        for t, ch in ((0, "C5+C#5+D5"), (0.13, "F#5+G5+A5"), (0.21, "D6+Eb6"), (0.33, "A4+B4+C5+D5")):
            for p in ch.split("+"):
                toy.note(p, t, 0.08)
        self._meow(s, "E5", 0.5, 0.3, 0.8)
        return s

    def warn_a(self):
        s = self.score()
        s.track("fx:meme_mrrp").note("C5", 0, 0.22)
        return s

    def warn_b(self):
        s = self.score()
        s.track("fx:meme_mrrp").note("C5", 0, 0.18)
        self._meow(s, "A5", 0.22, 0.3)
        return s

    def idle(self):
        s = self.score()
        s.track("fx:purr", 1.2).note("A1", 0, 1.0)
        s.track("fx:meme_mrrp", 0.6).note("D5", 1.05, 0.2)
        return s

    def powerdown(self):
        s = self.score()
        self._meow(s, "E5", 0, 0.3)
        s.track("fx:purr", 1.2).note("A1", 0.3, 0.6)
        return s

    def flip(self):                      # zoomies
        s = self.score()
        s.track("kit:acoustic", 0.7).beat({"rim": "xxxxxxxx"}, 0.04)
        s.track("fx:meme_mrrp").note("A5", 0.33, 0.2)
        return s

    def launch(self):
        s = self.score()
        s.track("fx:whoosh", 0.8).note("G5", 0, 0.4)
        self._meow(s, "C6", 0.3, 0.45)
        return s

    def land(self):                      # four paws, thump
        s = self.score()
        s.track("kit:acoustic").hit("kick", 0)
        s.track("fx:meme_mrrp").note("E5", 0.15, 0.2)
        return s

    def home(self):
        s = self.score()
        self._toy(s).seq("G5 C6 E6 D6 C6 G6*3", 0.1, gap=0.1)
        s.track("fx:meme_mrrp", 0.7).note("G5", 0.7, 0.2)
        return s

    def cut(self):
        s = self.score()
        s.track("fx:meme_hiss").note("C5", 0, 0.15)
        s.track("kit:acoustic", 0.7).hit("kick", 0)
        return s

    def thr_on(self):
        s = self.score()
        s.track("fx:meme_mrrp").note("A5", 0, 0.14)
        return s


# ================================================================ Rubber Duck Squad

class RubberDuckSquad(Theme):
    id = "rubber-duck-squad"
    name = "Rubber Duck Squad"
    category = "meme"
    tagline = "Squeak squeak, you're armed."
    blurb = ("A choir of rubber ducks in close harmony, bath-time bubbles and splashes, "
             "and a goose-grade honk for anything critical.")
    skin = {"bg": "#ffd23f", "surface": "#fff8dc", "ink": "#1b3a5c", "muted": "#4f6d8a",
            "accent": "#ff6a00", "font": "Bagel Fat One"}
    root, scale, step = "C6", MAJOR, 0.1
    lead, alt, bass, kit = "fx:squeak", "fx:squeak", "fx:bubble", "kit:acoustic"

    def _sq(self, s, vol=0.8):
        return s.track("fx:squeak", vol)

    def _choir(self, s, t, chord, dur, vol=0.5):
        tr = self._sq(s, vol)
        for p in chord.split("+"):
            tr.note(p, t, dur)

    def startup(self):
        s = self.score()
        self._sq(s).seq("C6 E6 G6 C7*3", 0.11, gap=0.1)
        self._sq(s, 0.5).seq("E5 G5 E6 E6*3", 0.11, gap=0.1)
        for i in range(4):
            s.track("fx:bubble", 0.4).note("G4", 0.6 + i * 0.07, 0.06)
        return s

    def arm(self):
        s = self.score()
        self._choir(s, 0, "G5+C6+E6", 0.14)
        self._choir(s, 0.18, "C6+E6+G6", 0.4)
        s.track("fx:meme_splash", 0.6).note("G4", 0.18, 0.35)
        return s

    def disarm(self):                    # drain gurgle
        s = self.score()
        self._sq(s).note("G5", 0, 0.3)
        for i, p in enumerate(("G4", "E4", "C4", "A3", "F3")):
            s.track("fx:bubble", 0.8).note(p, 0.3 + i * 0.09, 0.07)
        return s

    def yes(self):
        s = self.score()
        self._sq(s).seq("E6 G6", 0.09, gap=0.15)
        return s

    def no(self):                        # sad duck
        s = self.score()
        self._sq(s).note("E5", 0, 0.3)
        return s

    def found(self):
        s = self.score()
        for i, p in enumerate(("C4", "E4", "G4", "C5", "E5")):
            s.track("fx:bubble", 0.8).note(p, i * 0.05, 0.05)
        self._sq(s).note("C7", 0.28, 0.2)
        return s

    def lost(self):                      # sinking
        s = self.score()
        self._sq(s).note("A4", 0, 0.45)
        for i, p in enumerate(("E4", "C4", "A3")):
            s.track("fx:bubble", 0.7).note(p, 0.5 + i * 0.12, 0.08)
        return s

    def lowbat(self):
        s = self.score()
        self._sq(s).seq("G6 R E6 R C6*2", 0.12, gap=0.15)
        return s

    def critbat(self):                   # honk honk honk honk
        s = self.score()
        for i in range(4):
            s.track("fx:meme_honk").note("A4", i * 0.2, 0.12)
        return s

    def signal_warn(self):
        s = self.score()
        self._sq(s).seq("G6 E6 G6 E6", 0.1, gap=0.3)
        return s

    def signal_crit(self):
        s = self.score()
        self._sq(s).seq("C7 A6 R " * 4, 0.055, gap=0.3)
        return s

    def error(self):
        s = self.score()
        s.track("fx:meme_honk").note("D4", 0, 0.2)
        s.track("fx:meme_honk").note("C4", 0.3, 0.3)
        return s

    def warn_a(self):
        s = self.score()
        self._sq(s).seq("C6 G6", 0.08, gap=0.15)
        return s

    def warn_b(self):
        s = self.score()
        self._sq(s).seq("C6 E6 G6 C7", 0.07, gap=0.15)
        return s

    def idle(self):
        s = self.score()
        for i in range(3):
            s.track("fx:bubble", 0.6).note("E4", i * 0.3, 0.07)
        self._sq(s, 0.6).note("G5", 0.95, 0.15)
        return s

    def powerdown(self):
        s = self.score()
        self._sq(s).seq("G6 E6 C6 G5", 0.1, gap=0.15)
        return s

    def flip(self):
        s = self.score()
        self._sq(s).seq("C6 G6 C7", 0.07, gap=0.15)
        s.track("fx:meme_splash", 0.7).note("G4", 0.22, 0.35)
        return s

    def launch(self):
        s = self.score()
        self._sq(s).seq("C5 E5 G5 C6 E6 G6 C7", 0.06, gap=0.15)
        for i in range(4):
            s.track("fx:bubble", 0.5).note("C5", 0.45 + i * 0.06, 0.05)
        return s

    def land(self):
        s = self.score()
        s.track("fx:meme_splash").note("G4", 0, 0.45)
        self._sq(s, 0.6).note("E6", 0.4, 0.15)
        return s

    def home(self):
        s = self.score()
        self._sq(s).seq("G5 C6 E6 G6 E6 C7*3", 0.1, gap=0.1)
        self._sq(s, 0.45).seq("E5 G5 C6 E6 C6 E6*3", 0.1, gap=0.1)
        return s

    def cut(self):
        s = self.score()
        s.track("fx:meme_splash", 0.8).note("E4", 0, 0.25)
        return s

    def thr_on(self):
        s = self.score()
        self._sq(s).note("G6", 0, 0.1)
        return s


# ================================================================ NPC Mode

class NPCMode(Theme):
    id = "npc-mode"
    name = "NPC Mode"
    category = "meme"
    tagline = "Notifications on. Always."
    blurb = ("Clean app-UI sound design: notification pings, stream gift chimes, level-up jingles, "
             "keyboard clicks and a phone buzzing on the desk.")
    skin = {"bg": "#eef1f5", "surface": "#ffffff", "ink": "#141a22", "muted": "#5d6775",
            "accent": "#00a676", "font": "Sora"}
    root, scale, step = "E6", MAJOR, 0.08
    lead, alt, bass, kit = "syn:meme-ping", "fm:marimba", "fm:marimba", "kit:909"
    master = [("reverb", {"size": 0.6, "wet": 0.18})]

    def _ping(self, s, vol=0.9):
        return s.track("syn:meme-ping", vol)

    def _click(self, s, t, vol=0.7):
        s.track("fx:meme_click", vol).note("C6", t, 0.03)

    def startup(self):                   # device boot
        s = self.score()
        s.track("fx:whoosh", 0.4).note("G5", 0, 0.35)
        s.track("fm:marimba", 0.8).arp(["E5", "B5", "E6", "G#6"], 0.09, 0.2)
        s.track("fm:bell", 0.45).note("B6", 0.56, 0.6)
        s.track("fm:bell", 0.35).note("E7", 0.56, 0.6)
        return s

    def arm(self):                       # level up
        s = self.score()
        s.track("fx:meme_buzz", 0.5).note("C3", 0, 0.12)
        s.track("fm:marimba").arp(["C6", "E6", "G6", "C7"], 0.06, 0.1)
        s.track("fx:meme_sparkle", 0.5).note("C7", 0.34, 0.3)
        s.track("fm:bell", 0.5).note("G7", 0.34, 0.4)
        return s

    def disarm(self):                    # app closed
        s = self.score()
        self._click(s, 0)
        s.track("fm:marimba").arp(["G5", "C5"], 0.1, 0.05)
        s.track("fx:whoosh", 0.5).note("C5", 0.15, 0.3)
        return s

    def yes(self):                       # notification
        s = self.score()
        self._ping(s).arp(["E6", "B6"], 0.07)
        return s

    def no(self):
        s = self.score()
        self._click(s, 0)
        s.track("fm:marimba").seq("E4 E4", 0.08, t=0.01, gap=0.2)
        return s

    def found(self):                     # reconnected
        s = self.score()
        self._ping(s).arp(["B5", "E6", "G#6", "B6"], 0.06)
        return s

    def lost(self):                      # disconnected
        s = self.score()
        self._ping(s).arp(["B6", "G#6", "E6"], 0.1)
        s.track("fx:meme_buzz", 0.6).note("C3", 0.32, 0.25)
        return s

    def lowbat(self):                    # phone battery chirp
        s = self.score()
        self._ping(s).seq("C7 R C7 R G6*3", 0.08, gap=0.2)
        return s

    def critbat(self):                   # buzz + beep, four times
        s = self.score()
        for i in range(4):
            s.track("fx:meme_buzz", 0.7).note("C3", i * 0.2, 0.07)
            self._ping(s).note("A6", i * 0.2, 0.08)
        return s

    def signal_warn(self):
        s = self.score()
        self._ping(s).seq("G6 R D6", 0.09, gap=0.2)
        return s

    def signal_crit(self):
        s = self.score()
        self._ping(s).seq("D7 A6 R " * 4, 0.05, gap=0.25)
        return s

    def error(self):
        s = self.score()
        s.track("fx:meme_buzz").note("C3", 0, 0.14)
        s.track("fx:meme_buzz").note("C3", 0.2, 0.14)
        s.track("fm:marimba", 0.8).note("E4", 0.02, 0.2)
        return s

    def warn_a(self):                    # "typing..."
        s = self.score()
        for i in range(3):
            self._click(s, i * 0.07)
        self._ping(s).note("B6", 0.24, 0.1)
        return s

    def warn_b(self):
        s = self.score()
        self._ping(s).seq("E6 B6", 0.07)
        s.track("fx:meme_buzz", 0.6).note("C3", 0.16, 0.2)
        return s

    def idle(self):                      # "are you still there?"
        s = self.score()
        for i in range(5):
            self._click(s, i * 0.06 + (0.05 if i % 2 else 0), 0.5)
        self._ping(s).arp(["G#6", "E6"], 0.12, 0.45)
        self._ping(s, 0.6).arp(["G#6", "E6"], 0.12, 0.9)
        return s

    def powerdown(self):
        s = self.score()
        s.track("fm:marimba").arp(["B6", "G#6", "E6", "B5"], 0.07)
        s.track("fx:whoosh", 0.4).note("C5", 0.2, 0.3)
        return s

    def flip(self):
        s = self.score()
        s.track("fx:whoosh").note("G5", 0, 0.2)
        s.track("fx:whoosh").note("A5", 0.2, 0.2)
        self._click(s, 0.4)
        return s

    def launch(self):                    # stream gift
        s = self.score()
        s.track("fx:whoosh", 0.5).note("G5", 0, 0.3)
        s.track("fm:bell", 0.7).arp(["E6", "G#6", "B6", "E7", "G#7"], 0.06, 0.2)
        s.track("fx:meme_sparkle", 0.5).note("E7", 0.5, 0.3)
        return s

    def land(self):
        s = self.score()
        s.track("kit:909", 0.7).hit("kick", 0)
        self._ping(s).note("E6", 0.1, 0.1)
        return s

    def home(self):                      # achievement unlocked
        s = self.score()
        s.track("fm:bell", 0.7).arp(["E6", "B6", "E7"], 0.08)
        s.track("fm:marimba", 0.6).arp(["E5", "G#5", "B5", "E6"], 0.06, 0.24)
        return s

    def cut(self):
        s = self.score()
        self._click(s, 0)
        s.track("kit:909", 0.6).hit("kick", 0.02)
        return s

    def thr_on(self):
        s = self.score()
        self._click(s, 0)
        s.track("fx:whoosh", 0.6).note("A5", 0.02, 0.15)
        return s
