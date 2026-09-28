import pathlib
import importlib.util

root = pathlib.Path(__file__).resolve().parents[1]
s = (root / "Traseu stelian V11 - histerezis.mix").read_text(encoding="utf-8").replace('\\"', '"')
end = s.find('<block type="controls_if" id="id0000000000000267">')
old_suffix = s[end - 120 : end]

spec = importlib.util.spec_from_file_location("gen", root / "tools" / "generate_histerezis_v2_mix.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)
new = gen.follow_logic()
new_suffix = new[-120:]

print("OLD suffix:")
print(old_suffix)
print("NEW suffix:")
print(new_suffix)
