import pathlib
import re

VARS = [
    "pragCitiri00",
    "antiOscilareActiv",
    "pragOscilareMs",
    "pragStabilCitiri",
    "pragCitiriLateral",
    "linieInstabila",
    "contor00",
    "contorStabil11",
    "ultimLateral",
    "tUltimLateral",
    "contorLateral",
    "patternLateral",
    "compensareVitMica",
    "compensareVitMare",
    "compensareDrept",
    "compensareStanga",
]

ROOT = pathlib.Path(__file__).resolve().parents[1]


def audit(path: pathlib.Path) -> None:
    if not path.exists():
        print(f"{path.name}: MISSING")
        return
    raw = path.read_text(encoding="utf-8")
    s = raw.replace('\\"', '"')
    print(f"=== {path.name} ===")
    for v in VARS:
        if v not in s:
            print(f"  {v}: absent")
            continue
        declares = len(
            re.findall(
                rf'<block type="variables_declare"[^>]*>.*?<field name="VAR">{v}</field>',
                s,
            )
        )
        gets = len(re.findall(rf'<field name="VAR">{v}</field>', s)) - declares
        sets = len(
            re.findall(rf'<block type="variables_set"[^>]*>.*?<field name="VAR">{v}</field>', s)
        )
        # gets counted in sets too sometimes - refine
        gets_only = len(
            re.findall(
                rf'<block type="variables_get"[^>]*><field name="VAR">{v}</field>',
                s,
            )
        )
        sets_only = len(
            re.findall(
                rf'<block type="variables_set"[^>]*><field name="VAR">{v}</field>',
                s,
            )
        )
        print(
            f"  {v}: declare={declares}, get={gets_only}, set={sets_only}"
        )
    # motor speed patterns
    has_plus_10 = "NUM\">10</field>" in s and "vitezaMare" in s
    has_plus_15 = "NUM\">15</field>" in s
    print(f"  [motor] hard-turn +10 block: {'yes' if 'NUM\">10</field>' in s else 'no'}")
    print(f"  [motor] hard-turn +15 block: {'yes' if 'NUM\">15</field>' in s else 'no'}")
    print()


for name in [
    "Traseu stelian V11 - histerezis.mix",
    "Traseu stelian V11 - histerezis v2.mix",
]:
    audit(ROOT / name)
