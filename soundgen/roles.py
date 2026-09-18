"""Which EdgeTX file plays which role, and how long each may run.

Paths are relative to SOUNDS/en/ on the SD card. Labels are the English voice
pack's source texts, so the site can say what each file announces.
"""

# (file, role, args, label)
EVENTS = [
    # power & arming
    ("SYSTEM/hello", "startup", (), "radio boot"),
    ("armed", "arm", (), "armed"),
    ("disarm", "disarm", (), "disarmed"),
    ("SYSTEM/modelpwr", "powerdown", (), "receiver still connected"),
    ("thrcut", "cut", (), "throttle cut"),
    ("thract", "thr_on", (), "throttle active"),
    # startup warnings
    ("SYSTEM/thralert", "warn_a", (), "throttle warning"),
    ("SYSTEM/swalert", "warn_b", (), "switch warning"),
    ("SYSTEM/inactiv", "idle", (), "inactivity alarm"),
    # link & telemetry
    ("SYSTEM/telemko", "lost", (), "telemetry lost"),
    ("SYSTEM/telemok", "found", (), "telemetry recovered"),
    ("SYSTEM/rxko", "signal_crit", (), "receiver signal lost"),
    ("SYSTEM/rssi_org", "signal_warn", (), "RF signal low"),
    ("SYSTEM/rssi_red", "signal_crit", (), "RF signal critical"),
    ("siglow", "signal_warn", (), "RF signal low"),
    ("sigcrt", "signal_crit", (), "RF signal critical"),
    ("SYSTEM/swr_red", "error", (), "radio antenna defective"),
    # battery
    ("lowbat", "lowbat", (), "low battery"),
    ("SYSTEM/lowbatt", "lowbat", (), "transmitter battery low"),
    ("clobat", "critbat", (), "critical low battery"),
    # status
    ("on", "yes", (), "on"), ("off", "no", (), "off"),
    ("good", "yes", (), "good"), ("bad", "no", (), "bad"),
    ("ready", "yes", (), "ready to fly"),
    ("start", "yes", (), "start"), ("stop", "no", (), "stop"),
    ("active", "yes", (), "active"), ("deact", "no", (), "deactivated"),
    ("enabl", "yes", (), "enabled"), ("disabl", "no", (), "disabled"),
    ("recsrt", "yes", (), "recording started"), ("recstp", "no", (), "recording stopped"),
    ("warnng", "warn_a", (), "warning"),
    ("danger", "critbat", (), "danger"),
    ("SYSTEM/sensorko", "error", (), "sensor lost"),
    ("SYSTEM/servoko", "error", (), "servo overload"),
    ("SYSTEM/eebad", "error", (), "storage corrupted"),
    # trainer
    ("SYSTEM/trainco", "yes", (), "trainer connected"),
    ("SYSTEM/trainok", "found", (), "trainer signal recovered"),
    ("SYSTEM/trainko", "no", (), "trainer signal lost"),
    # flight
    ("takeof", "launch", (), "take off"),
    ("alnch", "launch", (), "autolaunch started"),
    ("lnding", "land", (), "landing mode on"),
    ("landin", "land", (), "landing"),
    ("rth", "home", (), "return to home"),
    ("homrst", "home", (), "home reset"),
    ("flip", "flip", (), "flip"),
    ("crshon", "yes", (), "course hold active"),
    ("crshof", "no", (), "course hold off"),
    # timers & trims
    ("SYSTEM/timovr1", "timer", (1,), "timer 1 elapsed"),
    ("SYSTEM/timovr2", "timer", (2,), "timer 2 elapsed"),
    ("SYSTEM/timovr3", "timer", (3,), "timer 3 elapsed"),
    ("SYSTEM/mintrim", "trim", (0,), "trim at minimum"),
    ("SYSTEM/midtrim", "trim", (1,), "trim centered"),
    ("SYSTEM/maxtrim", "trim", (2,), "trim at maximum"),
]
EVENTS += [(f"fm-{i}", "count", (i, 0), f"flight mode {i}") for i in range(1, 9)]
EVENTS += [(f"rates{i}", "count", (i, 4), f"rates {i}") for i in range(1, 7)]

GROUPS = [
    ("Power & arming", ["SYSTEM/hello", "armed", "disarm", "SYSTEM/modelpwr", "thrcut", "thract"]),
    ("Startup warnings", ["SYSTEM/thralert", "SYSTEM/swalert", "SYSTEM/inactiv"]),
    ("Link & telemetry", ["SYSTEM/telemko", "SYSTEM/telemok", "SYSTEM/rxko", "SYSTEM/rssi_org",
                          "SYSTEM/rssi_red", "siglow", "sigcrt", "SYSTEM/swr_red"]),
    ("Battery", ["lowbat", "SYSTEM/lowbatt", "clobat"]),
    ("Status", ["on", "off", "good", "bad", "ready", "start", "stop", "active", "deact", "enabl",
                "disabl", "recsrt", "recstp", "warnng", "danger", "SYSTEM/sensorko",
                "SYSTEM/servoko", "SYSTEM/eebad"]),
    ("Trainer", ["SYSTEM/trainco", "SYSTEM/trainok", "SYSTEM/trainko"]),
    ("Flight", ["takeof", "alnch", "lnding", "landin", "rth", "homrst", "flip", "crshon", "crshof"]),
    ("Timers & trims", ["SYSTEM/timovr1", "SYSTEM/timovr2", "SYSTEM/timovr3",
                        "SYSTEM/mintrim", "SYSTEM/midtrim", "SYSTEM/maxtrim"]),
    ("Flight modes", [f"fm-{i}" for i in range(1, 9)]),
    ("Rates", [f"rates{i}" for i in range(1, 7)]),
]

# Alerts must get out of the way fast; everything else may run a little longer.
ALERT_ROLES = {"warn_a", "warn_b", "lost", "found", "signal_warn", "signal_crit", "lowbat", "critbat", "error"}
CRITICAL_FILES = {"clobat", "SYSTEM/rssi_red", "sigcrt", "SYSTEM/rxko", "danger"}
ALERT_MAX = 1.2
MAX_LEN = 2.0


def max_len(role, args=()):
    if role in ALERT_ROLES:
        return ALERT_MAX
    return MAX_LEN


ROLES = sorted({r for _, r, _, _ in EVENTS})
