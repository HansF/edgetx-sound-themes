# Stickbeats: EdgeTX voice packs and sound themes

**Voice packs** in 16 languages, previewable phrase by phrase, plus premium ElevenLabs voices made for this project: Dutch (Flemish and standard), British, Australian and Scottish English. The voices live in the [edgetx-sdcard-sounds fork](https://github.com/HansF/edgetx-sdcard-sounds); `voices_build.py` turns that repo into the site's catalogue, previews, hosted zips and one crawlable page per voice (`site/v/<id>.html`). Official EdgeTX voices are previewed here and downloaded from the EdgeTX release. In CI the voice repo is fetched as a sparse partial clone (`voices_build.py --sparse-patterns`); locally, set `EDGETX_VOICES_SRC` or keep the fork next to this checkout.

**Sound themes:** 30 free sound themes for EdgeTX radios. Each one replaces the radio's beeps, warnings and callouts (boot, arm/disarm, low battery, telemetry lost, RF critical, timers, trims, flight modes…) with sounds composed for that theme.

**Site:** https://hansf.github.io/edgetx-sound-themes/ lets you listen to every sound, compare themes, build your own mix and download ready-to-copy SD card packs.

| Category | Themes |
| --- | --- |
| Retro consoles | 8-Bit Hero, Block Drop, Pocket DMG, Blast Processing, 16-Bit Quest, Arcade '82 |
| Old PCs & phones | PC Speaker, AdLib FM, Dial-Up '98, Polyphonic 2003 |
| Screen & story | Wizard Academy, Chopper Command '84, Starship Bridge, Imperial Fleet, Neon Grid, Signal from Beyond, Haunted Manor, Medieval Bard |
| Sim & tycoon | Life Sim, Theme Park '99, City Planner 2000 |
| Gen Z, Gen Alpha & weird | Brainrot, Drift Phonk, Hyperpop, Kazoo Orchestra, Cat Mode, Rubber Duck Squad, NPC Mode, Elevator Bossa, Lo-fi Study |

All music is original, except public-domain tunes (Korobeiniki, Tárrega's Gran Vals). The themes are in the spirit of their eras; they are not affiliated with any game, film or TV show.

## Install a pack

Unzip it and copy its `SOUNDS` folder onto the root of the radio's SD card. Only the 70 event files are replaced; spoken numbers and units stay. See [install](https://hansf.github.io/edgetx-sound-themes/install.html).

## How it works

Every sound is a `Score` (`soundgen/score.py`): tracks of notes with bends, vibrato and drum hits. It is written out as a real MIDI file (shipped in each theme's MIDI zip) and rendered by `soundgen/render.py`:

- `chip:*`: NES/Game Boy pulse, triangle, wave and noise channels, and a 1-bit PC speaker
- `syn:*`: supersaws, synth brass, reese bass, theremin, Karplus-Strong strings, organ, calliope…
- `fm:*`: 2- and 3-operator FM (e-piano, bells, marimba, OPL/YM-style patches)
- `kit:*`: 808 / 909 / chip / phonk drum machines
- `fx:*`: procedural effects (vine boom, air horn, modem handshake, meows, rubber ducks, coaster screams…)
- `gm:<program>`: General MIDI instruments via FluidSynth and the GeneralUser GS soundfont

`soundgen/roles.py` maps each EdgeTX file to a role (`arm`, `lowbat`, `signal_crit`, …). `soundgen/theme.py` gives every role a template default, and each theme in `soundgen/themes/` overrides the roles that define it.

Output is 16 kHz, mono, 16-bit WAV, loudness-matched (-15 dBFS RMS, -1 dBFS peak).

## Build

Needs Python 3.11+, [uv](https://docs.astral.sh/uv/), `ffmpeg`, `fluidsynth` and the [GeneralUser GS](https://schristiancollins.com/generaluser.php) soundfont at `~/.cache/edgetx-sound-themes/GeneralUser-GS.sf2` (or set `EDGETX_SF2`).

```sh
uv run pytest -q                 # every theme must pass the safety checks
uv run build.py                  # all packs -> out/<theme>/SOUNDS/en + out/<theme>/midi
uv run build.py cat-mode         # one theme
uv run build.py --site           # + site/data, previews, zips, voice catalogue; then serve site/
uv run build.py --private        # + personal themes from private_themes/ (gitignored) -> private/
uv run build.py --private --masters ~/my-sounds   # ...with your own WAVs layered on top
```

`private_themes/` is for packs you keep to yourself, such as recreations of copyrighted game sounds. It is gitignored, never built by CI and never published.

Pushing to `main` runs the tests, builds everything and deploys `site/` to GitHub Pages (`.github/workflows/pages.yml`).

## Adding a theme

Create `soundgen/themes/<file>.py` with a `Theme` subclass: set `id`, `name`, `category`, `tagline`, `blurb`, `skin` and a palette, then write at least `startup`, `arm`, `disarm`, `yes`, `no`, `lowbat`, `critbat`, `found` and `lost`. It's registered automatically. The tests enforce:

- all 70 files, valid format, loudness in range
- alerts at most 1.2 s, everything at most 2 s
- arm differs from disarm, on differs from off
- critical alerts have at least 3 separate bursts

## License

Sounds and MIDI: CC0. Code: MIT. See [LICENSE](LICENSE).
