import pathlib

root = pathlib.Path(__file__).resolve().parents[1]
s = (root / "Traseu stelian V11 - histerezis.mix").read_text(encoding="utf-8").replace('\\"', '"')
start = s.find('<block type="controls_if" id="id0000000000000176">')
end = s.find('<block type="controls_if" id="id0000000000000267">')
chunk = s[start:end]
print("chunk len", len(chunk))
print("open block", chunk.count("<block"))
print("close block", chunk.count("</block>"))
print("open stmt", chunk.count("<statement"))
print("close stmt", chunk.count("</statement>"))
print("open next", chunk.count("<next>"))
print("close next", chunk.count("</next>"))
