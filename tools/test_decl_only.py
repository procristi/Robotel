import pathlib
import xml.etree.ElementTree as ET
import importlib.util

ROOT = pathlib.Path(__file__).resolve().parents[1]
xml = (ROOT / "Traseu stelian V11 - histerezis.mix").read_text(encoding="utf-8").replace('\\"', '"')
spec = importlib.util.spec_from_file_location("b", ROOT / "tools" / "build_v2_mix_composed.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
gen = b.load_gen()
try:
    ET.fromstring(b.patch_declarations(xml, gen))
    print("decl OK")
except ET.ParseError as e:
    print("decl fail", e)
