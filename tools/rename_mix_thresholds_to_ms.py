"""Rename threshold variables in v2.mix (ms names). Does not change block logic."""
import pathlib
import re
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
MIX = ROOT / "Traseu stelian V11 - histerezis v2.mix"

RENAMES = {
    "pragCitiri00": "prag00Ms",
    "pragCitiriLateral": "pragLateralMs",
    "pragStabilCitiri": "pragStabilMs",
}

DEFAULTS = {
    "prag00Ms": "8",
    "pragLateralMs": "0",
    "pragStabilMs": "80",
}


def main():
    s = MIX.read_text(encoding="utf-8").replace('\\"', '"')
    for old, new in RENAMES.items():
        s = s.replace(f'<field name="VAR">{old}</field>', f'<field name="VAR">{new}</field>')
    for name, val in DEFAULTS.items():
        s = re.sub(
            rf'(<field name="VAR">{name}</field><field name="TYPE">int</field><value name="VALUE"><block type="math_number" id="[^"]+"><field name="NUM">)\d+',
            rf"\g<1>{val}",
            s,
            count=1,
        )
    ET.fromstring(s)
    MIX.write_text(s.replace('"', '\\"'), encoding="utf-8")
    print("OK:", MIX.name)


if __name__ == "__main__":
    main()
