# Mixly 0.997 file for V12: sensors on both sides of the line, with turn memory
# and the 00 = straight / 00 = lost decision. Mirrors "Traseu stelian V12 - senzori laterali.cpp".
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import generate_simplu_mix as g  # noqa: E402
from generate_simplu_mix import (  # noqa: E402
    button_wait, chain, compare, controls_if, digital_read, led, logic_and,
    millis_block, millis_minus, nid, num, pin_mode, serial_motors, serial_write,
    var_decl, var_get, var_set,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
DST = ROOT / "Traseu stelian V12 - senzori laterali.mix"


def arith(op, a, b):
    return (
        f'<block type="math_arithmetic" id="{nid()}">'
        f'<field name="OP">{op}</field>'
        f'<value name="A"><shadow type="math_number" id="{nid()}"><field name="NUM">1</field></shadow>{a}</value>'
        f'<value name="B"><shadow type="math_number" id="{nid()}"><field name="NUM">1</field></shadow>{b}</value></block>'
    )


def logic_or(a, b):
    return (
        f'<block type="logic_operation" id="{nid()}">'
        f'<field name="OP">OR</field>'
        f'<value name="A">{a}</value><value name="B">{b}</value></block>'
    )


def eq(name, value):
    return compare("EQ", var_get(name), num(value))


def sensors(left, right):
    return logic_and(eq("senzorStanga", left), eq("senzorDreapta", right))


def set_n(name, value):
    return var_set(name, num(value))


def speeds(left_xml, right_xml):
    return chain([var_set("motorStanga", left_xml), var_set("motorDreapta", right_xml)])


def by_side(left_case, right_case):
    return controls_if([(eq("parte", -1), left_case)], right_case)


def drive():
    pattern = controls_if(
        [
            (sensors(1, 1), set_n("patternAcum", 3)),
            (sensors(1, 0), set_n("patternAcum", 2)),
            (sensors(0, 1), set_n("patternAcum", 1)),
        ],
        set_n("patternAcum", 0),
    )

    lateral = chain([
        controls_if([(
            compare("NEQ", var_get("patternAcum"), var_get("patternPrev")),
            chain([
                var_set("tStartLateral", millis_block()),
                controls_if([(eq("mod", 3), set_n("revenire", 1))], set_n("revenire", 0)),
            ]),
        )]),
        controls_if([(eq("patternAcum", 2), set_n("parte", -1))], set_n("parte", 1)),
        controls_if(
            [(compare("GTE", millis_minus("tStartLateral"), var_get("pragCurba")), set_n("mod", 2))],
            set_n("mod", 1),
        ),
    ])

    zero = controls_if([
        (
            logic_or(eq("patternPrev", 1), eq("patternPrev", 2)),
            controls_if(
                [
                    (eq("revenire", 1), chain([set_n("mod", 0), set_n("revenire", 0)])),
                    (
                        compare("LT", millis_minus("tStartLateral"), var_get("pragTraversareMs")),
                        chain([set_n("mod", 3), var_set("tStartPierdut", millis_block())]),
                    ),
                ],
                set_n("mod", 0),
            ),
        ),
        (
            eq("mod", 3),
            controls_if([(
                compare("GTE", millis_minus("tStartPierdut"), var_get("pragCautareMs")),
                set_n("mod", 4),
            )]),
        ),
    ])

    decide = controls_if(
        [
            (eq("patternAcum", 3), chain([set_n("mod", 0), set_n("parte", 0), set_n("revenire", 0)])),
            (logic_or(eq("patternAcum", 2), eq("patternAcum", 1)), lateral),
        ],
        zero,
    )

    motors = controls_if(
        [
            (eq("mod", 0), speeds(arith("ADD", var_get("vitezaMare"), var_get("compensareDrept")), var_get("vitezaMare"))),
            (eq("mod", 1), by_side(
                speeds(var_get("vitezaMica"), var_get("vitezaMare")),
                speeds(arith("ADD", var_get("vitezaMare"), var_get("compensareDrept")), var_get("vitezaMica")),
            )),
            (eq("mod", 2), by_side(
                speeds(num(0), var_get("vitezaMare")),
                speeds(arith("ADD", var_get("vitezaMare"), var_get("compensareDrept")), num(0)),
            )),
            (eq("mod", 3), by_side(
                speeds(num(0), var_get("vitezaCautare")),
                speeds(var_get("vitezaCautare"), num(0)),
            )),
        ],
        speeds(num(0), num(0)),
    )

    send = chain([
        var_set("comanda", arith("ADD", arith("MULTIPLY", var_get("mod"), num(10)), var_get("parte"))),
        controls_if([(compare("NEQ", var_get("comanda"), var_get("comandaTrimisa")), serial_motors())]),
    ])

    stop = controls_if([(
        eq("mod", 4),
        chain([
            set_n("pornit", 0), set_n("butonFaza", 0), set_n("mod", 0), set_n("parte", 0),
            set_n("revenire", 0), set_n("patternPrev", -1), set_n("comandaTrimisa", 99),
        ]),
    )])

    return chain([pattern, decide, var_set("patternPrev", var_get("patternAcum")), motors, send, stop])


def loop_body():
    return chain([
        var_set("senzorStanga", digital_read(9)),
        var_set("senzorDreapta", digital_read(3)),
        led("senzorDreapta", 5),
        led("senzorStanga", 6),
        var_set("buton", digital_read(7)),
        controls_if([(eq("pornit", 0), button_wait())], drive()),
    ])


def setup_body():
    decls = [
        ("CodMotor", "byte", 254), ("codViteza", "byte", 240),
        ("senzorStanga", "int", 0), ("senzorDreapta", "int", 0),
        ("vitezaMica", "byte", 40), ("vitezaMare", "byte", 200), ("vitezaCautare", "byte", 160),
        ("compensareDrept", "int", 0),
        ("pragCurba", "int", 70), ("pragTraversareMs", "int", 40), ("pragCautareMs", "int", 1500),
        ("mod", "int", 0), ("parte", "int", 0), ("revenire", "int", 0),
        ("patternAcum", "int", 0), ("patternPrev", "int", -1),
        ("tStartLateral", "long", 0), ("tStartPierdut", "long", 0),
        ("comanda", "int", 0), ("comandaTrimisa", "int", 99),
        ("motorStanga", "int", 0), ("motorDreapta", "int", 0),
        ("butonApasat", "int", 1), ("buton", "int", 0), ("pornit", "int", 0),
        ("butonFaza", "int", 0), ("durataPornire", "int", 2000),
        ("tStartButon", "long", 0), ("butonPrev", "int", 99),
    ]
    blocks = [var_decl(n, t, v) for n, t, v in decls]
    blocks += [pin_mode(9, "INPUT"), pin_mode(3, "INPUT"), pin_mode(5, "OUTPUT"),
               pin_mode(6, "OUTPUT"), pin_mode(7, "INPUT")]
    blocks += [
        serial_write(var_get("CodMotor")), serial_write(num(1)), serial_write(var_get("codViteza")), serial_write(num(0)),
        serial_write(var_get("CodMotor")), serial_write(num(2)), serial_write(var_get("codViteza")), serial_write(num(0)),
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
        f'<statement name="DO">{body}</statement></block></xml>'
    )
    import xml.etree.ElementTree as ET
    ET.fromstring(xml)
    DST.write_text(xml.replace('"', '\\"'), encoding="utf-8")
    print(f"Wrote {DST}")


if __name__ == "__main__":
    main()
