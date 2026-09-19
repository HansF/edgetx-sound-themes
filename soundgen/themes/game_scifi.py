"""Game homages, part 2: survival horror, spy, lab, alien depths, shoot-'em-up.

Original motifs in the spirit of each genre. No melodies, names or samples from any game.
"""
from .game_base import GameTheme
from ..theme import MINOR, HARM_MINOR, DORIAN, PHRYGIAN, MIXOLYDIAN, BLUES


# ---------------------------------------------------------------- Safe Room

class SafeRoom(GameTheme):
    id = "safe-room"
    name = "Safe Room"
    category = "game"
    tagline = "Save point reached. Ammunition is limited."
    blurb = ("Slow piano in a dark mansion, a typewriter click, a heartbeat that never quite settles and "
             "shrieking strings when something opens the door.")
    skin = {"bg": "#160f0d", "surface": "#251814", "ink": "#e9d9b8", "muted": "#9a7f66",
            "accent": "#b3201a", "font": "IM Fell English"}
    root, scale, step = "D5", HARM_MINOR, 0.14
    lead, alt, bass, kit = "fm:epiano", "syn:pad", "syn:sub", "kit:acoustic"
    alert = "fm:marimba"
    master = [("reverb", {"size": 1.5, "wet": 0.35, "predelay": 0.03})]

    def startup(self):                    # save room piano
        s = self.score()
        s.track("fm:epiano", 0.9).seq("D4*2 F4 A4*2 C#5 A4*3 E4 F4*2 D4*4", 0.17)
        s.track("syn:pad", 0.4).chord("D3+A3+F4", 0, 1.9)
        return s

    def arm(self):                        # typewriter clicks, then a door
        s = self.score(fx=[("reverb", {"size": 0.6, "wet": 0.15})])
        s.track("fx:click", 0.7).seq("C5 C5 C5 R C5 C5", 0.06)
        s.track("syn:sub", 0.9).note("D2", 0.42, 0.35)
        s.track("fm:epiano").chord("D4+A4", 0.42, 0.5)
        return s

    def disarm(self):
        s = self.score()
        s.track("fm:epiano").seq("A4 F4 D4*3", 0.14)
        return s

    def lowbat(self):                     # heartbeat
        s = self.score()
        s.track("fx:heartbeat", 0.9).note("C2", 0, 0.9)
        return s

    def critbat(self):
        s = self.score(fx=[])
        tr = s.track("syn:sub", 1.0)
        for i in range(4):
            tr.note("D2", i * 0.22, 0.09, decay=0.06)
            tr.note("D2", i * 0.22 + 0.1, 0.06, 0.6, decay=0.05)
        return s

    def yes(self):
        s = self.score()
        s.track("fm:epiano").seq("D5 A5*2", 0.09)
        return s

    def no(self):
        s = self.score()
        s.track("fm:epiano").seq("A4 C#4*2", 0.09)
        return s

    def found(self):                      # item pickup
        s = self.score()
        s.track("fm:celesta", 0.9).seq("D6 F6 A6 D7", 0.06)
        return s

    def lost(self):                       # strings screech
        s = self.score()
        s.track("fx:sadviolin", 0.7).note("A5", 0, 0.7, bend=-3)
        return s

    def error(self):
        s = self.score()
        s.track("fx:impact", 0.7).note("D2", 0, 0.5)
        return s


# ---------------------------------------------------------------- Agent 64

class Agent64(GameTheme):
    id = "agent-64"
    name = "Agent 64"
    category = "game"
    tagline = "Slick, silenced and slightly too polygonal."
    blurb = ("Twangy surf guitar over low-poly brass, silenced-pistol pops and a briefing-room stinger. "
             "Suave, slightly too polygonal, always in a tuxedo.")
    skin = {"bg": "#0d1522", "surface": "#1a2740", "ink": "#e8edf7", "muted": "#8b9ac0",
            "accent": "#d9b23b", "font": "Oswald"}
    root, scale, step = "E4", HARM_MINOR, 0.1
    lead, alt, bass, kit = "syn:pluck", "fm:brass", "fm:bass", "kit:acoustic"
    alert = "syn:pluck"
    master = [("reverb", {"size": 0.9, "wet": 0.2}), ("chorus", {})]

    def startup(self):                    # briefing stinger: guitar riff + brass hit
        s = self.score()
        s.track("syn:pluck").seq("E3 G3 E3 B3 E3 G3 F#3 E3*4", 0.1)
        s.track("fm:brass", 0.7).chord("E3+G3+B3+D#4", 0.8, 0.8)
        s.track("fm:bass", 0.9).seq("E2*3 E2 G2 E2*3 B1*4", 0.1)
        s.track("kit:acoustic", 0.7).beat({"kick": "x.....x.x.....", "rim": "..x...x...x..."}, 0.1)
        return s

    def arm(self):                        # silenced shot + click
        s = self.score(fx=[("reverb", {"size": 0.5, "wet": 0.12})])
        s.track("kit:acoustic", 0.9).hit("snare", 0)
        s.track("fx:click", 0.8).note("C6", 0.2, 0.05)
        s.track("syn:pluck").seq("E4 B4 E5*3", 0.07, t=0.3)
        return s

    def disarm(self):
        s = self.score()
        s.track("syn:pluck").seq("E5 B4 E4*3", 0.07)
        return s

    def lowbat(self):
        s = self.score()
        s.track("syn:pluck").seq("B4 R B4 R G4 F#4", 0.1)
        return s

    def critbat(self):                    # countdown beeps
        s = self.score(fx=[])
        s.track("syn:sine").seq("E6 " * 6, 0.1, gap=0.6, decay=0.05)
        return s

    def yes(self):
        s = self.score()
        s.track("syn:pluck").seq("E4 B4", 0.06)
        return s

    def no(self):
        s = self.score()
        s.track("syn:pluck").seq("B4 D#4", 0.06)
        return s

    def found(self):                      # gadget unlocked
        s = self.score()
        s.track("syn:sine", 0.7).seq("E6 G6 B6 E7", 0.05)
        s.track("syn:pluck").seq("E4 G4 B4 E5*2", 0.07)
        return s

    def home(self):                       # mission complete
        s = self.score()
        s.track("fm:brass").seq("E4 G4 B4 E5*3 D#5 E5*4", 0.1)
        s.track("syn:pluck", 0.7).seq("E3 B3 E4 B3 E4 G4 E4*4", 0.1)
        return s


# ---------------------------------------------------------------- Hazard Suit

class HazardSuit(GameTheme):
    id = "hazard-suit"
    name = "Hazard Suit"
    category = "game"
    tagline = "Suit systems online. Please remain calm."
    blurb = ("An orange radiation suit's beeps, chirps and warnings: medkit hiss, energy charger, a "
             "distant alarms, plus a heavy metal bar clang for good measure.")
    skin = {"bg": "#1a1206", "surface": "#2d2008", "ink": "#ffb428", "muted": "#a3782a",
            "accent": "#ff7a00", "font": "VT323"}
    root, scale, step = "A5", MINOR, 0.08
    lead, alt, bass, kit = "syn:sq", "syn:sine", "syn:sub", "kit:909"
    alert = "syn:sq"
    master = [("bitcrush", {"bits": 9, "hold": 1}), ("reverb", {"size": 0.5, "wet": 0.1})]

    def startup(self):                    # suit boot sequence
        s = self.score()
        s.track("syn:sq", 0.6).seq("A5 R A5 R E6 R A6*3", 0.08)
        s.track("syn:sine", 0.7).note("A3", 0.2, 1.0, bend=12, steps=8)
        s.track("syn:sub").note("A2", 0, 1.4, bend=7)
        s.track("fx:static", 0.4).note("C4", 0.9, 0.5)
        return s

    def arm(self):                        # weapon selected + charger ping
        s = self.score()
        s.track("syn:sq").seq("E6 A6 E7*2", 0.06)
        s.track("syn:sub", 0.9).note("A2", 0, 0.3)
        return s

    def disarm(self):
        s = self.score()
        s.track("syn:sq").seq("E7 A6 E6*2", 0.06)
        return s

    def lowbat(self):                     # "power level low"
        s = self.score()
        s.track("syn:sq").seq("A5 E5 A5 E5", 0.11)
        return s

    def critbat(self):                    # flatline-style long-short beeps
        s = self.score(fx=[])
        tr = s.track("syn:sq")
        for i in range(5):
            tr.note("E6", i * 0.14, 0.05, decay=0.04)
        return s

    def yes(self):
        s = self.score()
        s.track("syn:sq").seq("A6 E7", 0.05)
        return s

    def no(self):
        s = self.score()
        s.track("syn:sq").seq("E6 A5*2", 0.06)
        return s

    def found(self):                      # medkit
        s = self.score()
        s.track("fx:whoosh", 0.4).note("C6", 0, 0.3)
        s.track("syn:sq").seq("A6 R A6 R E7", 0.05, t=0.15)
        return s

    def lost(self):
        s = self.score()
        s.track("fx:static", 0.6).note("C4", 0, 0.4)
        s.track("syn:sq").note("A5", 0, 0.5, bend=-24)
        return s

    def error(self):                      # metal bar clang
        s = self.score()
        s.track("fm:bell", 0.9).note("D4", 0, 0.5, decay=0.3)
        s.track("kit:909").hit("crash", 0.0, 0.4)
        return s


# ---------------------------------------------------------------- Bounty Hunter

class BountyHunter(GameTheme):
    id = "bounty-hunter"
    name = "Bounty Hunter"
    category = "game"
    tagline = "Alone on an alien world. Something is watching."
    blurb = ("Sonar pings under dripping caverns, a chilly drone and a shimmering suit-upgrade jingle. "
             "Exploration first, shooting later.")
    skin = {"bg": "#071417", "surface": "#0f2a30", "ink": "#b8f0e0", "muted": "#5f9c90",
            "accent": "#ff8c1a", "font": "Orbitron"}
    root, scale, step = "F#4", PHRYGIAN, 0.12
    lead, alt, bass, kit = "fm:bell", "syn:pad", "syn:sub", "kit:808"
    alert = "syn:sine"
    master = [("reverb", {"size": 1.8, "wet": 0.4, "predelay": 0.03}), ("echo", {"delay": 0.22, "feedback": 0.3})]

    def startup(self):                    # cavern drip + drone
        s = self.score()
        s.track("syn:pad", 0.6).chord("F#2+C#3", 0, 1.9)
        s.track("fm:bell", 0.9).seq("F#5 R C#6 R G5 R F#5", 0.2)
        s.track("fx:ping", 0.5).note("F#6", 0.9, 0.4)
        return s

    def arm(self):                        # upgrade acquired
        s = self.score()
        s.track("fm:celesta").arp(["F#5", "A5", "C#6", "F#6", "A6", "C#7"], 0.06)
        s.track("syn:pad", 0.6).chord("F#3+C#4+A4", 0.1, 0.6)
        return s

    def disarm(self):
        s = self.score()
        s.track("fm:celesta").arp(["C#7", "A6", "F#6", "C#6", "A5", "F#5"], 0.06)
        return s

    def lowbat(self):                     # energy low: slow sonar pings
        s = self.score()
        s.track("fx:ping", 0.9).seq("F#6 R R F#6", 0.16)
        s.track("syn:sub", 0.7).note("F#2", 0, 0.6)
        return s

    def critbat(self):
        s = self.score(fx=[])
        s.track("syn:sine").seq("C#7 " * 6, 0.1, gap=0.6, decay=0.05)
        return s

    def yes(self):
        s = self.score()
        s.track("fm:bell").seq("F#6 C#7", 0.08)
        return s

    def no(self):
        s = self.score()
        s.track("fm:bell").seq("C#6 F#5", 0.1)
        return s

    def found(self):                      # door unlocks
        s = self.score()
        s.track("fm:bell").seq("F#5 A5 C#6 F#6", 0.07)
        s.track("syn:sub").note("F#2", 0, 0.3)
        return s

    def lost(self):
        s = self.score()
        s.track("syn:sine").note("F#5", 0, 0.8, bend=-12, vib=0.4)
        return s

    def home(self):                       # elevator up
        s = self.score()
        s.track("syn:pad").chord("F#3+C#4+A4", 0, 1.2)
        s.track("fm:bell", 0.8).seq("F#5 A5 C#6 F#6*3", 0.15)
        return s


# ---------------------------------------------------------------- Shmup Fury

class ShmupFury(GameTheme):
    id = "shmup-fury"
    name = "Shmup Fury"
    category = "game"
    tagline = "Charge the beam. Ignore the bullets."
    blurb = ("A side-scrolling shoot-'em-up: a charging beam whine, pod-orbit blips, bosses that grumble in "
             "low FM brass and a very long stage of dodging.")
    skin = {"bg": "#0a0a24", "surface": "#161645", "ink": "#d5d9ff", "muted": "#7e83c4",
            "accent": "#ff3d81", "font": "Orbitron"}
    root, scale, step = "A4", DORIAN, 0.07
    lead, alt, bass, kit = "fm:lead", "fm:brass", "fm:bass", "kit:909"
    alert = "fm:marimba"

    def startup(self):                    # stage intro
        s = self.score()
        s.track("fm:lead").seq("A4 C5 E5 A5*2 G5 E5 D5 E5*4", 0.08)
        s.track("fm:brass", 0.5).seq("A3*4 C4*2 E4*2 A3*4", 0.08)
        s.track("fm:bass", 0.9).seq("A2 R A2 R A2 R C3 R A2*4", 0.08)
        s.track("kit:909", 0.6).beat({"kick": "x.x.x.x.x.x.", "snare": "....x.......", "hat": "xxxxxxxxxxxx"}, 0.08)
        return s

    def arm(self):                        # beam charge, release
        s = self.score()
        s.track("fm:lead", 0.8).note("A3", 0, 0.5, bend=24, steps=20)
        s.track("fx:laser", 0.9).note("A5", 0.5, 0.4)
        s.track("kit:909").hit("crash", 0.5, 0.6)
        return s

    def disarm(self):
        s = self.score()
        s.track("fm:lead").note("A6", 0, 0.5, bend=-30, steps=16)
        return s

    def lowbat(self):
        s = self.score()
        s.track("fm:brass").seq("A3 R A3 R E3*2", 0.11)
        s.track("fx:siren", 0.3).note("A4", 0, 0.5)
        return s

    def critbat(self):
        s = self.score(fx=[])
        s.track("fm:marimba").seq("A6 E6 " * 3, 0.1, gap=0.6, decay=0.05)
        return s

    def yes(self):                        # power-up capsule
        s = self.score()
        s.track("fm:lead").seq("A5 E6 A6", 0.05)
        return s

    def no(self):
        s = self.score()
        s.track("fm:bass").note("A3", 0, 0.2, bend=-12)
        return s

    def found(self):
        s = self.score()
        s.track("fx:zap", 0.8).note("A5", 0, 0.15)
        s.track("fm:lead").seq("E6 A6 C7", 0.05, t=0.12)
        return s

    def home(self):                       # boss defeated
        s = self.score()
        s.track("fx:impact", 0.8).note("A2", 0, 0.5)
        s.track("fm:lead", 0.8).seq("A5 C6 E6 A6*4", 0.09, t=0.3)
        return s
