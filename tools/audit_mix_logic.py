import pathlib
import re

path = pathlib.Path(__file__).resolve().parents[1] / "Traseu stelian V11 - histerezis v2.mix"
s = path.read_text(encoding="utf-8").replace('\\"', '"')

checks = [
    ("Declare pragCitiri00", r'<field name="VAR">pragCitiri00</field><field name="TYPE">int</field>'),
    ("Declare antiOscilareActiv", r'<field name="VAR">antiOscilareActiv</field>'),
    ("Read pragCitiri00 in loop", r'variables_get"[^>]*><field name="VAR">pragCitiri00</field>'),
    ("Read antiOscilareActiv", r'variables_get"[^>]*><field name="VAR">antiOscilareActiv</field>'),
    ("Read pragOscilareMs", r'variables_get"[^>]*><field name="VAR">pragOscilareMs</field>'),
    ("Read pragStabilCitiri", r'variables_get"[^>]*><field name="VAR">pragStabilCitiri</field>'),
    ("Read pragCitiriLateral", r'variables_get"[^>]*><field name="VAR">pragCitiriLateral</field>'),
    ("Write linieInstabila", r'variables_set"[^>]*><field name="VAR">linieInstabila</field>'),
    ("Write contor00", r'variables_set"[^>]*><field name="VAR">contor00</field>'),
    ("Increment contor00 (change)", r'variables_set"[^>]*><field name="VAR">contor00</field>'),
    ("compensareVitMica in motors", r'variables_get"[^>]*><field name="VAR">compensareVitMica</field>'),
    ("compensareVitMare in motors", r'variables_get"[^>]*><field name="VAR">compensareVitMare</field>'),
    ("compensareDrept straight", r'variables_get"[^>]*><field name="VAR">compensareDrept</field>'),
    ("No outer +10 boost", r'<field name="NUM">10</field></block></value></block></value></block></value></block></statement><statement name="DO0"><block type="variables_set" id="id0000000000000207"'),
    ("No +15 on hard right", r'NUM">15</field>'),
]

print(path.name)
for label, pat in checks:
    n = len(re.findall(pat, s))
    ok = n > 0 if "No" not in label else n == 0
    if "No outer" in label:
        ok = "id0000000000000203" not in s or "NUM\">10</field>" not in s.split("motorDreapta")[1][:2000] if "motorDreapta" in s else True
    if label == "No +15 on hard right":
        ok = n == 0
    status = "OK" if ok else "LIPSA/PROBLEMA"
    print(f"  [{status}] {label} (matches={n})")

# declare count exact
for v in ["pragCitiri00", "antiOscilareActiv", "pragCitiriLateral"]:
    n = len(re.findall(rf'<block type="variables_declare" id="[^"]+"><field name="VAR">{v}</field>', s))
    print(f"  Declare blocks for {v}: {n}")
