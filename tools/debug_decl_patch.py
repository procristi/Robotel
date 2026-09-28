import pathlib
import importlib.util

ROOT = pathlib.Path(__file__).resolve().parents[1]
xml = (ROOT / "Traseu stelian V11 - histerezis.mix").read_text(encoding="utf-8").replace('\\"', '"')
spec = importlib.util.spec_from_file_location("b", ROOT / "tools" / "build_v2_mix_composed.py")
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
out = b.patch_declarations(xml, b.load_gen())
i = out.find('compensareDrept')
print(out[i : i + 2500])
