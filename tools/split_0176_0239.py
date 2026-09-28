import pathlib
import importlib.util

root = pathlib.Path(__file__).resolve().parents[1]
s = (root / "Traseu stelian V11 - histerezis.mix").read_text(encoding="utf-8").replace('\\"', '"')
start = s.find('<block type="controls_if" id="id0000000000000176">')
mid = s.find('<next><block type="controls_if" id="id0000000000000239">')
end = s.find('<block type="controls_if" id="id0000000000000267">')
old_0176 = s[start:mid]
old_0239 = s[mid:end]

spec = importlib.util.spec_from_file_location("gen", root / "tools" / "generate_histerezis_v2_mix.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)
new_logic = gen.follow_logic()

print("0176 len", len(old_0176))
print("0176 end", old_0176[-80:])
print("0239 len", len(old_0239))
print("0239 end", old_0239[-80:])
print("new len", len(new_logic))
print("new end", new_logic[-80:])

# try compose: keep 0176 wrapper start - no, compose new sensor + old 0239 pattern
