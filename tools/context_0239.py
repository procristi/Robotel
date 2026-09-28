import pathlib

s = pathlib.Path(__file__).resolve().parents[1].joinpath("Traseu stelian V11 - histerezis.mix").read_text(encoding="utf-8").replace('\\"', '"')
i = s.find('id="id0000000000000239"')
print(s[i - 200 : i + 100])
