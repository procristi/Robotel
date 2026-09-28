import pathlib

s = pathlib.Path(__file__).resolve().parents[1].joinpath("Traseu stelian V11 - histerezis v2.mix").read_text(encoding="utf-8").replace('\\"', '"')
start = s.find('<block type="controls_if" id="id9100000000000095">')
if start < 0:
    print("block not found")
    raise SystemExit(1)
# walk block depth from start
pos = start + len('<block type="controls_if"')
depth = 1
i = start + 1
while i < len(s) and depth > 0:
    if s.startswith("<block ", i):
        depth += 1
        i += 6
        continue
    if s.startswith("</block>", i):
        depth -= 1
        i += len("</block>")
        if depth == 0:
            end_block = i
            break
        continue
    i += 1
else:
    print("no end")
    raise SystemExit(1)

print("sensor only len", end_block - start)
print("after sensor:", repr(s[end_block : end_block + 150]))
