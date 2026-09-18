"""Every theme must produce a complete, safe EdgeTX pack."""
import wave

import numpy as np
import pytest

from soundgen.export import RMS_DB, build_theme
from soundgen.roles import CRITICAL_FILES, EVENTS, max_len
from soundgen.themes import REGISTRY


def read(path):
    with wave.open(str(path)) as w:
        assert (w.getnchannels(), w.getsampwidth(), w.getframerate()) == (1, 2, 16000), path
        return np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(float) / 32768


def onsets(y, frame=80):
    """Count distinct bursts (hysteresis on a 5 ms RMS envelope)."""
    n = len(y) // frame
    env = np.sqrt(np.mean(y[: n * frame].reshape(n, frame) ** 2, axis=1))
    env = env / (env.max() or 1)
    count, armed = 0, True
    for v in env:
        if armed and v > 0.5:
            count, armed = count + 1, False
        elif v < 0.22:
            armed = True
    return count


@pytest.fixture(scope="module", params=sorted(REGISTRY))
def pack(request, tmp_path_factory):
    d = tmp_path_factory.mktemp(request.param)
    index = build_theme(REGISTRY[request.param], d)
    return request.param, d, index


def test_complete_and_valid(pack):
    tid, d, index = pack
    assert len(index) == len(EVENTS)
    for file, role, args, _ in EVENTS:
        y = read(d / "SOUNDS" / "en" / f"{file}.wav")
        dur = len(y) / 16000
        assert 0.04 < dur <= max_len(role, args) + 0.01, f"{tid}/{file}: {dur:.2f}s"
        assert np.abs(y).max() < 0.95, f"{tid}/{file} clips"
        loud = np.sort(np.abs(y))[len(y) // 2:]
        rms_db = 20 * np.log10(np.sqrt(np.mean(loud ** 2)) + 1e-9)
        assert RMS_DB - 7 < rms_db < RMS_DB + 2, f"{tid}/{file}: loudness {rms_db:.1f} dB"
        assert (d / "midi" / f"{file}.mid").stat().st_size > 30


def test_arm_and_disarm_differ(pack):
    tid, d, index = pack
    assert index["armed"]["hash"] != index["disarm"]["hash"]
    assert index["on"]["hash"] != index["off"]["hash"]


@pytest.mark.parametrize("file", sorted(CRITICAL_FILES))
def test_critical_alerts_repeat(pack, file):
    """Critical alerts must be urgent: at least 3 distinct bursts."""
    tid, d, _ = pack
    y = read(d / "SOUNDS" / "en" / f"{file}.wav")
    assert onsets(y) >= 3, f"{tid}/{file}: only {onsets(y)} bursts"
