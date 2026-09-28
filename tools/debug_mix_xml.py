import pathlib

p = pathlib.Path(__file__).resolve().parents[1] / "Traseu stelian V11 - histerezis v2.mix"
s = p.read_text(encoding="utf-8").replace('\\"', '"')
pos = 69685
print(s[pos - 200 : pos + 200])
