import pathlib
import xml.etree.ElementTree as ET

p = pathlib.Path(__file__).resolve().parents[1] / "Traseu stelian V11 - histerezis v2.mix"
s = p.read_text(encoding="utf-8").replace('\\"', '"')
ET.fromstring(s)
print("XML OK", len(s))
