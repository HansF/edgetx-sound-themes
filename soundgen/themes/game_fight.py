"""Game homages, part 3: fighters, rally, jungle platformer and gothic castle.

Original motifs in the spirit of each genre. No melodies, names or samples from any game.
"""
from .game_base import GameTheme
from ..theme import MAJOR, MINOR, PHRYGIAN, PENTA, MINOR_PENTA, HARM_MINOR, MIXOLYDIAN


# ---------------------------------------------------------------- Dojo Duel

class DojoDuel(GameTheme):
    id = "dojo-duel"
    name = "Dojo Duel"
    category = "game"
    tagline = "Round one. Fight! K.O.!"
    blurb = ("A 16-bit street fighter: punchy kicks and snares, brassy hits, a round-start sting and a "
             "victory fanfare. Every alert lands like a well-timed uppercut.")
    skin = {"bg": "#1c1030", "surface": "#f4e9d1", "ink": "#2a1240", "muted": "#7a5b8c",
            "accent": "#e5352b", "font": "Bungee"}
    root, scale, step = "G4", MINOR_PENTA, 0.08
    lead, alt, bass, kit = "fm:brass", "fm:lead", "fm:bass", "kit:909"
    alert = "fm:marimba"

    def startup(self):                    # character-select riff
        s = self.score()
        s.track("fm:brass").seq("G4 G4 Bb4 C5 D5*2 C5 Bb4 G4*3", 0.085)
        s.track("fm:bass", 0.9).seq("G2 R G2 R G2 D3 G2 R F2*3", 0.085)
        s.track("kit:909", 0.9).beat({"kick": "x.x...x.x.x...", "snare": "....x.......x."}, 0.085)
        s.track("kit:909", 0.6).hit("crash", 0.0)
        return s

    def arm(self):                        # round start: hit + "fight!" stab
        s = self.score()
        s.track("kit:909").hit("kick", 0)
        s.track("fm:brass").chord("G4+D5+G5", 0.12, 0.35)
        s.track("kit:909", 0.8).hit("snare", 0.12)
        return s

    def disarm(self):                     # K.O.
        s = self.score()
        s.track("kit:909").hit("snare", 0)
        s.track("fm:brass").seq("D5 Bb4 G4 D4*3", 0.08, t=0.1)
        s.track("fm:bass").note("G2", 0.1, 0.5, bend=-12)
        return s

    def lowbat(self):                     # health bar flashing
        s = self.score()
        s.track("fm:lead").seq("D6 R D6 R Bb5 R Bb5", 0.08)
        return s

    def critbat(self):
        s = self.score(fx=[])
        s.track("fm:marimba").seq("D6 Bb5 " * 3, 0.1, gap=0.6, decay=0.05)
        return s

    def yes(self):                        # punch
        s = self.score()
        s.track("kit:909").hit("snare", 0)
        s.track("fm:lead").seq("G5 D6", 0.05, t=0.03)
        return s

    def no(self):                         # blocked
        s = self.score()
        s.track("kit:909").hit("floor", 0, 0.9)
        s.track("fm:bass").note("G2", 0, 0.2, bend=-12)
        return s

    def found(self):                      # combo counter
        s = self.score()
        s.track("fm:lead").seq("G5 Bb5 D6 G6", 0.05)
        s.track("kit:909").beat({"kick": "x.x.x.x."}, 0.05)
        return s

    def flip(self):                       # spinning kick
        s = self.score()
        for i in range(3):
            s.track("fm:lead").note("G5", i * 0.07, 0.06, bend=7)
        s.track("kit:909").hit("snare", 0.22)
        return s

    def home(self):                       # victory pose
        s = self.score()
        s.track("fm:brass").seq("G4 Bb4 D5 G5*3 F5 G5*4", 0.085)
        s.track("fm:bass").seq("G2*3 G2*3 G2*5", 0.085)
        s.track("kit:909", 0.7).beat({"kick": "x...x...", "crash": "x......."}, 0.085)
        return s


# ---------------------------------------------------------------- Polygon Brawler

class PolygonBrawler(GameTheme):
    id = "polygon-brawler"
    name = "Polygon Brawler"
    category = "game"
    tagline = "Three-dimensional violence, in five colours of flat shading."
    blurb = ("An early-3D tournament arena: taiko drums, industrial pings, string-machine drama and a "
             "big juggle-combo hit for every important event.")
    skin = {"bg": "#101820", "surface": "#1f2d3a", "ink": "#f0f4f8", "muted": "#8ea4b8",
            "accent": "#ffb300", "font": "Russo One"}
    root, scale, step = "D4", HARM_MINOR, 0.09
    lead, alt, bass, kit = "syn:brass", "syn:lead", "syn:bass", "kit:acoustic"
    alert = "syn:sq"
    master = [("reverb", {"size": 1.0, "wet": 0.2})]

    def startup(self):                    # arena intro: taiko + strings
        s = self.score()
        s.track("kit:acoustic", 0.95).beat({"floor": "x.x.xx..x.x.xxxx", "kick": "x.......x......."}, 0.075)
        s.track("syn:pad", 0.6).chord("D3+A3+F4", 0.3, 1.5)
        s.track("syn:brass").seq("D4*3 A3 D4 F4 A4*3", 0.12, t=0.6)
        return s

    def arm(self):
        s = self.score()
        s.track("kit:acoustic").beat({"floor": "xx", "kick": "x."}, 0.08)
        s.track("syn:brass").chord("D4+A4+D5", 0.16, 0.4)
        return s

    def disarm(self):
        s = self.score()
        s.track("syn:brass").seq("A4 F4 D4*3", 0.09)
        s.track("kit:acoustic").hit("floor", 0.25)
        return s

    def lowbat(self):
        s = self.score()
        s.track("syn:lead", 0.7).seq("A5 R A5 R F5", 0.1)
        return s

    def critbat(self):
        s = self.score(fx=[])
        s.track("syn:sq").seq("A6 E6 " * 3, 0.1, gap=0.6, decay=0.05)
        return s

    def yes(self):
        s = self.score()
        s.track("kit:acoustic").hit("floor", 0)
        s.track("syn:lead").seq("D5 A5", 0.05, t=0.03)
        return s

    def no(self):
        s = self.score()
        s.track("kit:acoustic").hit("tom3", 0)
        s.track("syn:bass").note("D2", 0, 0.2, bend=-7)
        return s

    def found(self):                      # juggle combo
        s = self.score()
        for i in range(4):
            s.track("kit:acoustic", 0.9).hit("snare" if i % 2 else "floor", i * 0.06)
        s.track("syn:lead").seq("D5 F5 A5 D6", 0.06, t=0.05)
        return s

    def home(self):
        s = self.score()
        s.track("syn:brass").seq("D4 F4 A4 D5*3 C#5 D5*4", 0.1)
        s.track("kit:acoustic", 0.8).beat({"floor": "x...x...x", "crash": "x"}, 0.1)
        return s


# ---------------------------------------------------------------- Tournament Gong

class TournamentGong(GameTheme):
    id = "tournament-gong"
    name = "Tournament Gong"
    category = "game"
    tagline = "Choose your fighter. Mind the gong."
    blurb = ("A dark martial-arts tournament: a giant gong, deep choir, war drums and a pentatonic "
             "flute that drifts in from somewhere ominous.")
    skin = {"bg": "#1a0708", "surface": "#2e0f10", "ink": "#f5e2c0", "muted": "#a3785c",
            "accent": "#d62b1f", "font": "Cinzel Decorative"}
    root, scale, step = "E4", MINOR_PENTA, 0.12
    lead, alt, bass, kit = "syn:whistle", "syn:choir", "syn:sub", "kit:acoustic"
    alert = "fm:marimba"
    master = [("reverb", {"size": 1.6, "wet": 0.33, "predelay": 0.03})]

    def _gong(self, s, t=0.0, vol=1.0):
        s.track("fm:bell", vol).note("E3", t, 1.2, decay=0.9)
        s.track("kit:acoustic", vol * 0.8).hit("crash", t, 0.8)

    def startup(self):
        s = self.score()
        self._gong(s)
        s.track("syn:choir", 0.6).chord("E3+B3", 0.3, 1.5)
        s.track("syn:whistle", 0.8).seq("E5*2 G5 A5*2 B5*3", 0.14, t=0.6)
        s.track("kit:acoustic", 0.8).beat({"floor": "x...x.x.x...", "tom1": "..x...x..."}, 0.1, t=0.4)
        return s

    def arm(self):
        s = self.score()
        self._gong(s, 0, 0.9)
        s.track("kit:acoustic", 0.9).beat({"floor": "xx"}, 0.09, t=0.4)
        s.track("syn:choir").chord("E3+B3+E4", 0.5, 0.6)
        return s

    def disarm(self):
        s = self.score()
        s.track("kit:acoustic").hit("floor", 0)
        s.track("syn:choir").seq("B3 G3 E3*3", 0.14)
        return s

    def lowbat(self):                     # low health drum
        s = self.score()
        s.track("kit:acoustic", 0.9).beat({"floor": "x.x."}, 0.14)
        s.track("syn:whistle", 0.6).seq("G5 E5", 0.15, t=0.05)
        return s

    def critbat(self):
        s = self.score(fx=[])
        s.track("fm:marimba").seq("B5 E5 " * 3, 0.1, gap=0.6, decay=0.05)
        return s

    def yes(self):                        # hit landed
        s = self.score()
        s.track("kit:acoustic").hit("floor", 0)
        s.track("syn:whistle", 0.8).seq("E5 B5", 0.06, t=0.03)
        return s

    def no(self):
        s = self.score()
        s.track("syn:sub").note("E2", 0, 0.25, bend=-7)
        return s

    def found(self):                      # bell chime
        s = self.score()
        s.track("fm:bell", 0.9).seq("E5 G5 B5 E6", 0.08, decay=0.3)
        return s

    def error(self):                      # flawless defeat
        s = self.score()
        self._gong(s, 0, 0.8)
        return s

    def home(self):                       # victory
        s = self.score()
        self._gong(s, 0, 0.6)
        s.track("syn:whistle").seq("E5 G5 A5 B5*2 E6*3", 0.11, t=0.2)
        s.track("syn:choir", 0.7).chord("E3+B3+E4", 0.3, 1.2)
        return s


# ---------------------------------------------------------------- Rally Stage

class RallyStage(GameTheme):
    id = "rally-stage"
    name = "Rally Stage"
    category = "game"
    tagline = "Hairpin left, flat over the crest, gravel everywhere."
    blurb = ("A 90s arcade rally cabinet: a co-driver's pace-note beeps, revving engines, turbo whistles "
             "and a slap-bass checkpoint jingle. Continue? 9, 8, 7...")
    skin = {"bg": "#2b1a0a", "surface": "#f2d8a7", "ink": "#3b1f06", "muted": "#8b6a3a",
            "accent": "#e2231a", "font": "Russo One"}
    root, scale, step = "G4", MIXOLYDIAN, 0.08
    lead, alt, bass, kit = "fm:brass", "fm:lead", "fm:bass", "kit:909"
    alert = "chip:p50"

    def startup(self):                    # stage select, slap bass + brass
        s = self.score()
        s.track("fm:bass", 1.0).seq("G2 G3 G2 R G2 F3 G2 R G2 G3 F2 F3 G2*3", 0.085)
        s.track("fm:brass", 0.8).seq("D5 D5 F5 G5*2 A5 G5 F5 D5*4", 0.085, t=0.2)
        s.track("kit:909", 0.7).beat({"kick": "x..x..x..x..x...", "hat": "..x...x...x...x."}, 0.085)
        return s

    def arm(self):                        # engine rev + green light
        s = self.score()
        s.track("fm:lead", 0.8).note("G3", 0, 0.55, bend=12, steps=24, vib=0.5, vib_rate=22)
        s.track("fx:whoosh", 0.5).note("C4", 0.1, 0.5)
        s.track("chip:p50").seq("G6*2", 0.15, t=0.6)
        return s

    def disarm(self):
        s = self.score()
        s.track("fm:lead").note("G4", 0, 0.5, bend=-12, steps=16)
        return s

    def lowbat(self):                     # time running out
        s = self.score()
        s.track("chip:p50").seq("D6 R D6 R D6 R", 0.09)
        s.track("fm:bass", 0.8).note("G2", 0, 0.5)
        return s

    def critbat(self):
        s = self.score(fx=[])
        s.track("chip:p50").seq("D7 A6 " * 3, 0.1, gap=0.6, decay=0.05)
        return s

    def yes(self):                        # checkpoint beep
        s = self.score()
        s.track("chip:p50").seq("G6 D7", 0.06)
        return s

    def no(self):                         # skid
        s = self.score()
        s.track("fx:whoosh", 0.7).note("C5", 0, 0.3)
        return s

    def found(self):                      # extended play
        s = self.score()
        s.track("fm:brass").seq("D5 G5 D6*3", 0.07)
        return s

    def launch(self):                     # turbo whistle
        s = self.score()
        s.track("syn:whistle", 0.8).note("G5", 0, 0.5, bend=12, steps=12)
        s.track("fm:lead", 0.7).note("G3", 0, 0.6, bend=24, steps=24)
        return s

    def home(self):                       # goal! trophy!
        s = self.score()
        s.track("fm:brass").seq("D5 G5 A5 D6*3 C6 D6*4", 0.09)
        s.track("fm:bass", 0.9).seq("G2*3 G2 G2 D3 G2*4", 0.09)
        s.track("kit:909", 0.6).beat({"kick": "x...x...x...", "crash": "x"}, 0.09)
        return s


# ---------------------------------------------------------------- Jungle Rumble

class JungleRumble(GameTheme):
    id = "jungle-rumble"
    name = "Jungle Rumble"
    category = "game"
    tagline = "Barrel blasts, banana bunches and a very warm reverb."
    blurb = ("Steel-pan and marimba in a humid jungle: bongo rolls, a rubbery bass, water drips and "
             "the swingy sixteenth-note groove of a primate-powered platformer.")
    skin = {"bg": "#123524", "surface": "#f4e2a5", "ink": "#1e3b12", "muted": "#7a8f3a",
            "accent": "#f0a500", "font": "Fredoka"}
    root, scale, step = "F5", PENTA, 0.09
    lead, alt, bass, kit = "fm:marimba", "fm:kalimba", "fm:bass", "kit:acoustic"
    alert = "fm:marimba"
    master = [("reverb", {"size": 1.4, "wet": 0.28, "predelay": 0.02})]

    def startup(self):
        s = self.score()
        s.track("fm:marimba").seq("F5 A5 C6 F6*2 E6 C6 A5 C6*3", 0.1)
        s.track("fm:kalimba", 0.6).seq("C6 R A5 R C6 R F6 R", 0.2, t=0.15)
        s.track("fm:bass", 0.9).seq("F2 R F3 R C3 R F3 R F2*3", 0.1)
        s.track("kit:acoustic", 0.7).beat({"tom1": "x.x..x.x..x.", "tom2": "..x..x.x.x.."}, 0.1)
        return s

    def arm(self):                        # barrel cannon
        s = self.score()
        s.track("kit:acoustic").hit("floor", 0)
        s.track("fm:marimba").note("F4", 0.05, 0.4, bend=24, steps=12)
        s.track("fx:bubble", 0.5).note("C5", 0.45, 0.2)
        return s

    def disarm(self):
        s = self.score()
        s.track("fm:marimba").seq("C6 A5 F5*3", 0.07)
        return s

    def lowbat(self):
        s = self.score()
        s.track("fm:kalimba").seq("C6 R C6 R A5", 0.1)
        return s

    def critbat(self):
        s = self.score(fx=[])
        s.track("fm:marimba").seq("C7 G6 " * 3, 0.1, gap=0.6, decay=0.05)
        return s

    def yes(self):                        # banana
        s = self.score()
        s.track("fm:kalimba").seq("F6 C7", 0.05)
        return s

    def no(self):                         # oof
        s = self.score()
        s.track("fm:bass").note("C3", 0, 0.2, bend=-7)
        return s

    def found(self):                      # bonus room
        s = self.score()
        s.track("fm:marimba").seq("F5 G5 A5 C6 D6 F6", 0.05)
        return s

    def home(self):                       # level complete
        s = self.score()
        s.track("fm:marimba").seq("F5 A5 C6 F6*2 E6 F6*4", 0.09)
        s.track("kit:acoustic", 0.7).beat({"tom1": "x.x.x.xx", "crash": "x"}, 0.09)
        s.track("fm:bass").seq("F2*4 C3*2 F2*3", 0.09)
        return s


# ---------------------------------------------------------------- Nocturne Keep

class NocturneKeep(GameTheme):
    id = "nocturne-keep"
    name = "Nocturne Keep"
    category = "game"
    tagline = "Whip the candles. Beware the clock tower."
    blurb = ("A gothic castle at midnight: harpsichord runs, church organ, tolling bells and a driving "
             "bass line. Baroque minor-key drama for the vampire hunter in you.")
    skin = {"bg": "#0d0716", "surface": "#1e1230", "ink": "#e9dcff", "muted": "#9a83c0",
            "accent": "#c4142c", "font": "IM Fell English SC"}
    root, scale, step = "A4", HARM_MINOR, 0.08
    lead, alt, bass, kit = "fm:harpsi", "syn:organ", "fm:bass", "kit:acoustic"
    alert = "fm:harpsi"
    master = [("reverb", {"size": 1.4, "wet": 0.3})]

    def startup(self):                    # tolling bell + harpsichord run + pedal bass
        s = self.score()
        s.track("fm:bell", 0.9).note("A3", 0, 1.0, decay=0.8)
        s.track("fm:harpsi").seq("A4 C5 E5 A5 G#5 E5 C5 B4 E5 G#5 B5 E6*3", 0.075, t=0.3)
        s.track("syn:organ", 0.5).chord("A2+E3", 0.3, 1.5)
        s.track("fm:bass", 0.8).seq("A2 A2 R A2 A2 R E2*3", 0.1, t=0.3)
        return s

    def arm(self):                        # door creaks open: organ chord
        s = self.score()
        s.track("syn:organ").chord("A3+C4+E4+A4", 0, 0.7)
        s.track("fm:harpsi").seq("E5 A5 C6 E6", 0.06, t=0.1)
        return s

    def disarm(self):
        s = self.score()
        s.track("fm:harpsi").seq("E6 C6 A5 E5", 0.07)
        s.track("syn:organ", 0.7).chord("A2+E3", 0.1, 0.5)
        return s

    def lowbat(self):
        s = self.score()
        s.track("fm:bell", 0.8).seq("A4 R A4 R", 0.16, decay=0.3)
        return s

    def critbat(self):
        s = self.score(fx=[])
        s.track("fm:harpsi").seq("E6 B5 " * 3, 0.1, gap=0.6, decay=0.05)
        return s

    def yes(self):                        # candle whipped: heart pickup
        s = self.score()
        s.track("fm:harpsi").seq("A5 E6", 0.05)
        return s

    def no(self):
        s = self.score()
        s.track("fm:bass").seq("E3 A2*2", 0.07)
        return s

    def found(self):
        s = self.score()
        s.track("fm:harpsi").seq("A5 C6 E6 A6 G#6 A6", 0.05)
        return s

    def lost(self):                       # bat swarm
        s = self.score()
        s.track("fm:harpsi", 0.9).seq("E6 D#6 E6 D#6 E6 D#6", 0.05, gap=0.2, bend=-1)
        return s

    def home(self):                       # boss defeated: organ fanfare
        s = self.score()
        s.track("syn:organ").seq("A3+E4 C4+A4 E4+A4*2 G#4+B4 A4+C5*4", 0.1)
        s.track("fm:bell", 0.6).note("A3", 0, 1.0, decay=0.8)
        return s
