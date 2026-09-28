import pathlib

s = pathlib.Path(__file__).resolve().parents[1].joinpath("Traseu stelian V11 - histerezis.mix").read_text(encoding="utf-8").replace('\\"', '"')
start = s.find('<block type="controls_if" id="id0000000000000176">')
end = s.find('<block type="controls_if" id="id0000000000000267">')
print("BEFORE 0176:")
print(s[start - 300 : start])
print("\nEND OF SLICE (before 0267):")
print(s[end - 400 : end])
print("\n0267 start:")
print(s[end : end + 120])
