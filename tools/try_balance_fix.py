import pathlib
import importlib.util
import xml.etree.ElementTree as ET

root = pathlib.Path(__file__).resolve().parents[1]
s = (root / "Traseu stelian V11 - histerezis.mix").read_text(encoding="utf-8").replace('\\"', '"')
start = s.find('<block type="controls_if" id="id0000000000000176">')
end = s.find('<block type="controls_if" id="id0000000000000267">')

spec = importlib.util.spec_from_file_location("gen", root / "tools" / "generate_histerezis_v2_mix.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

prefix = s[:start]
suffix = s[end:]

for n in range(0, 10):
    new = gen.follow_logic()
    for _ in range(n):
        i = new.rfind("</block>")
        if i >= 0:
            new = new[:i] + new[i + len("</block>") :]
    try:
        ET.fromstring(prefix + new + suffix)
        print("OK with removed", n, "closing blocks")
        break
    except ET.ParseError as e:
        print("n=", n, "fail", e)
else:
    print("no fix")
