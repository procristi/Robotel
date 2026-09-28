import pathlib

s = pathlib.Path(__file__).resolve().parents[1].joinpath("Traseu stelian V11 - histerezis v2.mix").read_text(encoding="utf-8").replace('\\"', '"')
m = s.find('mutation elseif="2" else="1"')
start = s.rfind('<block type="controls_if"', 0, m)
end = s.find('<block type="controls_if" id="id0000000000000267">', m)
if end < 0:
    # motor block id may differ
    end = s.find('motorStanga', m)
    end = s.rfind('<block type="controls_if"', m, end)
print("start", start, "end", end, "len", end - start if end > start else "n/a")
if start >= 0 and end > start:
    print("start snippet:", s[start : start + 120])
    print("end snippet:", s[end - 80 : end + 80])
