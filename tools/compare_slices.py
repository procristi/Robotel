import pathlib
import importlib.util

root = pathlib.Path(__file__).resolve().parents[1]
s = (root / "Traseu stelian V11 - histerezis.mix").read_text(encoding="utf-8").replace('\\"', '"')
start = s.find('<block type="controls_if" id="id0000000000000176">')
end = s.find('<block type="controls_if" id="id0000000000000267">')
old = s[start:end]

spec = importlib.util.spec_from_file_location("gen", root / "tools" / "generate_histerezis_v2_mix.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)
new = gen.follow_logic()

def stats(label, chunk):
    print(label, "len", len(chunk))
    print("  block", chunk.count("<block"), chunk.count("</block>"))
    print("  statement", chunk.count("<statement"), chunk.count("</statement>"))
    print("  next", chunk.count("<next>"), chunk.count("</next>"))
    print("  value", chunk.count("<value"), chunk.count("</value>"))

stats("old", old)
stats("new", new)
