from ..theme import Theme, MAJOR


class EightBitHero(Theme):
    """NES 2A03: two pulse channels, 4-bit triangle, LFSR noise."""
    id = "8bit-hero"
    name = "8-Bit Hero"
    category = "retro"
    tagline = "Pulse, triangle, noise. Nothing else."
    blurb = ("Two square channels, a stepped triangle bass and the noise channel of a 1985 console. "
             "Coins, jumps, pipes and power-ups for every radio event.")
    skin = {"bg": "#5c94fc", "surface": "#fcfcfc", "ink": "#000000", "muted": "#3c3c3c",
            "accent": "#e45c10", "font": "Press Start 2P"}
    root, scale, step = "C6", MAJOR, 0.075
    lead, alt, bass, kit = "chip:p25", "chip:p50", "chip:tri", "kit:chip"

    def startup(self):
        s = self.score()
        arp = ["C5", "E5", "G5", "C6", "E6", "G6", "C7", "E7"]
        s.track("chip:p25").arp(arp, 0.055)
        s.track("chip:p25").note("G7", 8 * 0.055, 0.22)
        s.track("chip:p25").note("E7", 8 * 0.055 + 0.22, 0.3, decay=0.15)
        s.track("chip:p50", 0.35).arp(["G4", "C5", "E5", "G5", "C6", "E6", "G6", "C7"], 0.055)
        tri = s.track("chip:tri", 0.9)
        tri.note("C3", 0, 0.33)
        tri.note("G3", 0.33, 0.2)
        tri.note("C4", 0.53, 0.3)
        s.track("kit:chip", 0.6).beat({"kick": "x...x...", "hat": "..x...x."}, 0.055)
        return s

    def arm(self):                       # extra life
        s = self.score()
        s.track("chip:p50").seq("E6 G6 E7 C7 D7 G7*2", 0.075, gap=0.05)
        return s

    def disarm(self):                    # down the pipe
        s = self.score()
        for i in range(3):
            s.track("chip:p50").note("F5", i * 0.14, 0.11, bend=-17, steps=8)
        return s

    def yes(self):                       # coin
        s = self.score()
        tr = s.track("chip:p25")
        tr.note("B5", 0, 0.07)
        tr.note("E6", 0.07, 0.4, decay=0.14)
        return s

    def no(self):                        # bump
        s = self.score()
        s.track("chip:tri").note("F3", 0, 0.16, bend=-14)
        s.track("chip:noise", 0.5).note("C4", 0, 0.07, decay=0.025)
        return s

    def found(self):                     # power-up
        s = self.score()
        s.track("chip:p50").seq("C5 E5 G5 C6 D5 F#5 A5 D6 E5 G#5 B5 E6 F5 A5 C6 F6", 0.035, gap=0)
        return s

    def lost(self):                      # falling into the pit
        s = self.score()
        s.track("chip:p25").note("E6", 0, 0.62, bend=-45, vib=0.3)
        return s

    def lowbat(self):                    # hurry up
        s = self.score()
        s.track("chip:p25").seq("E6 R F6 R F#6 R G6*3", 0.07)
        s.track("chip:tri").seq("C4 R C#4 R D4 R Eb4*3", 0.07)
        return s

    def critbat(self):
        s = self.score()
        t = s.track("chip:p25").seq("C7 A6 C7 A6", 0.085, gap=0.5)
        s.track("chip:p25").seq("C6 B5 Bb5 A5 Ab5 G5", 0.055, t + 0.03)
        s.track("chip:tri").note("G3", t + 0.03, 0.35, bend=-12)
        return s

    def signal_warn(self):               # pause jingle-ish two-tone
        s = self.score()
        s.track("chip:p25").seq("E6 C6 E6 C6", 0.08)
        return s

    def signal_crit(self):
        s = self.score()
        s.track("chip:p25").seq("E6 C6 E6 R " * 4, 0.045, gap=0.15)
        return s

    def error(self):
        s = self.score()
        s.track("chip:p12").note("A2", 0, 0.28, vib=0.9, vib_rate=30)
        s.track("chip:p12").note("F#2", 0.34, 0.28, vib=0.9, vib_rate=30)
        return s

    def warn_a(self):                    # small jump
        s = self.score()
        s.track("chip:p25").note("D5", 0, 0.16, bend=17, steps=10)
        return s

    def warn_b(self):                    # super jump
        s = self.score()
        s.track("chip:p25").note("A4", 0, 0.3, bend=33, steps=18, vib=0.4)
        return s

    def powerdown(self):                 # shrink
        s = self.score()
        s.track("chip:p50").seq("A6 E6 G6 D6 F6 C6 E6 B5 D6 A5", 0.045, gap=0)
        return s

    def flip(self):                      # spin jump
        s = self.score()
        for i in range(4):
            s.track("chip:p25").note("D5", i * 0.08, 0.07, bend=26, steps=6)
        return s

    def land(self):                      # flagpole slide + thud
        s = self.score()
        s.track("chip:p25").note("G7", 0, 0.7, bend=-38, vib=0.3)
        s.track("chip:tri").note("F3", 0.72, 0.16, bend=-14)
        s.track("chip:noise", 0.5).note("C4", 0.72, 0.07, decay=0.025)
        return s

    def home(self):                      # castle-clear style fanfare (original)
        s = self.score()
        s.track("chip:p25").seq("G5 C6 E6 G6*2 E6 G6*4", 0.08)
        s.track("chip:p50", 0.5).seq("E5 G5 C6 E6*2 C6 E6*4", 0.08)
        s.track("chip:tri", 0.8).seq("C4*4 G3*2 C4*4", 0.08)
        return s

    def cut(self):
        s = self.no()
        s.track("chip:tri").note("C3", 0.18, 0.15)
        return s

    def thr_on(self):                    # fireball
        s = self.score()
        s.track("chip:noise", 0.5).note("C6", 0, 0.06, decay=0.02)
        s.track("chip:p25").note("G7", 0, 0.09, bend=-23)
        return s

    def timer(self, n):
        s = self.score()
        for i in range(n):
            s.merge(self.yes(), at=i * 0.2)
        return s
