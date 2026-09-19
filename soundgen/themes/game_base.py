"""Shared base for the game-homage themes."""
from ..theme import Theme


class GameTheme(Theme):
    """Adds a spaced-out critical alert: six short, clearly separate bursts."""
    alert = None                          # instrument for alerts; defaults to the lead
    alert_decay = 0.07

    def _bursts(self, s, a, b, n=6, step=0.1, vol=1.0, t=0.0):
        tr = s.track(self.alert or self.lead, vol)
        for i in range(n):
            tr.note(a if i % 2 == 0 else b, t + i * step, 0.04, decay=self.alert_decay)
        return t + n * step

    def signal_crit(self):
        s = self.score(fx=[])                 # no reverb: tails would glue the bursts together
        self._bursts(s, self.deg(9), self.deg(7))
        return s
