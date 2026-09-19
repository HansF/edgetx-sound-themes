"""Game homages, part 1: stealth, quest, speed, platformer, metal and RTS.

Original motifs in the spirit of each genre. No melodies, names or samples from any game.
"""
from .game_base import GameTheme
from ..theme import Theme, MAJOR, MINOR, PHRYGIAN, PENTA, LYDIAN, DORIAN


# ---------------------------------------------------------------- Stealth Op

class StealthOp(GameTheme):
    id = "stealth-op"
    name = "Stealth Op"
    category = "game"
    tagline = "Crawl. Hide. Do not be spotted."
    blurb = ("Radio-codec pings, a tense low pulse and an alert sting when the guards notice. "
             "Sneaking-mission sounds for every radio event.")
    skin = {"bg": "#10160f", "surface": "#1b2418", "ink": "#c9f0b8", "muted": "#7f9a72",
            "accent": "#ff5a1f", "font": "Share Tech Mono"}
    root, scale, step = "E5", MINOR, 0.08
    lead, alt, bass, kit = "fm:epiano", "syn:sine", "syn:sub", "kit:909"
    master = [("reverb", {"size": 0.7, "wet": 0.15})]

    def startup(self):
        s = self.score()
        s.track("syn:sine", 0.7).seq("A6 R A6 R E6*2", 0.07)          # codec ring
        s.track("syn:sub", 0.9).seq("E2*3 R E2 G2*2", 0.12)
        s.track("syn:brass", 0.5).seq("E3*4 F3*2 E3*4", 0.11)
        s.track("kit:909", 0.5).beat({"hat": "x.x.x.x.x.x.x.x."}, 0.1)
        return s

    def arm(self):                        # "all clear" ping
        s = self.score()
        s.track("syn:sine").seq("E6 B6 E7*3", 0.07)
        s.track("syn:sub", 0.8).note("E2", 0, 0.4)
        return s

    def disarm(self):
        s = self.score()
        s.track("syn:sine").seq("E7 B6 E6*3", 0.07)
        return s

    def lowbat(self):                     # caution
        s = self.score()
        s.track("syn:brass", 0.7).seq("E4 F4 R E4 F4", 0.12)
        return s

    def critbat(self):                    # alert sting: stab, then rapid pulses
        s = self.score(fx=[])
        s.track("syn:sine").seq("B6 B6 B6 B6 B6 B6", 0.09, gap=0.5)
        return s

    def yes(self):
        s = self.score()
        s.track("syn:sine").seq("E6 A6", 0.06)
        return s

    def no(self):
        s = self.score()
        s.track("syn:sine").seq("A6 E6*2", 0.06)
        return s

    def found(self):                      # codec incoming
        s = self.score()
        s.track("syn:sine", 0.7).seq("A6 R A6 R A6", 0.06)
        return s

    def lost(self):
        s = self.score()
        s.track("fx:static", 0.6).note("C4", 0, 0.5)
        return s

    def signal_warn(self):
        s = self.score()
        s.track("syn:sine").seq("B6 R B6 R", 0.08)
        s.track("syn:sub").note("E2", 0, 0.3)
        return s

    def signal_crit(self):
        s = self.score()
        s.track("syn:sine").seq("B6 " * 5, 0.09, gap=0.5)
        s.track("syn:brass", 0.6).chord("E4+F4", 0, 0.12)
        return s

    def cut(self):                        # crouch
        s = self.score()
        s.track("syn:sub").note("E2", 0, 0.18, bend=-5)
        return s


# ---------------------------------------------------------------- Meadow Hero

class MeadowHero(GameTheme):
    id = "meadow-hero"
    name = "Meadow Hero"
    category = "game"
    tagline = "Wide fields, small dungeons, one battery."
    blurb = ("Harp glissandi, ocarina-ish whistle and a treasure-chest fanfare, all original tunes for a "
             "green-tunic adventure across wide fields and small dungeons.")
    skin = {"bg": "#2c5b2f", "surface": "#f1e7b8", "ink": "#2a3a1a", "muted": "#5e6d3a",
            "accent": "#c9942b", "font": "Cinzel"}
    root, scale, step = "D5", MAJOR, 0.1
    lead, alt, bass, kit = "syn:whistle", "syn:pluck", "syn:sub", "kit:acoustic"
    master = [("reverb", {"size": 1.3, "wet": 0.3, "predelay": 0.02})]

    def _harp(self, s, notes, step=0.055, t=0.0, vol=0.9):
        return s.track("syn:pluck", vol).arp(notes, step, t, decay=0.4)

    def startup(self):                    # overworld dawn
        s = self.score()
        self._harp(s, ["D4", "A4", "D5", "F#5", "A5", "D6"])
        s.track("syn:whistle", 0.8).seq("A5*3 F#5 D6*4", 0.12, t=0.3)
        s.track("syn:pad", 0.5).chord("D4+A4+D5", 0, 1.5)
        return s

    def arm(self):                        # chest open
        s = self.score()
        s.track("syn:whistle").seq("G5 A5 B5 D6*4", 0.1)
        self._harp(s, ["G4", "D5", "G5", "B5", "D6"], 0.06, 0.1)
        return s

    def disarm(self):
        s = self.score()
        s.track("syn:whistle").seq("D6 B5 A5 G5*4", 0.1)
        return s

    def lowbat(self):                     # heart container running low
        s = self.score()
        s.track("fm:bell", 0.8).seq("D6 R D6 R D6", 0.11)
        s.track("syn:sub", 0.6).note("D3", 0, 0.5)
        return s

    def critbat(self):
        s = self.score(fx=[])
        s.track("fm:marimba").seq("D6 " * 6, 0.1, gap=0.6, decay=0.05)
        return s

    def found(self):                      # secret room (own tune, no borrowed notes)
        s = self.score()
        self._harp(s, ["D5", "E5", "G5", "A5", "B5", "D6"], 0.06)
        return s

    def yes(self):
        s = self.score()
        s.track("fm:bell").seq("D6 A6", 0.07)
        return s

    def home(self):
        s = self.score()
        s.track("syn:whistle").seq("D5 F#5 A5 D6*2 A5 D6*4", 0.1)
        self._harp(s, ["D4", "A4", "D5", "F#5", "A5", "D6", "F#6"], 0.08, 0.1)
        return s


# ---------------------------------------------------------------- Ring Dash

class RingDash(GameTheme):
    id = "ring-dash"
    name = "Ring Dash"
    category = "game"
    tagline = "Collect the rings. Beat the clock."
    blurb = ("Sparkly collect pings, spring boings, a spin-dash revving up and a bright zone-clear jingle. "
             "Everything is fast, bouncy and slightly too cheerful.")
    skin = {"bg": "#0b3d91", "surface": "#f5f7ff", "ink": "#0b1b45", "muted": "#3f5aa8",
            "accent": "#ffd400", "font": "Rubik"}
    root, scale, step = "G5", MAJOR, 0.065
    alert = "fm:marimba"
    lead, alt, bass, kit = "fm:brass", "fm:lead", "fm:bass", "kit:909"

    def startup(self):                    # zone title jingle
        s = self.score()
        s.track("fm:lead").seq("G5 B5 D6 G6*2 F#6 G6 B6*4", 0.07)
        s.track("fm:brass", 0.5).seq("G4*2 D5*2 G5*2 B5*4", 0.07)
        s.track("fm:bass", 0.9).seq("G2*2 G2 D3 G2*2 D3 G2*4", 0.07)
        s.track("kit:909", 0.6).beat({"kick": "x.x.x.x.x.x.x.x.", "hat": ".x.x.x.x.x.x.x.x"}, 0.065)
        return s

    def arm(self):                        # spin-dash charge and release
        s = self.score()
        for i in range(4):
            s.track("fm:lead").note("G4", i * 0.07, 0.06, bend=5 + i * 2)
        s.track("fx:whoosh", 0.8).note("C5", 0.3, 0.3)
        s.track("fm:brass").note("G6", 0.3, 0.3, decay=0.15)
        return s

    def disarm(self):
        s = self.score()
        s.track("fm:lead").note("G6", 0, 0.5, bend=-24)
        return s

    def lowbat(self):                     # drowning countdown
        s = self.score()
        s.track("fm:lead", 0.8).seq("E5 R E5 R C5 R C5", 0.08)
        s.track("fm:bass", 0.8).seq("C3*2 R C3*2", 0.1)
        return s

    def critbat(self):
        s = self.score()
        s.track("fm:lead").seq("C7 G6 C7 G6 C7 G6", 0.085, gap=0.5)
        s.track("kit:909", 0.7).beat({"kick": "x.x.x.x."}, 0.085)
        return s

    def yes(self):                        # ring pickup: two sparkly pings
        s = self.score()
        s.track("fm:bell", 0.9).seq("E7 B7", 0.05, gap=0.05)
        return s

    def no(self):                         # rings scattered
        s = self.score()
        for i in range(4):
            s.track("fm:bell", 0.7 - i * 0.12).note(f"{'BGEC'[i]}7", i * 0.045, 0.06)
        return s

    def warn_a(self):                     # spring
        s = self.score()
        s.track("fx:boing", 0.8).note("C5", 0, 0.3)
        return s

    def launch(self):
        s = self.score()
        s.track("fm:lead").note("G4", 0, 0.45, bend=24, steps=14)
        s.track("fx:whoosh", 0.6).note("C5", 0, 0.5)
        return s

    def home(self):                       # goal ring / act clear
        s = self.score()
        s.track("fm:lead").seq("G5 B5 D6 G6 D6 G6*3", 0.075)
        s.track("fm:brass", 0.5).seq("D5 G5 B5 D6 B5 D6*3", 0.075)
        s.track("kit:909", 0.6).beat({"kick": "x...x...", "hat": "..x...x."}, 0.075)
        return s


# ---------------------------------------------------------------- Warp Pipe

class WarpPipe(GameTheme):
    id = "warp-pipe"
    name = "Warp Pipe"
    category = "game"
    tagline = "Coin blocks, bouncy bass and a very long pipe."
    blurb = ("A sunny platformer in marimba and kalimba: coin blocks, stomps, power-ups and a goal-pole "
             "fanfare. Bouncy walking bass under everything.")
    skin = {"bg": "#5ab8ff", "surface": "#fff7e0", "ink": "#3a1f0f", "muted": "#8a5a2b",
            "accent": "#e63a2e", "font": "Baloo 2"}
    root, scale, step = "C5", MAJOR, 0.08
    lead, alt, bass, kit = "fm:marimba", "fm:kalimba", "fm:bass", "kit:acoustic"

    def startup(self):
        s = self.score()
        s.track("fm:marimba").seq("C5 E5 G5 C6 G5 E5 G5 C6*2 E6*3", 0.085)
        s.track("fm:bass", 0.9).seq("C3 R G2 R C3 R G2 R C3*3", 0.085)
        s.track("fm:kalimba", 0.5).seq("E6 R G6 R E6 R G6 R", 0.17, t=0.2)
        s.track("kit:acoustic", 0.5).beat({"kick": "x...x...x...", "hat": "..x...x...x."}, 0.085)
        return s

    def arm(self):                        # power-up: rising glide
        s = self.score()
        s.track("fm:lead").note("C5", 0, 0.5, bend=24, steps=12)
        s.track("fm:kalimba", 0.7).arp(["C6", "E6", "G6", "C7"], 0.06, 0.5)
        return s

    def disarm(self):                     # pipe down
        s = self.score()
        s.track("fm:bass").seq("G3 F3 E3 D3 C3*3", 0.065)
        return s

    def lowbat(self):
        s = self.score()
        s.track("fm:marimba").seq("G5 E5 R G5 E5", 0.1)
        return s

    def critbat(self):
        s = self.score()
        s.track("fm:marimba").seq("C6 G5 C6 G5 C6 G5", 0.085, gap=0.5)
        return s

    def yes(self):                        # coin
        s = self.score()
        s.track("fm:kalimba").seq("B6 E7*3", 0.05, decay=0.2)
        return s

    def no(self):                         # bonk
        s = self.score()
        s.track("fm:bass").note("E3", 0, 0.14, bend=-9)
        return s

    def land(self):                       # slide down the pole
        s = self.score()
        s.track("fm:lead").note("G6", 0, 0.7, bend=-31, steps=24)
        s.track("fm:bass").note("C2", 0.72, 0.2)
        return s

    def home(self):
        s = self.score()
        s.track("fm:marimba").seq("C6 G5 C6 E6 G6*2 E6 G6*4", 0.08)
        s.track("fm:bass", 0.9).seq("C3*3 G2*3 C3*5", 0.08)
        return s


# ---------------------------------------------------------------- Hellmetal

class Hellmetal(GameTheme):
    id = "hellmetal"
    name = "Hellmetal"
    category = "game"
    tagline = "Arm the quad. Angrily."
    blurb = ("Down-tuned palm-muted chugs, a Phrygian riff and a double-kick stampede. "
             "Every radio event sounds like a demon just noticed you.")
    skin = {"bg": "#120505", "surface": "#2a0d0a", "ink": "#ffb347", "muted": "#a35a3a",
            "accent": "#ff2a00", "font": "Rubik Glitch"}
    root, scale, step = "E4", PHRYGIAN, 0.075
    alert = "chip:p50"
    lead, alt, bass, kit = "syn:lead", "syn:saw", "syn:bass", "kit:909"
    master = [("drive", {"amount": 2.2}), ("reverb", {"size": 0.6, "wet": 0.12})]

    def _chug(self, s, notes, step=0.075, t=0.0, vol=1.0):
        return s.track("syn:bass", vol).seq(notes, step, t, gap=0.4)

    def startup(self):
        s = self.score()
        self._chug(s, "E2 E2 R E2 E2 R E2 G2*2 E2 E2 F2*3", 0.085)
        s.track("syn:lead", 0.6).seq("E4 R E4 F4 E4 R G4*2 F4*3", 0.085, t=0.4)
        s.track("kit:909", 0.9).beat({"kick": "x.x.x.x.x.x.x.x.x.x.", "snare": "....x.......x.......x"}, 0.085)
        s.track("kit:909", 0.7).hit("crash", 0)
        return s

    def arm(self):                        # chainsaw rev + power chord
        s = self.score()
        s.track("syn:saw", 0.7).note("E2", 0, 0.4, bend=12, steps=16, vib=0.6, vib_rate=25)
        s.track("syn:lead").chord("E3+B3+E4", 0.42, 0.3)
        s.track("kit:909").hit("crash", 0.42)
        return s

    def disarm(self):
        s = self.score()
        s.track("syn:lead").chord("E3+B3", 0, 0.12)
        s.track("syn:bass").note("E2", 0.14, 0.3, bend=-12)
        return s

    def lowbat(self):
        s = self.score()
        self._chug(s, "E2 E2 F2 E2 E2 F2*2", 0.09)
        return s

    def critbat(self):
        s = self.score()
        self._chug(s, "E2 " * 6, 0.09)
        return s

    def yes(self):
        s = self.score()
        s.track("syn:lead").chord("E3+B3", 0, 0.16)
        return s

    def no(self):
        s = self.score()
        s.track("syn:bass").seq("F2 E2*2", 0.07, gap=0.3)
        return s

    def signal_warn(self):
        s = self.score()
        s.track("syn:lead").seq("F4 E4 F4 E4", 0.08)
        return s

    def error(self):
        s = self.score()
        s.track("syn:bass").note("E1", 0, 0.5, vib=0.8, vib_rate=25)
        return s


# ---------------------------------------------------------------- War Room

class WarRoom(GameTheme):
    id = "war-room"
    name = "War Room"
    category = "game"
    tagline = "Base under attack. Reinforcements inbound."
    blurb = ("Real-time-strategy command grid: snare-drum marches, low synth brass, radar sweeps and a "
             "harvester chirp, with tense builder-bass underneath.")
    skin = {"bg": "#1b241a", "surface": "#2b3927", "ink": "#d6e6b2", "muted": "#8a9c6b",
            "accent": "#ffb100", "font": "Chakra Petch"}
    root, scale, step = "D4", DORIAN, 0.09
    alert = "syn:sq"
    lead, alt, bass, kit = "syn:brass", "syn:sq", "syn:bass", "kit:acoustic"
    master = [("reverb", {"size": 0.8, "wet": 0.18})]

    def startup(self):
        s = self.score()
        s.track("kit:acoustic", 0.9).beat({"snare": "x.xxx.xxx.xxxxxx", "kick": "x...x...x...x..."}, 0.075)
        s.track("syn:brass", 0.8).seq("D4*3 A3*3 D4 F4 A4*3", 0.12, t=0.1)
        s.track("syn:bass", 0.8).seq("D2*4 D2 F2 A2*4", 0.1)
        return s

    def arm(self):                        # unit ready, moving out
        s = self.score()
        s.track("syn:sq", 0.6).seq("D6 D6 A6", 0.06)
        s.track("syn:brass").seq("D4*2 A4*3", 0.1)
        s.track("kit:acoustic").beat({"snare": "xxx"}, 0.06)
        return s

    def disarm(self):
        s = self.score()
        s.track("syn:brass").seq("A4 F4 D4*3", 0.1)
        return s

    def lowbat(self):                     # base under attack
        s = self.score()
        s.track("syn:sq", 0.7).seq("A5 D5 A5 D5", 0.09)
        s.track("kit:acoustic").beat({"snare": "x.x."}, 0.09)
        return s

    def critbat(self):
        s = self.score()
        s.track("syn:sq").seq("A5 D6 " * 3, 0.09, gap=0.5)
        return s

    def yes(self):                        # construction complete
        s = self.score()
        s.track("syn:sq", 0.7).seq("D6 A6", 0.06)
        return s

    def found(self):                      # radar sweep
        s = self.score()
        s.track("syn:sine").note("D5", 0, 0.5, bend=12, steps=20)
        s.track("syn:sq", 0.5).seq("D6 R D6", 0.08, t=0.5)
        return s

    def lost(self):
        s = self.score()
        s.track("syn:sine").note("D6", 0, 0.5, bend=-24)
        return s

    def home(self):                       # mission accomplished
        s = self.score()
        s.track("syn:brass").seq("D4 F4 A4 D5*3 C5 D5*4", 0.1)
        s.track("kit:acoustic", 0.7).beat({"snare": "x.xx.xxx"}, 0.1)
        return s
