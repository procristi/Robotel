import pathlib
import importlib.util

ROOT = pathlib.Path(__file__).resolve().parents[1]
s = (ROOT / "Traseu stelian V11 - histerezis v2.mix").read_text(encoding="utf-8").replace('\\"', '"')
m = s.find('mutation elseif="2" else="1"')
start = s.rfind('<block type="controls_if"', 0, m)
end = s.find('<block type="controls_if" id="id0000000000000267">', m)
old = s[start:end]

spec = importlib.util.spec_from_file_location("gen", ROOT / "tools" / "generate_histerezis_v2_mix.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)
new = gen.follow_logic()

print("old", old.count("<block"), old.count("</block>"), "next", old.count("<next>"), old.count("</next>"))
print("new", new.count("<block"), new.count("</block>"), "next", new.count("<next>"), new.count("</next>"))
print("OLD suffix:", repr(s[end - 100 : end]))
print("NEW suffix:", repr(new[-100:]))
