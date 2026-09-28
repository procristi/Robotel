using Robotel.LineFollower.Helpers;
using Robotel.LineFollower.Simulated.Arduino;
using Robotel.Utils;

namespace Robotel.LineFollower.Sketch;

/// <summary>
/// Authoring copy of Traseu stelian V11 - histerezis v3.cpp — translate blocks to Mixly; do not run on PC.
/// </summary>
public static class V11HisterezisV3Sketch
{
    public static int senzorStanga;
    public static int senzorDreapta;
    public static byte vitezaMica;
    public static byte vitezaMare;
    public static int compensareDrept;
    public static int compensareVitMica;
    public static int compensareVitMare;
    public static int pragCurba;
    public static int prag00Ms;
    public static int antiOscilareActiv;
    public static int pragOscilareMs;
    public static int pragStabilMs;
    public static int pragLateralMs;
    public static int stare;
    public static int ultimaDirectie;
    public static int esteCurba;
    public static long tStartViraj;
    public static int ignoraSenzor;
    public static int stareMotor;
    public static int curbaTrimisa;
    public static int motorStanga;
    public static int motorDreapta;
    public static int stareButonCurenta;
    public static int robotPornit;
    public static int durataPornire;
    public static long tStartButon;
    public static int stareButonAnterior;
    public static int patternPrev;
    public static int linieInstabila;
    public static int ultimLateral;
    public static long tUltimLateral;
    public static long tStart00;
    public static long tStartLateral;
    public static long tStartStabil11;

    public static void setup()
    {
        senzorStanga = 0;
        senzorDreapta = 0;
        vitezaMica = 40;
        vitezaMare = 240;
        compensareDrept = 0;
        compensareVitMica = 0;
        compensareVitMare = 0;
        pragCurba = 70;
        prag00Ms = 8;
        antiOscilareActiv = 1;
        pragOscilareMs = 120;
        pragStabilMs = 80;
        pragLateralMs = 0;
        stare = 0;
        ultimaDirectie = 0;
        esteCurba = 0;
        tStartViraj = 0;
        ignoraSenzor = 0;
        stareMotor = 99;
        curbaTrimisa = 99;
        motorStanga = 0;
        motorDreapta = 0;
        stareButonCurenta = 0;
        robotPornit = 0;
        durataPornire = 2000;
        tStartButon = 0;
        stareButonAnterior = 0;
        patternPrev = -1;
        linieInstabila = 0;
        ultimLateral = 0;
        tUltimLateral = 0;
        tStart00 = 0;
        tStartLateral = 0;
        tStartStabil11 = 0;

        Pin.SetPinMode(Pins.SenzorStanga, PinMode.Input);
        Pin.SetPinMode(Pins.SenzorDreapta, PinMode.Input);
        Pin.SetPinMode(Pins.BecDreapta, PinMode.Output);
        Pin.SetPinMode(Pins.BecStanga, PinMode.Output);
        Pin.SetPinMode(Pins.Buton, PinMode.Input);

        Serial.begin(9600);

        Engine.SetSpeed(0, 0);

        while (true)
        {
            senzorStanga = Pin.Citeste(Pins.SenzorStanga);
            senzorDreapta = Pin.Citeste(Pins.SenzorDreapta);
            stareButonCurenta = Pin.Citeste(Pins.Buton);

            Pin.DigitalWrite(Pins.BecDreapta, senzorDreapta == 1 ? PinState.High : PinState.Low);
            Pin.DigitalWrite(Pins.BecStanga, senzorStanga == 1 ? PinState.High : PinState.Low);


            if (robotPornit == 0)
            {
                if (stareButonAnterior == 0 && stareButonCurenta == 1)
                {
                    tStartButon = millis();
                }

                stareButonAnterior = stareButonCurenta;

                if (tStartButon != 0 && (millis() - tStartButon) >= durataPornire)
                {
                    robotPornit = 1;
                }
            }
            if (robotPornit == 1)
            {
                int patternAcum;
                if (senzorStanga == 1 && senzorDreapta == 1)
                {
                    patternAcum = 3;
                }
                else if (senzorStanga == 1 && senzorDreapta == 0)
                {
                    patternAcum = 2;
                }
                else if (senzorStanga == 0 && senzorDreapta == 1)
                {
                    patternAcum = 1;
                }
                else
                {
                    patternAcum = 0;
                }

                if (patternAcum == 3)
                {
                    if (patternPrev != 3)
                    {
                        tStartStabil11 = millis();
                    }

                    if (antiOscilareActiv == 1 && (millis() - tStartStabil11) >= pragStabilMs)
                    {
                        linieInstabila = 0;
                    }

                    ultimLateral = 0;
                    stare = 0;
                    ultimaDirectie = 0;
                    esteCurba = 0;
                    ignoraSenzor = 0;
                }
                else if (patternAcum == 2)
                {
                    if (patternPrev != 2)
                    {
                        tStartLateral = millis();
                    }

                    if (antiOscilareActiv == 1)
                    {
                        if (ultimLateral == 2 && (millis() - tUltimLateral) <= pragOscilareMs)
                        {
                            linieInstabila = 1;
                        }

                        ultimLateral = 1;
                        tUltimLateral = millis();
                    }

                    if (ignoraSenzor == 1)
                    {
                        stare = 0;
                    }
                    else if (stare != 0 && ultimaDirectie == 1)
                    {
                        stare = 0;
                        ultimaDirectie = 0;
                        esteCurba = 0;
                        ignoraSenzor = 1;
                    }
                    else if (stare == 0)
                    {
                        if (linieInstabila == 0 && (millis() - tStartLateral) >= pragLateralMs)
                        {
                            ultimaDirectie = -1;
                        }

                        stare = 0;
                    }
                    else
                    {
                        if (ultimaDirectie != -1)
                        {
                            tStartViraj = millis();
                            esteCurba = 0;
                        }

                        ultimaDirectie = -1;
                        if ((millis() - tStartViraj) >= pragCurba)
                        {
                            esteCurba = 1;
                        }

                        stare = -1;
                    }
                }
                else if (patternAcum == 1)
                {
                    if (patternPrev != 1)
                    {
                        tStartLateral = millis();
                    }

                    if (antiOscilareActiv == 1)
                    {
                        if (ultimLateral == 1 && (millis() - tUltimLateral) <= pragOscilareMs)
                        {
                            linieInstabila = 1;
                        }

                        ultimLateral = 2;
                        tUltimLateral = millis();
                    }

                    if (ignoraSenzor == 2)
                    {
                        stare = 0;
                    }
                    else if (stare != 0 && ultimaDirectie == -1)
                    {
                        stare = 0;
                        ultimaDirectie = 0;
                        esteCurba = 0;
                        ignoraSenzor = 2;
                    }
                    else if (stare == 0)
                    {
                        if (linieInstabila == 0 && (millis() - tStartLateral) >= pragLateralMs)
                        {
                            ultimaDirectie = 1;
                        }

                        stare = 0;
                    }
                    else
                    {
                        if (ultimaDirectie != 1)
                        {
                            tStartViraj = millis();
                            esteCurba = 0;
                        }

                        ultimaDirectie = 1;
                        if ((millis() - tStartViraj) >= pragCurba)
                        {
                            esteCurba = 1;
                        }

                        stare = 1;
                    }
                }
                else
                {
                    if (patternPrev != 0)
                    {
                        tStart00 = millis();
                    }

                    ignoraSenzor = 0;

                    if (linieInstabila == 1)
                    {
                        stare = 0;
                    }
                    else if (ultimaDirectie != 0)
                    {
                        if (stare != 0)
                        {
                            if ((millis() - tStartViraj) >= pragCurba)
                            {
                                esteCurba = 1;
                            }

                            stare = ultimaDirectie;
                        }
                        else if ((millis() - tStart00) >= prag00Ms)
                        {
                            if (stare == 0)
                            {
                                tStartViraj = millis();
                                esteCurba = 0;
                            }

                            if ((millis() - tStartViraj) >= pragCurba)
                            {
                                esteCurba = 1;
                            }

                            stare = ultimaDirectie;
                        }
                        else
                        {
                            stare = 0;
                        }
                    }
                    else
                    {
                        stare = 0;
                    }
                }

                patternPrev = patternAcum;

                if (linieInstabila == 1 && stare != 0)
                {
                    stare = 0;
                    esteCurba = 0;
                }

                if (stare == 0)
                {
                    motorStanga = vitezaMare + compensareDrept;
                    motorDreapta = vitezaMare;
                }
                else if (stare == -1)
                {
                    if (esteCurba == 1)
                    {
                        motorStanga = 0;
                        motorDreapta = vitezaMare;
                    }
                    else
                    {
                        motorStanga = vitezaMica + compensareVitMica;
                        motorDreapta = vitezaMare;
                    }
                }
                else
                {
                    if (esteCurba == 1)
                    {
                        motorStanga = vitezaMare + compensareVitMare;
                        motorDreapta = 0;
                    }
                    else
                    {
                        motorStanga = vitezaMare + compensareVitMare;
                        motorDreapta = vitezaMica;
                    }
                }

                if (stare != stareMotor || esteCurba != curbaTrimisa)
                {
                    stareMotor = stare;
                    curbaTrimisa = esteCurba;
                    Engine.SetSpeed(motorStanga, motorDreapta);

                }
            }
        }
    }

    public static void loop()
    {
    }
}
