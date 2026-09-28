# Mixly 0.997 file for the simple four-case follower.
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
DST = ROOT / "Traseu stelian V11 - simplu.mix"

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


def motor_case(code, left_xml, right_xml):
    return chain(
        [
            var_set("comanda", num(code)),
            var_set("motorStanga", left_xml),
            var_set("motorDreapta", right_xml),
        ]
    )


def serial_motors():
    return chain(
        [
            var_set("comandaTrimisa", var_get("comanda")),
            serial_write(var_get("CodMotor")),
            serial_write(num(1)),
            serial_write(var_get("codViteza")),
            serial_write(var_get("motorStanga")),
            serial_write(var_get("CodMotor")),
            serial_write(num(2)),
            serial_write(var_get("codViteza")),
            serial_write(var_get("motorDreapta")),
        ]
    )


def button_wait():
    edge = controls_if(
        [
            (
                logic_and(
                    compare("NEQ", var_get("butonPrev"), var_get("butonApasat")),
                    compare("EQ", var_get("buton"), var_get("butonApasat")),
                ),
                chain(
                    [
                        var_set("tStartButon", millis_block()),
                        var_set("butonFaza", num(1)),
                    ]
                ),
            )
        ]
    )
    first = controls_if(
        [(compare("EQ", var_get("butonPrev"), num(99)), var_set("butonPrev", var_get("buton")))],
        chain([edge, var_set("butonPrev", var_get("buton"))]),
    )
    elapsed = controls_if(
        [
            (
                compare("EQ", var_get("butonFaza"), num(1)),
                controls_if(
                    [
                        (
                            compare("GTE", millis_minus("tStartButon"), var_get("durataPornire")),
                            var_set("pornit", num(1)),
                        )
                    ]
                ),
            )
        ]
    )
    return chain([first, elapsed])


def drive():
    cases = controls_if(
        [
            (sensors(1, 1), motor_case(0, var_get("vitezaMare"), var_get("vitezaMare"))),
            (sensors(1, 0), motor_case(1, var_get("vitezaMica"), var_get("vitezaMare"))),
            (sensors(0, 1), motor_case(2, var_get("vitezaMare"), var_get("vitezaMica"))),
        ],
        motor_case(3, num(0), var_get("vitezaMare")),
    )
    send = controls_if(
        [(compare("NEQ", var_get("comanda"), var_get("comandaTrimisa")), serial_motors())]
    )
    return chain([cases, send])


def led(sensor, pin):
    return controls_if(
        [(compare("EQ", var_get(sensor), num(1)), digital_write(pin, "HIGH"))],
        digital_write(pin, "LOW"),
    )


def loop_body():
    return chain(
        [
            var_set("senzorStanga", digital_read(9)),
            var_set("senzorDreapta", digital_read(3)),
            led("senzorDreapta", 5),
            led("senzorStanga", 6),
            var_set("buton", digital_read(7)),
            controls_if(
                [(compare("EQ", var_get("pornit"), num(0)), button_wait())],
                drive(),
            ),
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
        ("comanda", "int", 0),
        ("comandaTrimisa", "int", 99),
        ("motorStanga", "int", 0),
        ("motorDreapta", "int", 0),
        ("butonApasat", "int", 1),
        ("buton", "int", 0),
        ("pornit", "int", 0),
        ("butonFaza", "int", 0),
        ("durataPornire", "int", 2000),
        ("tStartButon", "long", 0),
        ("butonPrev", "int", 99),
    ]
    blocks = [var_decl(name, typ, value) for name, typ, value in decls]
    blocks += [
        pin_mode(9, "INPUT"),
        pin_mode(3, "INPUT"),
        pin_mode(5, "OUTPUT"),
        pin_mode(6, "OUTPUT"),
        pin_mode(7, "INPUT"),
    ]
    blocks += [
        serial_write(var_get("CodMotor")),
        serial_write(num(1)),
        serial_write(var_get("codViteza")),
        serial_write(num(0)),
        serial_write(var_get("CodMotor")),
        serial_write(num(2)),
        serial_write(var_get("codViteza")),
        serial_write(num(0)),
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
    body = setup_body()
    xml = (
        '<xml version="0.997" board="Arduino Uno WiFi" xmlns="http://www.w3.org/1999/xhtml">'
        f'<block type="base_setup" id="{nid()}" x="-420" y="-380">'
        f"<statement name=\"DO\">{body}</statement></block></xml>"
    )
    import xml.etree.ElementTree as ET

    ET.fromstring(xml)
    DST.write_text(xml.replace('"', '\\"'), encoding="utf-8")
    print(f"Wrote {DST}")


if __name__ == "__main__":
    main()
