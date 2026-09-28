import pathlib

xml = pathlib.Path(__file__).resolve().parents[1].joinpath("Traseu stelian V11 - histerezis.mix").read_text(encoding="utf-8").replace('\\"', '"')
i = xml.find('id="id0000000000000015"')
print(xml[i : i + 1200])
