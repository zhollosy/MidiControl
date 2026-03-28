# MidiControl

PyQt6-based custom Qt widgets for controlling MIDI instruments.

## Features

- Interactive envelope editors with draggable control points
- Custom curve rendering with gradient fill and grid overlay
- Real-time parameter display on hover and drag
- Transform-based coordinate system (Y-axis increases upward)
- All parameters clamped to MIDI range (0-127)

## QMCAmpADSR

Standard ADSR (Attack, Decay, Sustain, Release) amplifier envelope.

![QMCAmpADSR](doc/QMCAmpADSR.png)

```python
adsr = QMCAmpADSR()
adsr.attack_time = 20
adsr.attack_level = 127
adsr.decay_time = 35
adsr.sustain_level = 80
adsr.release_time = 40
```

### Properties

| Property       | Range   | Description                    |
|----------------|---------|--------------------------------|
| `attack_time`  | 0-127   | Attack duration                |
| `attack_level` | 0-127   | Peak level after attack        |
| `decay_time`   | 0-127   | Decay duration                 |
| `sustain_level` | 0-127  | Sustain amplitude level        |
| `release_time` | 0-127   | Release duration               |

## QMCAmpADSR (with Breakpoint mode)

Extended envelope with a decay breakpoint between Attack and Decay, splitting the decay into two stages (Decay1 and Decay2).

![QMCAmpADBSR](doc/QMCAmpADBSR.png)

```python
adbsr = QMCAmpADSR(breakpoint=True)
adbsr.attack_time = 20
adbsr.attack_level = 127
adbsr.breakpoint_time = 25
adbsr.breakpoint_level = 100
adbsr.decay_time = 30
adbsr.sustain_level = 70
adbsr.release_time = 40
```

### Additional Properties

| Property           | Range   | Description                          |
|--------------------|---------|--------------------------------------|
| `breakpoint_time`  | 0-127   | Decay1 duration (Attack to Breakpoint) |
| `breakpoint_level` | 0-127   | Amplitude level at breakpoint        |

## Setup

```bash
python -m venv .venv
.venv/Scripts/activate && pip install -r requirements.txt
```

## Run

```bash
.venv/Scripts/activate && python midiWidgets.py
```
