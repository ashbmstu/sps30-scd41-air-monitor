# Contributing to sps30-scd41-air-monitor

Thank you for considering a contribution. This is a small piece of MicroPython
for a specific set of parts, and most changes to it only mean anything on a real
box with real sensors in it.

## Before you open a pull request

There is no simulator. CI checks that the files parse, that the pin numbers
agree across the code, the wiring table and the diagram, and that the links in
the documentation resolve. It cannot talk to a sensor or refresh a panel.
Anything past that has to be tried on hardware.

If your change touches the measurement path, say in the pull request what you
saw before and after, and under what conditions. A reading taken alongside a
reference instrument, or a spike-and-decay curve from a match or a candle, is
worth far more than an argument about the arithmetic.

## Running the checks locally

```bash
python -m compileall -q src tools
python tools/check-pins.py
```

## Code style

- MicroPython, 4-space indent, no tabs.
- `snake_case` for functions and variables.
- Match the style of `src/main.py` and `src/sps30uart.py`.
- Comments explain why, not what. Most of this code needs none.
- Catch `Exception`, not a bare `except:`. A bare except swallows Ctrl+C, which
  makes a board running a tight sensor loop very tedious to interrupt.

`src/DEPG0213BN.py`, `src/scd4x_sensirion.py` and everything under
`src/sensor_pack_2/` are carried unmodified from upstream so they can be checked
against it. Please do not edit them, including to translate their comments. If
one needs to behave differently, wrap it rather than patching it, and say in the
pull request why upstream will not do.

## Credentials

Never commit a `config.py`. It is in `.gitignore`, it holds a Wi-Fi password and
a ThingSpeak write key, and git remembers a file long after it is deleted. The
same goes for a screenshot of a console with a key in it.

## Commit messages

Use an imperative subject line under about 72 characters, with no type prefix.
In the body, explain the reasoning. When a change comes from something you
measured, say what you measured and with what.

## Reporting a problem with a box you built

Useful reports include:

- What the panel shows, and what the serial console prints once a second
- Whether it is on USB or on battery, since the particulate sensor only runs on
  USB
- MicroPython version (`import sys; sys.implementation` at the REPL)
- Which T5 revision and which e-paper panel, and which SCD4x part
- The output of an I²C scan — see
  [troubleshooting.md](docs/troubleshooting.md#scd41-err-where-the-co2-rows-should-be)

Open bugs through GitHub Issues on this repository.
