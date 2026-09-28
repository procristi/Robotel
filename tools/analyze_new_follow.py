import pathlib
import importlib.util

spec = importlib.util.spec_from_file_location("gen", pathlib.Path(__file__).parent / "generate_histerezis_v2_mix.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)
chunk = gen.follow_logic()
print("chunk len", len(chunk))
print("open block", chunk.count("<block"))
print("close block", chunk.count("</block>"))
print("open stmt", chunk.count("<statement"))
print("close stmt", chunk.count("</statement>"))
print("open next", chunk.count("<next>"))
print("close next", chunk.count("</next>"))
