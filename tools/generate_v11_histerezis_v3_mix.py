# Mixly 0.997 file for the current V11HisterezisV3Sketch loop.
# ResetStare and Pas stay out: they exist only for the desktop simulator.
# The 00 turn list in the sketch is empty, so 00 uses parteMemorata.
import pathlib
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
DST = ROOT / "V11HisterezisV3Sketch_charp.mix"

_id = 0


def nid():
    global _id
    _id += 1
    return f"id{_id:016d}"


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
    blocks = [b for b in blocks if b]
    if not blocks:
        raise ValueError("empty chain")
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


def var_decl(name, typ, value):
    return (
        f'<block type="variables_declare" id="{nid()}">'
        f'<field name="VAR">{name}</field><field name="TYPE">{typ}</field>'
        f'<value name="VALUE">{num(value)}</value></block>'
    )


def var_set(name, value_xml):
    return (
        f'<block type="variables_set" id="{nid()}">'
        f'<field name="VAR">{name}</field>'
        f'<value name="VALUE">{value_xml}</value></block>'
    )


def pin_mode(pin, mode):
    return (
        f'<block type="inout_pinMode" id="{nid()}"><field name="MODE">{mode}</field>'
        f'<value name="PIN"><shadow type="pins_digital" id="{nid()}">'
        f'<field name="PIN">{pin}</field></shadow></value></block>'
    )


def digital_read(pin):
    return (
        f'<block type="inout_digital_read2" id="{nid()}">'
        f'<value name="PIN"><shadow type="pins_digital" id="{nid()}">'
        f'<field name="PIN">{pin}</field></shadow></value></block>'
    )


def digital_write(pin, level):
    return (
        f'<block type="inout_digital_write2" id="{nid()}">'
        f'<value name="PIN"><shadow type="pins_digital" id="{nid()}">'
        f'<field name="PIN">{pin}</field></shadow></value>'
        f'<value name="STAT"><shadow type="inout_highlow" id="{nid()}">'
        f'<field name="BOOL">{level}</field></shadow></value></block>'
    )


def serial_write(content):
    return (
        f'<block type="serial_write" id="{nid()}">'
        f'<field name="serial_select">Serial</field>'
        f'<value name="CONTENT">{content}</value></block>'
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


def logic_or(a, b):
    return (
        f'<block type="logic_operation" id="{nid()}">'
        f'<field name="OP">OR</field>'
        f'<value name="A">{a}</value><value name="B">{b}</value></block>'
    )


def millis_block():
    return f'<block type="controls_millis" id="{nid()}"><field name="UNIT">millis</field></block>'


def arith(op, a, b):
    return (
        f'<block type="math_arithmetic" id="{nid()}">'
        f'<field name="OP">{op}</field>'
        f'<value name="A"><shadow type="math_number" id="{nid()}"><field name="NUM">1</field></shadow>{a}</value>'
        f'<value name="B"><shadow type="math_number" id="{nid()}"><field name="NUM">1</field></shadow>{b}</value></block>'
    )


def millis_minus(var_name):
    return arith("MINUS", millis_block(), var_get(var_name))


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


def eq_num(var, n):
    return compare("EQ", var_get(var), num(n))


def neq_num(var, n):
    return compare("NEQ", var_get(var), num(n))


def set_num(var, n):
    return var_set(var, num(n))


def set_millis(var):
    return var_set(var, millis_block())


def led(sensor, pin):
    return controls_if(
        [(eq_num(sensor, 1), digital_write(pin, "HIGH"))],
        digital_write(pin, "LOW"),
    )


def elapsed_gte(timer, threshold):
    return compare("GTE", millis_minus(timer), var_get(threshold))


def mark_hard_curve():
    return controls_if([(elapsed_gte("momentInceputViraj", "pragCurba"), set_num("esteCurbaTare", 1))])


def viraj_din_parte():
    return controls_if(
        [
            (eq_num("parteMemorata", 1), set_num("virajCurent", -1)),
            (eq_num("parteMemorata", 2), set_num("virajCurent", 1)),
        ],
        set_num("virajCurent", 0),
    )


def remember_side_after_wait(side):
    # Both lateral patterns share momentInceputLateral. The sketch reads that timer through LiniaDreapta.
    return controls_if(
        [(compare("GTE", millis_minus("momentInceputLateral"), var_get("pragLateralMs")), set_num("parteMemorata", side))]
    )


def caz11():
    return chain(
        [
            set_num("virajCurent", 0),
            set_num("parteMemorata", 0),
            set_num("esteCurbaTare", 0),
            set_num("senzorDeIgnorat", 0),
        ]
    )


def caz_lateral(ignore_code, straight_side, cross_memory, cross_ignore, turn_code):
    # Each branch ends the case. Later branches run only when the earlier condition is false.
    straight_body = chain([remember_side_after_wait(straight_side), set_num("virajCurent", 0)])
    cross_body = chain(
        [
            set_num("virajCurent", 0),
            set_num("parteMemorata", 0),
            set_num("esteCurbaTare", 0),
            set_num("senzorDeIgnorat", cross_ignore),
        ]
    )
    turn_body = chain(
        [
            controls_if(
                [
                    (
                        neq_num("parteMemorata", straight_side),
                        chain([set_millis("momentInceputViraj"), set_num("esteCurbaTare", 0)]),
                    )
                ]
            ),
            set_num("parteMemorata", straight_side),
            mark_hard_curve(),
            set_num("virajCurent", turn_code),
        ]
    )
    decision = controls_if(
        [
            (eq_num("senzorDeIgnorat", ignore_code), set_num("virajCurent", 0)),
            (eq_num("virajAnterior", 0), straight_body),
            (eq_num("parteMemorata", cross_memory), cross_body),
        ],
        turn_body,
    )
    return chain([var_set("virajAnterior", var_get("virajCurent")), decision])


def caz00():
    already_turning = chain([mark_hard_curve(), viraj_din_parte()])
    start_from_straight = chain(
        [
            controls_if(
                [
                    (
                        eq_num("virajAnterior", 0),
                        chain([set_millis("momentInceputViraj"), set_num("esteCurbaTare", 0)]),
                    )
                ]
            ),
            mark_hard_curve(),
            viraj_din_parte(),
        ]
    )
    has_memory = controls_if(
        [
            (neq_num("virajAnterior", 0), already_turning),
            (elapsed_gte("momentInceputDeraiere", "prag00Ms"), start_from_straight),
        ],
        set_num("virajCurent", 0),
    )
    return chain(
        [
            var_set("virajAnterior", var_get("virajCurent")),
            set_num("senzorDeIgnorat", 0),
            controls_if([(neq_num("parteMemorata", 0), has_memory)], set_num("virajCurent", 0)),
        ]
    )


def porneste_cronometre():
    def arm(code, timer):
        return controls_if(
            [
                (
                    logic_and(eq_num("combinatieSenzoriAcum", code), neq_num("combinatieSenzoriAnterioara", code)),
                    set_millis(timer),
                )
            ]
        )

    return chain(
        [
            arm(3, "momentInceputStabil"),
            arm(2, "momentInceputLateral"),
            arm(1, "momentInceputLateral"),
            arm(0, "momentInceputDeraiere"),
        ]
    )


def citeste_combinatie():
    both = logic_and(eq_num("senzorStanga", 1), eq_num("senzorDreapta", 1))
    left = logic_and(eq_num("senzorStanga", 1), eq_num("senzorDreapta", 0))
    right = logic_and(eq_num("senzorStanga", 0), eq_num("senzorDreapta", 1))
    return controls_if(
        [
            (both, set_num("combinatieSenzoriAcum", 3)),
            (left, set_num("combinatieSenzoriAcum", 2)),
            (right, set_num("combinatieSenzoriAcum", 1)),
        ],
        set_num("combinatieSenzoriAcum", 0),
    )


def actualizeaza_viraj():
    return chain(
        [
            controls_if([(eq_num("combinatieSenzoriAcum", 3), caz11())]),
            controls_if([(eq_num("combinatieSenzoriAcum", 2), caz_lateral(1, 1, 2, 1, -1))]),
            controls_if([(eq_num("combinatieSenzoriAcum", 1), caz_lateral(2, 2, 1, 2, 1))]),
            controls_if([(eq_num("combinatieSenzoriAcum", 0), caz00())]),
        ]
    )


def speed_add(base, extra):
    return arith("ADD", var_get(base), var_get(extra))


def aplica_motoare():
    straight = chain(
        [
            var_set("vitezaMotorStanga", speed_add("vitezaMare", "compensareDrept")),
            var_set("vitezaMotorDreapta", var_get("vitezaMare")),
        ]
    )
    soft_left = chain(
        [
            var_set("vitezaMotorStanga", speed_add("vitezaMica", "compensareVitMica")),
            var_set("vitezaMotorDreapta", var_get("vitezaMare")),
        ]
    )
    hard_left = chain(
        [
            var_set("vitezaMotorStanga", var_get("vitezaStationara")),
            var_set("vitezaMotorDreapta", var_get("vitezaMare")),
        ]
    )
    left = controls_if([(eq_num("esteCurbaTare", 1), hard_left)], soft_left)
    soft_right = chain(
        [
            var_set("vitezaMotorStanga", speed_add("vitezaMare", "compensareVitMare")),
            var_set("vitezaMotorDreapta", var_get("vitezaMica")),
        ]
    )
    hard_right = chain(
        [
            var_set("vitezaMotorStanga", speed_add("vitezaMare", "compensareVitMare")),
            var_set("vitezaMotorDreapta", var_get("vitezaStationara")),
        ]
    )
    right = controls_if([(eq_num("esteCurbaTare", 1), hard_right)], soft_right)
    choose = controls_if(
        [
            (eq_num("virajCurent", 0), straight),
            (eq_num("virajCurent", -1), left),
            (eq_num("virajCurent", 1), right),
        ]
    )
    send = chain(
        [
            var_set("vitezaTrimisaStanga", var_get("vitezaMotorStanga")),
            var_set("vitezaTrimisaDreapta", var_get("vitezaMotorDreapta")),
            serial_write(var_get("CodMotor")),
            serial_write(num(1)),
            serial_write(var_get("codViteza")),
            serial_write(var_get("vitezaMotorStanga")),
            serial_write(var_get("CodMotor")),
            serial_write(num(2)),
            serial_write(var_get("codViteza")),
            serial_write(var_get("vitezaMotorDreapta")),
        ]
    )
    changed = controls_if(
        [
            (
                logic_or(
                    compare("NEQ", var_get("vitezaMotorStanga"), var_get("vitezaTrimisaStanga")),
                    compare("NEQ", var_get("vitezaMotorDreapta"), var_get("vitezaTrimisaDreapta")),
                ),
                send,
            )
        ]
    )
    return chain(
        [
            set_num("vitezaMotorStanga", 0),
            set_num("vitezaMotorDreapta", 0),
            choose,
            changed,
        ]
    )


def citeste_senzorii():
    press = controls_if(
        [
            (
                logic_and(eq_num("stareButonAnterior", 0), eq_num("stareButonCurenta", 1)),
                set_millis("tStartButon"),
            )
        ]
    )
    armed = controls_if(
        [
            (
                logic_and(neq_num("tStartButon", 0), elapsed_gte("tStartButon", "durataPornire")),
                set_num("robotPornit", 1),
            )
        ]
    )
    waiting = controls_if(
        [(eq_num("robotPornit", 0), chain([press, var_set("stareButonAnterior", var_get("stareButonCurenta")), armed]))]
    )
    return chain(
        [
            var_set("senzorStanga", digital_read(9)),
            var_set("senzorDreapta", digital_read(3)),
            var_set("stareButonCurenta", digital_read(7)),
            led("senzorDreapta", 5),
            led("senzorStanga", 6),
            waiting,
        ]
    )


def loop_body():
    follow = chain(
        [
            citeste_combinatie(),
            porneste_cronometre(),
            actualizeaza_viraj(),
            aplica_motoare(),
            var_set("combinatieSenzoriAnterioara", var_get("combinatieSenzoriAcum")),
        ]
    )
    return chain(
        [
            citeste_senzorii(),
            controls_if([(eq_num("robotPornit", 1), follow)]),
        ]
    )


def stop_motors():
    return chain(
        [
            serial_write(var_get("CodMotor")),
            serial_write(num(1)),
            serial_write(var_get("codViteza")),
            serial_write(num(0)),
            serial_write(var_get("CodMotor")),
            serial_write(num(2)),
            serial_write(var_get("codViteza")),
            serial_write(num(0)),
        ]
    )


def setup_body():
    decls = [
        ("CodMotor", "byte", 254),
        ("codViteza", "byte", 240),
        ("senzorStanga", "int", 0),
        ("senzorDreapta", "int", 0),
        ("vitezaMica", "byte", 40),
        ("vitezaMare", "byte", 240),
        ("vitezaStationara", "byte", 0),
        ("compensareDrept", "int", 0),
        ("compensareVitMica", "int", 0),
        ("compensareVitMare", "int", 0),
        ("pragCurba", "int", 70),
        ("prag00Ms", "int", 8),
        ("pragOscilareMs", "int", 120),
        ("pragStabilMs", "int", 80),
        ("pragLateralMs", "int", 0),
        ("virajCurent", "int", 0),
        ("parteMemorata", "int", 0),
        ("esteCurbaTare", "int", 0),
        ("momentInceputViraj", "long", 0),
        ("senzorDeIgnorat", "int", 0),
        ("vitezaTrimisaStanga", "int", 0),
        ("vitezaTrimisaDreapta", "int", 0),
        ("stareButonCurenta", "int", 0),
        ("robotPornit", "int", 0),
        ("durataPornire", "int", 2000),
        ("tStartButon", "long", 0),
        ("stareButonAnterior", "int", 0),
        ("combinatieSenzoriAnterioara", "int", -1),
        ("momentInceputDeraiere", "long", 0),
        ("momentInceputLateral", "long", 0),
        ("momentInceputStabil", "long", 0),
        ("combinatieSenzoriAcum", "int", 0),
        ("virajAnterior", "int", 0),
        ("vitezaMotorStanga", "int", 0),
        ("vitezaMotorDreapta", "int", 0),
    ]
    blocks = [var_decl(name, typ, value) for name, typ, value in decls]
    blocks += [
        pin_mode(9, "INPUT"),
        pin_mode(3, "INPUT"),
        pin_mode(5, "OUTPUT"),
        pin_mode(6, "OUTPUT"),
        pin_mode(7, "INPUT"),
        stop_motors(),
        (
            f'<block type="controls_whileUntil" id="{nid()}">'
            f'<field name="MODE">WHILE</field>'
            f'<value name="BOOL"><block type="logic_boolean" id="{nid()}">'
            f'<field name="BOOL">TRUE</field></block></value>'
            f'<statement name="DO">{loop_body()}</statement></block>'
        ),
    ]
    return chain(blocks)


def main():
    xml = (
        '<xml version="0.997" board="Arduino Uno WiFi" xmlns="http://www.w3.org/1999/xhtml">'
        f'<block type="base_setup" id="{nid()}" x="-420" y="-380">'
        f'<statement name="DO">{setup_body()}</statement></block></xml>'
    )
    ET.fromstring(xml)
    DST.write_text(xml.replace('"', '\\"'), encoding="utf-8")
    print(f"Wrote {DST} ({DST.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
