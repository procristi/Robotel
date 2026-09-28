# Replace read-count debounce in v2.mix with millisecond timers.
# The while loop, loop/lightActive indicator, speeds, and motor blocks stay in place.
import pathlib
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
PATH = ROOT / "Traseu stelian V11 - histerezis v2.mix"

_id = 9300000000000000


def nid():
    global _id
    _id += 1
    return f"id{_id}"


def outer_close(xml):
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
    acc = blocks[-1]
    for block in reversed(blocks[:-1]):
        cut = outer_close(block)
        if cut != block.rfind("</block>"):
            raise SystemExit("chain cut an inner block")
        acc = block[:cut] + "<next>" + acc + "</next>" + block[cut:]
    return acc


def num(n):
    return f'<block type="math_number" id="{nid()}"><field name="NUM">{n}</field></block>'


def var_get(name):
    return f'<block type="variables_get" id="{nid()}"><field name="VAR">{name}</field></block>'


def var_set_num(name, n):
    return (
        f'<block type="variables_set" id="{nid()}">'
        f'<field name="VAR">{name}</field><value name="VALUE">{num(n)}</value></block>'
    )


def var_set_var(name, src):
    return (
        f'<block type="variables_set" id="{nid()}">'
        f'<field name="VAR">{name}</field><value name="VALUE">{var_get(src)}</value></block>'
    )


def var_set_expr(name, expr):
    return (
        f'<block type="variables_set" id="{nid()}">'
        f'<field name="VAR">{name}</field><value name="VALUE">{expr}</value></block>'
    )


def compare(op, a, b):
    return (
        f'<block type="logic_compare" id="{nid()}">'
        f'<field name="OP">{op}</field>'
        f'<value name="A">{a}</value><value name="B">{b}</value></block>'
    )


def logic_and(a, b):
    return (
        f'<block type="logic_operation" id="{nid()}">'
        f'<field name="OP">AND</field>'
        f'<value name="A">{a}</value><value name="B">{b}</value></block>'
    )


def millis_block():
    return f'<block type="controls_millis" id="{nid()}"><field name="UNIT">millis</field></block>'


def millis_minus(var_name):
    return (
        f'<block type="math_arithmetic" id="{nid()}">'
        f'<field name="OP">MINUS</field>'
        f'<value name="A"><shadow type="math_number" id="{nid()}"><field name="NUM">1</field></shadow>'
        f"{millis_block()}</value>"
        f'<value name="B"><shadow type="math_number" id="{nid()}"><field name="NUM">1</field></shadow>'
        f"{var_get(var_name)}</value></block>"
    )


def controls_if(pairs, else_body=None):
    n = len(pairs)
    mut = ""
    if n > 1 or else_body:
        mut = "<mutation"
        if n > 1:
            mut += f' elseif="{n - 1}"'
        if else_body:
            mut += ' else="1"'
        mut += "></mutation>"
    parts = [f'<block type="controls_if" id="{nid()}">{mut}']
    for idx, (cond, body) in enumerate(pairs):
        parts.append(f'<value name="IF{idx}">{cond}</value>')
        parts.append(f'<statement name="DO{idx}">{body}</statement>')
    if else_body:
        parts.append(f'<statement name="ELSE">{else_body}</statement>')
    parts.append("</block>")
    return "".join(parts)


def sensors(left, right):
    return logic_and(
        compare("EQ", var_get("senzorStanga"), num(left)),
        compare("EQ", var_get("senzorDreapta"), num(right)),
    )


def mark_pattern_start(pattern_code, timer_var):
    return controls_if(
        [(compare("NEQ", var_get("patternPrev"), num(pattern_code)), var_set_expr(timer_var, millis_block()))]
    )


def elapsed(timer_var, prag_var):
    return compare("GTE", millis_minus(timer_var), var_get(prag_var))


def continue_turn(direction):
    return chain(
        [
            controls_if(
                [
                    (
                        compare("NEQ", var_get("ultimaDirectie"), num(direction)),
                        chain([var_set_expr("tStartViraj", millis_block()), var_set_num("esteCurba", 0)]),
                    )
                ]
            ),
            var_set_num("ultimaDirectie", direction),
            controls_if([(elapsed("tStartViraj", "pragCurba"), var_set_num("esteCurba", 1))]),
            var_set_num("stare", direction),
        ]
    )


def anti_osc(previous_code, new_code):
    detect = controls_if(
        [
            (
                compare("EQ", var_get("ultimLateral"), num(previous_code)),
                controls_if(
                    [
                        (
                            compare("LTE", millis_minus("tUltimLateral"), var_get("pragOscilareMs")),
                            var_set_num("linieInstabila", 1),
                        )
                    ]
                ),
            )
        ]
    )
    return controls_if(
        [
            (
                compare("EQ", var_get("antiOscilareActiv"), num(1)),
                chain(
                    [
                        detect,
                        var_set_num("ultimLateral", new_code),
                        var_set_expr("tUltimLateral", millis_block()),
                    ]
                ),
            )
        ]
    )


def straight_memory(direction):
    return chain(
        [
            controls_if(
                [
                    (
                        logic_and(
                            compare("EQ", var_get("linieInstabila"), num(0)),
                            elapsed("tStartLateral", "pragLateralMs"),
                        ),
                        var_set_num("ultimaDirectie", direction),
                    )
                ]
            ),
            var_set_num("stare", 0),
        ]
    )


def cancel(lockout):
    return chain(
        [
            var_set_num("stare", 0),
            var_set_num("ultimaDirectie", 0),
            var_set_num("esteCurba", 0),
            var_set_num("ignoraSenzor", lockout),
        ]
    )


def lateral_branch(pattern_code, flip_from, ultim_set, direction, lockout):
    stare_if = controls_if(
        [
            (compare("EQ", var_get("ignoraSenzor"), num(lockout)), var_set_num("stare", 0)),
            (
                logic_and(
                    compare("NEQ", var_get("stare"), num(0)),
                    compare("EQ", var_get("ultimaDirectie"), num(-direction)),
                ),
                cancel(lockout),
            ),
            (compare("EQ", var_get("stare"), num(0)), straight_memory(direction)),
        ],
        continue_turn(direction),
    )
    return chain(
        [
            mark_pattern_start(pattern_code, "tStartLateral"),
            anti_osc(flip_from, ultim_set),
            stare_if,
            var_set_num("patternPrev", pattern_code),
        ]
    )


def body_11():
    clear = controls_if(
        [
            (
                logic_and(
                    compare("EQ", var_get("antiOscilareActiv"), num(1)),
                    elapsed("tStartStabil11", "pragStabilMs"),
                ),
                var_set_num("linieInstabila", 0),
            )
        ]
    )
    return chain(
        [
            mark_pattern_start(3, "tStartStabil11"),
            clear,
            var_set_num("ultimLateral", 0),
            var_set_num("stare", 0),
            var_set_num("ultimaDirectie", 0),
            var_set_num("esteCurba", 0),
            var_set_num("ignoraSenzor", 0),
            var_set_num("patternPrev", 3),
        ]
    )


def enter_from_straight():
    return chain(
        [
            controls_if(
                [
                    (
                        compare("EQ", var_get("stare"), num(0)),
                        chain([var_set_expr("tStartViraj", millis_block()), var_set_num("esteCurba", 0)]),
                    )
                ]
            ),
            controls_if([(elapsed("tStartViraj", "pragCurba"), var_set_num("esteCurba", 1))]),
            var_set_var("stare", "ultimaDirectie"),
        ]
    )


def already_turning():
    return chain(
        [
            controls_if([(elapsed("tStartViraj", "pragCurba"), var_set_num("esteCurba", 1))]),
            var_set_var("stare", "ultimaDirectie"),
        ]
    )


def body_00():
    mid = controls_if(
        [
            (compare("NEQ", var_get("stare"), num(0)), already_turning()),
            (elapsed("tStart00", "prag00Ms"), enter_from_straight()),
        ],
        var_set_num("stare", 0),
    )
    outer = controls_if(
        [(compare("NEQ", var_get("ultimaDirectie"), num(0)), mid)],
        var_set_num("stare", 0),
    )
    unstable = controls_if(
        [(compare("EQ", var_get("linieInstabila"), num(1)), var_set_num("stare", 0))],
        outer,
    )
    return chain(
        [
            mark_pattern_start(0, "tStart00"),
            var_set_num("ignoraSenzor", 0),
            unstable,
            var_set_num("patternPrev", 0),
        ]
    )


def body_else():
    # 10 is pattern 2, flip if previous ultimLateral was 2 (01). 01 is pattern 1.
    return controls_if(
        [
            (sensors(1, 0), lateral_branch(2, 2, 1, -1, 1)),
            (sensors(0, 1), lateral_branch(1, 1, 2, 1, 2)),
        ],
        body_00(),
    )


def block_end(xml, at):
    return at + outer_close(xml[at:]) + len("</block>")


def direct_statements(xml, block_at):
    end = block_end(xml, block_at)
    i = xml.find(">", block_at) + 1
    depth = 1
    found = []
    while i < end:
        if xml.startswith("<block", i) or xml.startswith("<shadow", i):
            depth += 1
            i += 6
        elif xml.startswith("</block>", i) or xml.startswith("</shadow>", i):
            depth -= 1
            i += 8 if xml.startswith("</block>", i) else 9
        elif depth == 1 and xml.startswith("<statement ", i):
            name_at = xml.find('name="', i) + 6
            name = xml[name_at : xml.find('"', name_at)]
            open_end = xml.find(">", i) + 1
            j = open_end
            inner_depth = 1
            while j < end:
                if xml.startswith("<block", j) or xml.startswith("<shadow", j):
                    inner_depth += 1
                    j += 6
                elif xml.startswith("</block>", j) or xml.startswith("</shadow>", j):
                    inner_depth -= 1
                    j += 8 if xml.startswith("</block>", j) else 9
                elif inner_depth == 1 and xml.startswith("</statement>", j):
                    found.append((name, open_end, j))
                    i = j + len("</statement>")
                    break
                else:
                    j += 1
            else:
                raise SystemExit("statement not closed")
        else:
            i += 1
    return found


def replace_declare(xml, old_name, new_name, new_type, new_num):
    token = f'<field name="VAR">{old_name}</field>'
    at = xml.find(token)
    if at < 0:
        raise SystemExit(f"declare {old_name} missing")
    type_at = xml.find('<field name="TYPE">', at)
    type_end = xml.find("</field>", type_at)
    num_at = xml.find('<field name="NUM">', type_end)
    num_end = xml.find("</field>", num_at)
    return (
        xml[:at]
        + f'<field name="VAR">{new_name}</field>'
        + xml[at + len(token) : type_at]
        + f'<field name="TYPE">{new_type}</field>'
        + xml[type_end + len("</field>") : num_at]
        + f'<field name="NUM">{new_num}</field>'
        + xml[num_end + len("</field>") :]
    )


def main():
    raw = PATH.read_text(encoding="utf-8")
    xml = raw.replace('\\"', '"')
    marker = 'id="id9100000000000364"'
    id_at = xml.find(marker)
    if id_at < 0:
        raise SystemExit("sensor if missing")
    block_at = xml.rfind("<block", 0, id_at)
    stmts = direct_statements(xml, block_at)
    names = [name for name, _, _ in stmts]
    if names != ["DO0", "ELSE"]:
        raise SystemExit(f"unexpected statements: {names}")

    _, else_a, else_b = stmts[1]
    xml = xml[:else_a] + body_else() + xml[else_b:]
    stmts = direct_statements(xml, block_at)
    _, do_a, do_b = stmts[0]
    xml = xml[:do_a] + body_11() + xml[do_b:]

    xml = replace_declare(xml, "contor00", "patternPrev", "int", -1)
    xml = replace_declare(xml, "contorLateral", "tStart00", "long", 0)
    xml = replace_declare(xml, "patternLateral", "tStartLateral", "long", 0)
    xml = replace_declare(xml, "contorStabil11", "tStartStabil11", "long", 0)

    for gone in (
        "contor00",
        "contorLateral",
        "contorStabil11",
        "patternLateral",
        "pragCitiri00",
        "pragCitiriLateral",
        "pragStabilCitiri",
    ):
        if gone in xml:
            raise SystemExit(f"still present: {gone}")
    for need in (
        "patternPrev",
        "tStart00",
        "tStartLateral",
        "tStartStabil11",
        "prag00Ms",
        "pragLateralMs",
        "pragStabilMs",
        "loop",
        "lightActive",
    ):
        if need not in xml:
            raise SystemExit(f"missing {need}")
    if "vitezaMica" not in xml or ">200<" not in xml or ">247<" not in xml:
        raise SystemExit("user speeds were not kept")

    ET.fromstring(xml)
    PATH.write_text(xml.replace('"', '\\"'), encoding="utf-8")
    print("updated", PATH)


if __name__ == "__main__":
    main()
