#!/usr/bin/env python3
"""Check that the code, the wiring table and the diagram agree about pins.

Four GPIO numbers are written down in three places: the constants in
src/main.py, the wiring table in docs/hardware.md, and the labels in
docs/img/wiring.svg.

Two of those four cross over. The board transmits on PIN_TX into the SPS30's
RX, and receives on PIN_RX from its TX, so a wiring table that lines PIN_TX up
against the sensor's TX is wrong in the one way that is hardest to spot and
that costs the most time on the bench. That pairing is asserted below rather
than inferred, so a table edit that quietly un-crosses it fails the build.

The IOnn silkscreen name in the table is checked against the GPIO number in the
same row, which catches a mistyped pin label independently of the code.
"""

import ast
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Constant in main.py -> the (device, pin) it lands on in the wiring table.
CONSTANTS = {
    "PIN_SDA": ("SCD41", "SDA"),
    "PIN_SCL": ("SCD41", "SCL"),
    "PIN_TX": ("SPS30", "RX"),
    "PIN_RX": ("SPS30", "TX"),
}


def from_code():
    """Pull the pin constants out of src/main.py, including tuple assignments."""
    tree = ast.parse((ROOT / "src" / "main.py").read_text(encoding="utf-8"))
    found = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            names, values = [target], [node.value]
            if isinstance(target, ast.Tuple) and isinstance(node.value, ast.Tuple):
                names, values = target.elts, node.value.elts
            for name, value in zip(names, values):
                if (isinstance(name, ast.Name) and name.id in CONSTANTS
                        and isinstance(value, ast.Constant)):
                    found[CONSTANTS[name.id]] = value.value
    return found


def from_table():
    text = (ROOT / "docs" / "hardware.md").read_text(encoding="utf-8")
    found = {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 3 or not re.fullmatch(r"GPIO\d+", cells[2].strip("`")):
            continue
        # Each of the first two cells reads like: SCD41 `SDA`
        signal = re.search(r"`([^`]+)`", cells[0])
        pin = re.search(r"`([^`]+)`", cells[1])
        if not signal or not pin:
            continue
        device = "SCD41" if "SCD41" in cells[0] else "SPS30"
        found[(device, signal.group(1))] = (pin.group(1), int(cells[2].strip("`")[4:]))
    return found


def from_diagram():
    """Collect the GPIO numbers labelled in the diagram.

    Only the set is compared, not the pairing. Tying the check to the exact
    coordinates of each label would break every time the diagram is redrawn,
    which is a worse failure than the one it would catch; the table above
    already pins down which signal goes where.
    """
    svg = ET.parse(ROOT / "docs" / "img" / "wiring.svg")
    labels = [el.text.strip() for el in svg.iter()
              if el.tag.endswith("text") and el.text]
    return {int(m.group(1)) for t in labels
            for m in [re.match(r"GPIO(\d+)", t)] if m}


def main():
    code, table, diagram = from_code(), from_table(), from_diagram()
    problems = []

    for key in sorted(CONSTANTS.values()):
        device, signal = key
        where = f"{device} {signal}"

        if key not in code:
            problems.append(f"{where}: no matching constant in src/main.py")
            continue
        gpio = code[key]

        if key not in table:
            problems.append(f"{where}: missing from docs/hardware.md")
            continue
        pin, said = table[key]

        if said != gpio:
            problems.append(
                f"{where}: src/main.py says GPIO{gpio}, docs/hardware.md says GPIO{said}")
        if pin.upper() != f"IO{said}":
            problems.append(
                f"{where}: docs/hardware.md pairs {pin} with GPIO{said}")

    in_code = set(code.values())
    if diagram != in_code:
        problems.append(
            f"docs/img/wiring.svg labels GPIOs {sorted(diagram)}, "
            f"but src/main.py uses {sorted(in_code)}")

    if problems:
        print("Pin definitions disagree:")
        for p in problems:
            print("  " + p)
        return 1

    for (device, signal), gpio in sorted(code.items()):
        print(f"{device} {signal}: GPIO{gpio} - code, table and diagram agree")
    return 0


if __name__ == "__main__":
    sys.exit(main())
