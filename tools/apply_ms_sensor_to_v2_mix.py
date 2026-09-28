"""Replace sensor/motor-prep logic in v2.mix with ms-based generator output."""
import pathlib
import re
import xml.etree.ElementTree as ET
import importlib.util

ROOT = pathlib.Path(__file__).resolve().parents[1]
MIX = ROOT / "Traseu stelian V11 - histerezis v2.mix"

RENAMES = {
    "pragCitiri00": "prag00Ms",
    "pragCitiriLateral": "pragLateralMs",
    "pragStabilCitiri": "pragStabilMs",
}


def load_gen():
    spec = importlib.util.spec_from_file_location("gen", ROOT / "tools" / "generate_histerezis_v2_mix.py")
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    return gen


def rename_threshold_vars(s: str) -> str:
    for old, new in RENAMES.items():
        s = s.replace(f'<field name="VAR">{old}</field>', f'<field name="VAR">{new}</field>')
    return s


def strip_old_counter_declares(s: str) -> str:
    for name in ("contor00", "contorLateral", "contorStabil11", "patternLateral"):
        s = re.sub(
            rf"<next><block type=\"variables_declare\" id=\"[^\"]+\"><field name=\"VAR\">{name}</field>.*?</value>",
            "",
            s,
            count=1,
            flags=re.DOTALL,
        )
    return s


def insert_ms_declares_if_missing(s: str, gen) -> str:
    if "tStart00" in s:
        return s

    def mix_decl(name, typ, init):
        return (
            f'<block type="variables_declare" id="{gen.nid()}">'
            f'<field name="VAR">{name}</field><field name="TYPE">{typ}</field>'
            f'<value name="VALUE">{gen.num(init)}</value>'
        )

    decls = [
        mix_decl("patternPrev", "int", -1),
        mix_decl("tStart00", "long", 0),
        mix_decl("tStartLateral", "long", 0),
        mix_decl("tStartStabil11", "long", 0),
    ]
    extra = decls[0]
    for d in decls[1:]:
        extra += f"<next>{d}"
    anchor = '<next><block type="variables_declare" id="id0000000000000017"><field name="VAR">pragCurba</field>'
    if anchor not in s:
        anchor = '<field name="VAR">pragCurba</field>'
        return s
    return s.replace(anchor, f"<next>{extra}{anchor[len('<next>'):]}", 1)


def replace_sensor_chain(s: str, gen) -> str:
    m = s.find('mutation elseif="2" else="1"')
    if m < 0:
        raise SystemExit("sensor ifelse block not found")
    start = s.rfind('<block type="controls_if"', 0, m)
    end = s.find('<block type="controls_if" id="id0000000000000267">', m)
    if start < 0 or end < 0:
        raise SystemExit(f"slice bounds start={start} end={end}")
    return s[:start] + gen.follow_logic() + s[end:]


def main():
    gen = load_gen()
    raw = MIX.read_text(encoding="utf-8")
    s = raw.replace('\\"', '"')
    s = rename_threshold_vars(s)
    s = insert_ms_declares_if_missing(s, gen)
    s = replace_sensor_chain(s, gen)
    ET.fromstring(s)
    MIX.write_text(s.replace('"', '\\"'), encoding="utf-8")
    print("OK:", MIX.name)


if __name__ == "__main__":
    main()
