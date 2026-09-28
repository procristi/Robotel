import pathlib
import xml.etree.ElementTree as ET
import importlib.util

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("b", ROOT / "tools" / "build_v2_mix_composed.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
gen = b.load_gen()
xml = b.load_xml()

steps = [
    ("decl", lambda x: b.patch_declarations(x, gen)),
    ("motor", b.patch_motor_block),
    ("sensor", lambda x: b.patch_sensor_logic(x, gen)),
]

cur = xml
for name, fn in steps:
    cur = fn(cur)
    try:
        ET.fromstring(cur)
        print(name, "OK")
    except ET.ParseError as e:
        print(name, "FAIL", e)
        break
