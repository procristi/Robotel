"""Rename threshold vars in v2.mix and swap declare defaults. Logic must match v2.cpp (update in Mixly or re-export)."""
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

# Old counter/state vars -> ms timers (declares only; remove counter declares manually in Mixly if duplicated)
REMOVE_DECLARE = {
    "contor00",
    "contorLateral",
    "contorStabil11",
    "patternLateral",
}

ADD_DECLARES = [
    ("patternPrev", "int", -1),
    ("tStart00", "long", 0),
    ("tStartLateral", "long", 0),
    ("tStartStabil11", "long", 0),
]

DEFAULTS_AFTER_RENAME = {
    "prag00Ms": "8",
    "pragLateralMs": "0",
    "pragStabilMs": "80",
}


def mix_decl(name, typ, init):
    return (
        f'<block type="variables_declare" id="ms{nid()}">'
        f'<field name="VAR">{name}</field><field name="TYPE">{typ}</field>'
        f'<value name="VALUE"><block type="math_number" id="ms{nid()}">'
        f'<field name="NUM">{init}</field></block></value>'
    )


_id = 9200000000000000


def nid():
    global _id
    _id += 1
    return str(_id)


def main():
    raw = MIX.read_text(encoding="utf-8")
    s = raw.replace('\\"', '"')

    for old, new in RENAMES.items():
        s = s.replace(f'<field name="VAR">{old}</field>', f'<field name="VAR">{new}</field>')

    for name, val in DEFAULTS_AFTER_RENAME.items():
        s = re.sub(
            rf'(<field name="VAR">{name}</field><field name="TYPE">int</field><value name="VALUE"><block type="math_number" id="[^"]+"><field name="NUM">)\d+',
            rf"\g<1>{val}",
            s,
            count=1,
        )

    # Insert new declares before pragCurba if missing
    if "tStart00" not in s:
        decls = [mix_decl(n, t, v) for n, t, v in ADD_DECLARES]
        extra = decls[0]
        for d in decls[1:]:
            extra += f"<next>{d}"
        anchor = '<next><block type="variables_declare" id="id0000000000000017"><field name="VAR">pragCurba</field>'
        if anchor in s:
            s = s.replace(anchor, f"<next>{extra}{anchor[len('<next>'):]}", 1)

    ET.fromstring(s)
    MIX.write_text(s.replace('"', '\\"'), encoding="utf-8")
    print(f"Updated {MIX.name} (variable names + defaults).")
    print("IMPORTANT: Replace counter logic in Mixly with millis timers per v2.cpp:")
    print("  - patternPrev + tStart00 / tStartLateral / tStartStabil11")
    print("  - Or copy follow logic from Traseu stelian V11 - histerezis v2.cpp into blocks.")


if __name__ == "__main__":
    main()
