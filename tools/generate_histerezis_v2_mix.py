# Generates Traseu stelian V11 - histerezis v2.mix from v1 template + v2 logic blocks.
import pathlib
import re
import xml.sax.saxutils as saxutils

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "Traseu stelian V11 - histerezis.mix"
DST = ROOT / "Traseu stelian V11 - histerezis v2.mix"

_id = 9100000000000000


def nid():
    global _id
    _id += 1
    return f"id{_id}"


def num(n):
    i = nid()
    return (
        f'<block type="math_number" id="{i}"><field name="NUM">{n}</field></block>'
    )


def var_get(name):
    i = nid()
    return f'<block type="variables_get" id="{i}"><field name="VAR">{name}</field></block>'


def var_decl(name, typ, init_num):
    i = nid()
    return (
        f'<block type="variables_declare" id="{i}">'
        f'<field name="VAR">{name}</field><field name="TYPE">{typ}</field>'
        f'<value name="VALUE">{num(init_num)}</value>'
    )


def var_set(name, value_inner):
    i = nid()
    return (
        f'<block type="variables_set" id="{i}">'
        f'<field name="VAR">{name}</field>'
        f'<value name="VALUE">{value_inner}</value>'
    )


def block_end(xml):
    """End index (exclusive) of the first block, including its closing tag."""
    return outer_close(xml) + len("</block>")


def outer_close(xml):
    """Index of the closing tag of the first block in xml."""
    depth = 0
    i = 0
    while i < len(xml):
        if xml.startswith("<block", i) or xml.startswith("<shadow", i):
            depth += 1
            i += 6
        elif xml.startswith("</block>", i) or xml.startswith("</shadow>", i):
            depth -= 1
            if depth == 0:
                return i
            i += 8 if xml.startswith("</block>", i) else 9
        else:
            i += 1
    raise ValueError("unclosed block")


def chain(blocks):
    """Nest statement blocks: each following block sits in <next> inside the previous one."""
    if not blocks:
        return ""
    acc = blocks[-1]
    for block in reversed(blocks[:-1]):
        cut = outer_close(block)
        last = block.rfind("</block>")
        if cut != last:
            raise SystemExit(
                "chain cut an inner block:\n"
                + block[:120]
                + "\n--- at cut ---\n"
                + block[max(0, cut - 40) : cut + 30]
            )
        acc = block[:cut] + "<next>" + acc + "</next>" + block[cut:]
    return acc


def compare(op, a_inner, b_inner):
    i = nid()
    return (
        f'<block type="logic_compare" id="{i}">'
        f'<field name="OP">{op}</field>'
        f'<value name="A">{a_inner}</value>'
        f'<value name="B">{b_inner}</value></block>'
    )


def logic_and(a, b):
    i = nid()
    return (
        f'<block type="logic_operation" id="{i}">'
        f'<field name="OP">AND</field>'
        f'<value name="A">{a}</value>'
        f'<value name="B">{b}</value></block>'
    )


def logic_or(a, b):
    i = nid()
    return (
        f'<block type="logic_operation" id="{i}">'
        f'<field name="OP">OR</field>'
        f'<value name="A">{a}</value>'
        f'<value name="B">{b}</value></block>'
    )


def millis_block():
    i = nid()
    return f'<block type="controls_millis" id="{i}"><field name="UNIT">millis</field></block>'


def millis_minus(var_name):
    i = nid()
    return (
        f'<block type="math_arithmetic" id="{i}">'
        f'<field name="OP">MINUS</field>'
        f'<value name="A"><shadow type="math_number" id="{nid()}"><field name="NUM">1</field></shadow>'
        f"{millis_block()}</value>"
        f'<value name="B"><shadow type="math_number" id="{nid()}"><field name="NUM">1</field></shadow>'
        f"{var_get(var_name)}</value></block>"
    )


def add(a, b):
    i = nid()
    return (
        f'<block type="math_arithmetic" id="{i}">'
        f'<field name="OP">ADD</field>'
        f'<value name="A"><shadow type="math_number" id="{nid()}"><field name="NUM">1</field></shadow>{a}</value>'
        f'<value name="B"><shadow type="math_number" id="{nid()}"><field name="NUM">1</field></shadow>{b}</value></block>'
    )


def controls_if0(condition, do_body, else_body=None):
    i = nid()
    mut = '<mutation else="1"></mutation>' if else_body else ""
    else_xml = f'<statement name="ELSE">{else_body}</statement>' if else_body else ""
    return (
        f'<block type="controls_if" id="{i}">{mut}'
        f'<value name="IF0">{condition}</value>'
        f'<statement name="DO0">{do_body}</statement>{else_xml}</block>'
    )


def controls_if_elseif_else(if_pairs, else_body=None):
    """if_pairs: [(cond, body), ...]"""
    i = nid()
    n = len(if_pairs)
    mut = f'<mutation elseif="{n - 1}"'
    if else_body:
        mut += ' else="1"'
    mut += "></mutation>"
    parts = [f'<block type="controls_if" id="{i}">{mut}']
    for idx, (cond, body) in enumerate(if_pairs):
        key = "IF0" if idx == 0 else f"IF{idx}"
        dkey = f"DO{idx}"
        parts.append(f'<value name="{key}">{cond}</value>')
        parts.append(f'<statement name="{dkey}">{body}</statement>')
    if else_body:
        parts.append(f'<statement name="ELSE">{else_body}</statement>')
    parts.append("</block>")
    return "".join(parts)


def stmt_chain(statements):
    return chain([var_set(*s) if isinstance(s, tuple) and s[0] == "set" else s for s in statements])


def set_num(var, n):
    i = nid()
    return (
        f'<block type="variables_set" id="{i}"><field name="VAR">{var}</field>'
        f'<value name="VALUE">{num(n)}</value></block>'
    )


def set_var(var, src):
    i = nid()
    return (
        f'<block type="variables_set" id="{i}"><field name="VAR">{var}</field>'
        f'<value name="VALUE">{var_get(src)}</value></block>'
    )


def set_expr(var, expr):
    i = nid()
    return (
        f'<block type="variables_set" id="{i}"><field name="VAR">{var}</field>'
        f'<value name="VALUE">{expr}</value></block>'
    )


def inc(var):
    return set_expr(var, add(var_get(var), num(1)))


def sensors_11():
    return logic_and(
        compare("EQ", var_get("senzorStanga"), num(1)),
        compare("EQ", var_get("senzorDreapta"), num(1)),
    )


def sensors_10():
    return logic_and(
        compare("EQ", var_get("senzorStanga"), num(1)),
        compare("EQ", var_get("senzorDreapta"), num(0)),
    )


def sensors_01():
    return logic_and(
        compare("EQ", var_get("senzorStanga"), num(0)),
        compare("EQ", var_get("senzorDreapta"), num(1)),
    )


def body_11():
    return chain(
        [
            controls_if0(
                compare("NEQ", var_get("patternPrev"), num(3)),
                set_expr("tStartStabil11", millis_block()),
            ),
            controls_if0(
                logic_and(
                    compare("EQ", var_get("antiOscilareActiv"), num(1)),
                    compare("GTE", millis_minus("tStartStabil11"), var_get("pragStabilMs")),
                ),
                set_num("linieInstabila", 0),
            ),
            set_num("ultimLateral", 0),
            set_num("stare", 0),
            set_num("ultimaDirectie", 0),
            set_num("esteCurba", 0),
            set_num("ignoraSenzor", 0),
            set_num("patternPrev", 3),
        ]
    )


def anti_osc_flip(expected_ultim, new_ultim):
    """If antiOscilare on and flip within pragOscilareMs, linieInstabila=1."""
    detect = controls_if0(
        compare("EQ", var_get("ultimLateral"), num(expected_ultim)),
        controls_if0(
            compare("LTE", millis_minus("tUltimLateral"), var_get("pragOscilareMs")),
            set_num("linieInstabila", 1),
        ),
    )
    track = chain(
        [
            detect,
            set_num("ultimLateral", new_ultim),
            set_expr("tUltimLateral", millis_block()),
        ]
    )
    return controls_if0(compare("EQ", var_get("antiOscilareActiv"), num(1)), track)


def lateral_timer_start(pattern_code):
    return controls_if0(
        compare("NEQ", var_get("patternPrev"), num(pattern_code)),
        set_expr("tStartLateral", millis_block()),
    )


def mem_ultima_when_straight(value):
    return controls_if0(
        logic_and(
            compare("EQ", var_get("linieInstabila"), num(0)),
            compare("GTE", millis_minus("tStartLateral"), var_get("pragLateralMs")),
        ),
        set_num("ultimaDirectie", value),
    )


def branch_10_continue_turn():
    return chain(
        [
            controls_if0(
                compare("NEQ", var_get("ultimaDirectie"), num(-1)),
                chain([set_expr("tStartViraj", millis_block()), set_num("esteCurba", 0)]),
            ),
            set_num("ultimaDirectie", -1),
            controls_if0(
                compare("GTE", millis_minus("tStartViraj"), var_get("pragCurba")),
                set_num("esteCurba", 1),
            ),
            set_num("stare", -1),
        ]
    )


def branch_10():
    cancel = chain(
        [
            set_num("stare", 0),
            set_num("ultimaDirectie", 0),
            set_num("esteCurba", 0),
            set_num("ignoraSenzor", 1),
        ]
    )
    straight_mem = chain([mem_ultima_when_straight(-1), set_num("stare", 0)])
    inner = controls_if_elseif_else(
        [
            (compare("EQ", var_get("ignoraSenzor"), num(1)), set_num("stare", 0)),
            (
                logic_and(
                    compare("NEQ", var_get("stare"), num(0)),
                    compare("EQ", var_get("ultimaDirectie"), num(1)),
                ),
                cancel,
            ),
            (compare("EQ", var_get("stare"), num(0)), straight_mem),
        ],
        branch_10_continue_turn(),
    )
    return chain(
        [
            lateral_timer_start(2),
            anti_osc_flip(2, 1),
            inner,
            set_num("patternPrev", 2),
        ]
    )


def branch_01_continue_turn():
    return chain(
        [
            controls_if0(
                compare("NEQ", var_get("ultimaDirectie"), num(1)),
                chain([set_expr("tStartViraj", millis_block()), set_num("esteCurba", 0)]),
            ),
            set_num("ultimaDirectie", 1),
            controls_if0(
                compare("GTE", millis_minus("tStartViraj"), var_get("pragCurba")),
                set_num("esteCurba", 1),
            ),
            set_num("stare", 1),
        ]
    )


def branch_01():
    cancel = chain(
        [
            set_num("stare", 0),
            set_num("ultimaDirectie", 0),
            set_num("esteCurba", 0),
            set_num("ignoraSenzor", 2),
        ]
    )
    straight_mem = chain([mem_ultima_when_straight(1), set_num("stare", 0)])
    inner = controls_if_elseif_else(
        [
            (compare("EQ", var_get("ignoraSenzor"), num(2)), set_num("stare", 0)),
            (
                logic_and(
                    compare("NEQ", var_get("stare"), num(0)),
                    compare("EQ", var_get("ultimaDirectie"), num(-1)),
                ),
                cancel,
            ),
            (compare("EQ", var_get("stare"), num(0)), straight_mem),
        ],
        branch_01_continue_turn(),
    )
    return chain(
        [
            lateral_timer_start(1),
            anti_osc_flip(1, 2),
            inner,
            set_num("patternPrev", 1),
        ]
    )


def body_00_enter_turn():
    already = chain(
        [
            controls_if0(
                compare("GTE", millis_minus("tStartViraj"), var_get("pragCurba")),
                set_num("esteCurba", 1),
            ),
            set_var("stare", "ultimaDirectie"),
        ]
    )
    debounced = chain(
        [
            controls_if0(
                compare("EQ", var_get("stare"), num(0)),
                chain([set_expr("tStartViraj", millis_block()), set_num("esteCurba", 0)]),
            ),
            controls_if0(
                compare("GTE", millis_minus("tStartViraj"), var_get("pragCurba")),
                set_num("esteCurba", 1),
            ),
            set_var("stare", "ultimaDirectie"),
        ]
    )
    wait = set_num("stare", 0)
    mid = controls_if_elseif_else(
        [
            (compare("NEQ", var_get("stare"), num(0)), already),
            (compare("GTE", millis_minus("tStart00"), var_get("prag00Ms")), debounced),
        ],
        wait,
    )
    outer = controls_if0(
        compare("NEQ", var_get("ultimaDirectie"), num(0)),
        mid,
        set_num("stare", 0),
    )
    return chain(
        [
            controls_if0(
                compare("NEQ", var_get("patternPrev"), num(0)),
                set_expr("tStart00", millis_block()),
            ),
            set_num("ignoraSenzor", 0),
            controls_if0(compare("EQ", var_get("linieInstabila"), num(1)), set_num("stare", 0), outer),
            set_num("patternPrev", 0),
        ]
    )


def follow_logic(tail=None):
    not_11 = controls_if_elseif_else(
        [(sensors_10(), branch_10()), (sensors_01(), branch_01())],
        body_00_enter_turn(),
    )
    main = controls_if0(sensors_11(), body_11(), not_11)
    force = controls_if0(
        logic_and(compare("EQ", var_get("linieInstabila"), num(1)), compare("NEQ", var_get("stare"), num(0))),
        chain([set_num("stare", 0), set_num("esteCurba", 0)]),
    )
    parts = [main, force, motor_mapping()]
    if tail:
        parts.append(tail)
    return chain(parts)


def motor_mapping():
    left_soft = set_expr("motorStanga", add(var_get("vitezaMica"), var_get("compensareVitMica")))
    right_soft_l = set_expr("motorStanga", add(var_get("vitezaMare"), var_get("compensareVitMare")))
    straight = chain(
        [
            set_expr("motorStanga", add(var_get("vitezaMare"), var_get("compensareDrept"))),
            set_var("motorDreapta", "vitezaMare"),
        ]
    )
    left_turn = controls_if0(
        compare("EQ", var_get("esteCurba"), num(1)),
        chain([set_num("motorStanga", 0), set_var("motorDreapta", "vitezaMare")]),
        chain([left_soft, set_var("motorDreapta", "vitezaMare")]),
    )
    right_turn = controls_if0(
        compare("EQ", var_get("esteCurba"), num(1)),
        chain([right_soft_l, set_num("motorDreapta", 0)]),
        chain([right_soft_l, set_var("motorDreapta", "vitezaMica")]),
    )
    return controls_if_elseif_else(
        [
            (compare("EQ", var_get("stare"), num(0)), straight),
            (compare("EQ", var_get("stare"), num(-1)), left_turn),
        ],
        right_turn,
    )


def serial_motors():
    cond = logic_or(
        compare("NEQ", var_get("stare"), var_get("stareMotor")),
        compare("NEQ", var_get("esteCurba"), var_get("curbaTrimisa")),
    )
    # Reuse pattern from v1 - simplified serial chain
    writes = chain(
        [
            set_var("stareMotor", "stare"),
            set_var("curbaTrimisa", "esteCurba"),
            f'<block type="serial_write" id="{nid()}"><field name="serial_select">Serial</field><value name="CONTENT">{var_get("CodMotor")}</value></block>',
            f'<block type="serial_write" id="{nid()}"><field name="serial_select">Serial</field><value name="CONTENT">{num(1)}</value></block>',
            f'<block type="serial_write" id="{nid()}"><field name="serial_select">Serial</field><value name="CONTENT">{var_get("codViteza")}</value></block>',
            f'<block type="serial_write" id="{nid()}"><field name="serial_select">Serial</field><value name="CONTENT">{var_get("motorStanga")}</value></block>',
            f'<block type="serial_write" id="{nid()}"><field name="serial_select">Serial</field><value name="CONTENT">{var_get("CodMotor")}</value></block>',
            f'<block type="serial_write" id="{nid()}"><field name="serial_select">Serial</field><value name="CONTENT">{num(2)}</value></block>',
            f'<block type="serial_write" id="{nid()}"><field name="serial_select">Serial</field><value name="CONTENT">{var_get("codViteza")}</value></block>',
            f'<block type="serial_write" id="{nid()}"><field name="serial_select">Serial</field><value name="CONTENT">{var_get("motorDreapta")}</value></block>',
        ]
    )
    return controls_if0(cond, writes)


def patch_setup_declarations(xml: str) -> str:
    xml = xml.replace(
        '<field name="VAR">compensareStanga</field>',
        '<field name="VAR">compensareDrept</field>',
    )
    xml = re.sub(
        r'(<field name="VAR">compensareDrept</field><field name="TYPE">int</field><value name="VALUE"><block type="math_number" id="[^"]+"><field name="NUM">)\d+(</field></block></value>)',
        r"\g<1>0\2",
        xml,
        count=1,
    )
    xml = xml.replace('<field name="NUM">200</field>', '<field name="NUM">40</field>', 1)
    xml = xml.replace('<field name="NUM">220</field>', '<field name="NUM">240</field>', 1)

    decls = []
    for name, typ, val in [
        ("compensareVitMica", "int", 0),
        ("compensareVitMare", "int", 0),
        ("prag00Ms", "int", 8),
        ("antiOscilareActiv", "int", 1),
        ("pragOscilareMs", "int", 120),
        ("pragStabilMs", "int", 80),
        ("pragLateralMs", "int", 0),
        ("patternPrev", "int", -1),
        ("tStart00", "long", 0),
        ("tStartLateral", "long", 0),
        ("tStartStabil11", "long", 0),
        ("linieInstabila", "int", 0),
        ("ultimLateral", "int", 0),
        ("tUltimLateral", "long", 0),
    ]:
        decls.append(var_decl(name, typ, val) + "</block>")

    anchor = '<block type="variables_declare" id="id0000000000000017"><field name="VAR">pragCurba</field>'
    at = xml.find(anchor)
    if at < 0:
        raise SystemExit("pragCurba declare not found")
    end = at + block_end(xml[at:])
    prag = xml[at:end]
    inserted = chain(decls + [prag])
    xml = xml[:at] + inserted + xml[end:]

    xml = xml.replace(
        '<field name="VAR">butonPrev</field><field name="TYPE">int</field><value name="VALUE"><block type="math_number" id="id0000000000008002"><field name="NUM">-1</field>',
        '<field name="VAR">butonPrev</field><field name="TYPE">int</field><value name="VALUE"><block type="math_number" id="id0000000000008002"><field name="NUM">99</field>',
        1,
    )
    xml = xml.replace(
        'id="id0000000000008016"><field name="NUM">-1</field>',
        'id="id0000000000008016"><field name="NUM">99</field>',
        1,
    )
    return xml


def replace_follow_section(xml: str) -> str:
    start = '<block type="controls_if" id="id0000000000000176">'
    end_marker = '<block type="controls_if" id="id0000000000000267">'
    i0 = xml.find(start)
    i1 = xml.find(end_marker)
    if i0 < 0 or i1 < 0:
        raise SystemExit(f"markers not found: {i0}, {i1}")
    serial_end = i1 + block_end(xml[i1:])
    serial = xml[i1:serial_end]
    if outer_close(serial) + len("</block>") != len(serial):
        raise SystemExit("serial block close is not the end of the slice")
    follow_end = i0 + block_end(xml[i0:])
    new_follow = follow_logic(serial)
    return xml[:i0] + new_follow + xml[follow_end:]


def main():
    raw = SRC.read_text(encoding="utf-8")
    xml = raw.replace('\\"', '"')
    xml = patch_setup_declarations(xml)
    xml = replace_follow_section(xml)
    out = xml.replace('"', '\\"')
    DST.write_text(out, encoding="utf-8")
    print(f"Wrote {DST}")


if __name__ == "__main__":
    main()
