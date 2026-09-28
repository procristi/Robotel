import pathlib

s = pathlib.Path(__file__).resolve().parents[1].joinpath("Traseu stelian V11 - histerezis.mix").read_text(encoding="utf-8").replace('\\"', '"')
start = s.find('<block type="controls_if" id="id0000000000000176">')
print(s[start - 600 : start])
