"""Build v2.mix by patching v1 (keeps valid Mixly XML structure)."""
import pathlib
import re
import importlib.util
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "Traseu stelian V11 - histerezis.mix"
DST = ROOT / "Traseu stelian V11 - histerezis v2.mix"


def load_gen():
    spec = importlib.util.spec_from_file_location("gen", ROOT / "tools" / "generate_histerezis_v2_mix.py")
    gen = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gen)
    return gen


def load_xml() -> str:
    return SRC.read_text(encoding="utf-8").replace('\\"', '"')


def patch_declarations(xml: str, gen) -> str:
    xml = xml.replace(
        '<field name="VAR">compensareStanga</field>',
        '<field name="VAR">compensareDrept</field>',
    )
    xml = xml.replace(
        '<value name="VALUE"><block type="math_number" id="id0000000000000012"><field name="NUM">200</field>',
        '<value name="VALUE"><block type="math_number" id="id0000000000000012"><field name="NUM">40</field>',
        1,
    )
    xml = xml.replace(
        '<value name="VALUE"><block type="math_number" id="id0000000000000014"><field name="NUM">220</field>',
        '<value name="VALUE"><block type="math_number" id="id0000000000000014"><field name="NUM">240</field>',
        1,
    )
    xml = re.sub(
        r'(<field name="VAR">compensareDrept</field><field name="TYPE">int</field><value name="VALUE"><block type="math_number" id="id0000000000000016"><field name="NUM">)\d+',
        r"\g<1>0",
        xml,
        count=1,
    )
    def mix_decl(name, typ, init):
        return (
            f'<block type="variables_declare" id="{gen.nid()}">'
            f'<field name="VAR">{name}</field><field name="TYPE">{typ}</field>'
            f'<value name="VALUE">{gen.num(init)}</value>'
        )

    decls = [
        mix_decl("compensareVitMica", "int", 0),
        mix_decl("compensareVitMare", "int", 0),
        mix_decl("pragCitiri00", "int", 3),
        mix_decl("antiOscilareActiv", "int", 1),
        mix_decl("pragOscilareMs", "int", 120),
        mix_decl("pragStabilCitiri", "int", 4),
        mix_decl("pragCitiriLateral", "int", 1),
        mix_decl("contor00", "int", 0),
        mix_decl("contorLateral", "int", 0),
        mix_decl("patternLateral", "int", 0),
        mix_decl("linieInstabila", "int", 0),
        mix_decl("contorStabil11", "int", 0),
        mix_decl("ultimLateral", "int", 0),
        mix_decl("tUltimLateral", "long", 0),
    ]
    extra = decls[0]
    for d in decls[1:]:
        extra += f"<next>{d}"
    anchor = '<next><block type="variables_declare" id="id0000000000000017"><field name="VAR">pragCurba</field>'
    return xml.replace(anchor, f"<next>{extra}{anchor[len('<next>'):]}", 1)


def patch_motor_block(xml: str) -> str:
    xml = xml.replace(
        '<field name="VAR">compensareStanga</field>',
        '<field name="VAR">compensareDrept</field>',
    )
    xml = xml.replace(
        '<block type="variables_set" id="id0000000000000197"><field name="VAR">motorStanga</field>'
        '<value name="VALUE"><block type="variables_get" id="id0000000000000196"><field name="VAR">vitezaMica</field></block></value></block>',
        '<block type="variables_set" id="id0000000000000197"><field name="VAR">motorStanga</field>'
        '<value name="VALUE"><block type="math_arithmetic" id="id9100000000000196">'
        '<field name="OP">ADD</field>'
        '<value name="A"><shadow type="math_number" id="id9100000000000196a"><field name="NUM">1</field></shadow>'
        '<block type="variables_get" id="id0000000000000196"><field name="VAR">vitezaMica</field></block></value>'
        '<value name="B"><shadow type="math_number" id="id9100000000000196b"><field name="NUM">1</field></shadow>'
        '<block type="variables_get" id="id9100000000000196c"><field name="VAR">compensareVitMica</field></block></value>'
        "</block></value></block>",
        1,
    )
    xml = xml.replace(
        '<block type="variables_set" id="id0000000000000207"><field name="VAR">motorDreapta</field>'
        '<value name="VALUE"><block type="math_arithmetic" id="id0000000000000204">'
        '<field name="OP">ADD</field>'
        '<value name="A"><shadow type="math_number" id="id0000000000000205"><field name="NUM">1</field></shadow>'
        '<block type="variables_get" id="id0000000000000202"><field name="VAR">vitezaMare</field></block></value>'
        '<value name="B"><shadow type="math_number" id="id0000000000000206"><field name="NUM">1</field></shadow>'
        '<block type="math_number" id="id0000000000000203"><field name="NUM">10</field></block></value>'
        "</block></value></block>",
        '<block type="variables_set" id="id0000000000000207"><field name="VAR">motorDreapta</field>'
        '<value name="VALUE"><block type="variables_get" id="id0000000000000202"><field name="VAR">vitezaMare</field></block></value></block>',
        1,
    )
    xml = xml.replace(
        '<block type="math_arithmetic" id="id0000000000000220"><field name="OP">ADD</field>'
        '<value name="A"><shadow type="math_number" id="id0000000000000221"><field name="NUM">1</field></shadow>'
        '<block type="math_arithmetic" id="id0000000000000216"><field name="OP">ADD</field>'
        '<value name="A"><shadow type="math_number" id="id0000000000000217"><field name="NUM">1</field></shadow>'
        '<block type="variables_get" id="id0000000000000214"><field name="VAR">vitezaMare</field></block></value>'
        '<value name="B"><shadow type="math_number" id="id0000000000000218"><field name="NUM">1</field></shadow>'
        '<block type="variables_get" id="id0000000000000215"><field name="VAR">compensareDrept</field></block></value></block></value>'
        '<value name="B"><shadow type="math_number" id="id0000000000000222"><field name="NUM">1</field></shadow>'
        '<block type="math_number" id="id0000000000000219"><field name="NUM">15</field></block></value></block>',
        '<block type="math_arithmetic" id="id0000000000000220"><field name="OP">ADD</field>'
        '<value name="A"><shadow type="math_number" id="id0000000000000221"><field name="NUM">1</field></shadow>'
        '<block type="variables_get" id="id0000000000000214"><field name="VAR">vitezaMare</field></block></value>'
        '<value name="B"><shadow type="math_number" id="id0000000000000222"><field name="NUM">1</field></shadow>'
        '<block type="variables_get" id="id0000000000000215"><field name="VAR">compensareVitMare</field></block></value></block>',
        1,
    )
    xml = xml.replace(
        '<block type="variables_get" id="id0000000000000225"><field name="VAR">compensareDrept</field></block>',
        '<block type="variables_get" id="id0000000000000225"><field name="VAR">compensareVitMare</field></block>',
        1,
    )
    return xml


def replace_do_statement(xml: str, if_marker: str, do_name: str, new_body: str) -> str:
    i = xml.find(if_marker)
    if i < 0:
        raise SystemExit(f"marker missing: {if_marker[:60]}")
    s = xml.find(f'<statement name="{do_name}">', i)
    if s < 0:
        raise SystemExit(f"{do_name} missing after marker")
    pos = s + len(f'<statement name="{do_name}">')
    depth = 0
    end = -1
    while pos < len(xml):
        if xml.startswith("<statement", pos):
            depth += 1
            pos += 1
            continue
        if xml.startswith("</statement>", pos):
            if depth == 0:
                end = pos
                break
            depth -= 1
            pos += len("</statement>")
            continue
        pos += 1
    if end < 0:
        raise SystemExit(f"end of {do_name} not found")
    return xml[:s] + f'<statement name="{do_name}">{new_body}' + xml[end:]


def patch_sensor_logic(xml: str, gen) -> str:
    # 11 branch DO0
    body11 = gen.chain(
        [
            gen.set_num("contor00", 0),
            gen.inc("contorStabil11"),
            gen.controls_if0(
                gen.logic_and(
                    gen.compare("EQ", gen.var_get("antiOscilareActiv"), gen.num(1)),
                    gen.compare("GTE", gen.var_get("contorStabil11"), gen.var_get("pragStabilCitiri")),
                ),
                gen.set_num("linieInstabila", 0),
            ),
            gen.set_num("ultimLateral", 0),
            gen.set_num("contorLateral", 0),
            gen.set_num("patternLateral", 0),
            gen.set_num("stare", 0),
            gen.set_num("ultimaDirectie", 0),
            gen.set_num("esteCurba", 0),
            gen.set_num("ignoraSenzor", 0),
        ]
    )
    xml = replace_do_statement(
        xml,
        '<value name="IF0"><block type="logic_operation" id="id0000000000000161">',
        "DO0",
        body11,
    )

    xml = replace_do_statement(
        xml,
        '<value name="IF1"><block type="logic_operation" id="id0000000000000168">',
        "DO1",
        gen.branch_10(),
    )

    xml = replace_do_statement(
        xml,
        '<value name="IF2"><block type="logic_operation" id="id0000000000000175">',
        "DO2",
        gen.branch_01(),
    )

    # 00 else branch on sensor ifelse 0176
    else_marker = '<statement name="ELSE"><block type="variables_set" id="id0000000000000146">'
    i = xml.find(else_marker)
    if i < 0:
        raise SystemExit("00 else marker missing")
    j = xml.find("</statement>", i)
    # else branch includes nested blocks; find matching close for ELSE of 0176 only
    depth = 0
    pos = i + len('<statement name="ELSE">')
    while pos < len(xml):
        if xml.startswith("<statement", pos):
            depth += 1
            pos += 1
            continue
        if xml.startswith("</statement>", pos):
            if depth == 0:
                j = pos
                break
            depth -= 1
            pos += len("</statement>")
            continue
        pos += 1
    new_else = f'<statement name="ELSE">{gen.body_00_enter_turn()}'
    xml = xml[:i] + new_else + xml[j:]

    # Force straight when unstable (before motor block)
    force = gen.controls_if0(
        gen.logic_and(
            gen.compare("EQ", gen.var_get("linieInstabila"), gen.num(1)),
            gen.compare("NEQ", gen.var_get("stare"), gen.num(0)),
        ),
        gen.chain([gen.set_num("stare", 0), gen.set_num("esteCurba", 0)]),
    )
    motor = '<next><block type="controls_if" id="id0000000000000239">'
    xml = xml.replace(motor, "<next>" + force + motor, 1)
    return xml


def main():
    gen = load_gen()
    xml = load_xml()
    xml = patch_declarations(xml, gen)
    xml = patch_sensor_logic(xml, gen)
    xml = patch_motor_block(xml)
    ET.fromstring(xml)
    DST.write_text(xml.replace('"', '\\"'), encoding="utf-8")
    print("Wrote", DST)


if __name__ == "__main__":
    main()
