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
    //public static int antiOscilareActiv;
    public static int pragOscilareMs;
    public static int pragStabilMs;
    public static int pragLateralMs;
    public static Viraj stareViraj;
    public static Viraj ultimulViraj;
    public static bool esteCurba;
    public static long tStartViraj;
    public static IgnoraSenzor ignoraSenzor;
    public static Viraj stareMotor;
    public static bool? curbaTrimisa;
    public static int motorStanga;
    public static int motorDreapta;
    public static int stareButonCurenta;
    public static int robotPornit;
    public static int durataPornire;
    public static long tStartButon;
    public static int stareButonAnterior;
    public static CombinatieSenzori combinatieSenzoriAnterioara;
    public static int linieInstabila;
    //  public static int ultimLateral;
    //  public static long tUltimLateral;
    public static long tStart00;
    public static long tStartLateral;
    public static long timpStartStabil;

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
        //antiOscilareActiv = 1;
        pragOscilareMs = 120;
        pragStabilMs = 80;
        pragLateralMs = 0;
        stareViraj = Viraj.Drept;
        ultimulViraj = Viraj.Drept;
        esteCurba = false;
        tStartViraj = 0;
        ignoraSenzor = IgnoraSenzor.Niciunul;
        stareMotor = Viraj.Dreapta;
        curbaTrimisa = null;
        motorStanga = 0;
        motorDreapta = 0;
        stareButonCurenta = 0;
        robotPornit = 0;
        durataPornire = 2000;
        tStartButon = 0;
        stareButonAnterior = 0;
        combinatieSenzoriAnterioara = CombinatieSenzori.Necunoscut;
        linieInstabila = 0;
        // ultimLateral = 0;
        // tUltimLateral = 0;
        tStart00 = 0;
        tStartLateral = 0;
        timpStartStabil = 0;

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
                CombinatieSenzori combinatieSenzoriAcum = CitesteCombinatieSenzori();
                StartCronometre(combinatieSenzoriAcum);

                if (combinatieSenzoriAcum == CombinatieSenzori.AmbeleLinii)
                {
                    //if (antiOscilareActiv == 1 && (millis() - timpStartStabil) >= pragStabilMs)
                    //{
                    //    linieInstabila = 0;
                    //}

                    //  ultimLateral = 0;
                    stareViraj = Viraj.Drept;
                    ultimulViraj = Viraj.Drept;
                    esteCurba = false;
                    ignoraSenzor = 0;
                }
                if (combinatieSenzoriAcum == CombinatieSenzori.LiniaStanga)
                {

                    //if (antiOscilareActiv == 1)
                    //{
                    //    if (ultimLateral == 2 && (millis() - tUltimLateral) <= pragOscilareMs)
                    //    {
                    //        linieInstabila = 1;
                    //    }

                    //    ultimLateral = 1;
                    //    tUltimLateral = millis();
                    //}

                    if (ignoraSenzor == IgnoraSenzor.IgnoraStanga)
                    {
                        stareViraj = Viraj.Drept;
                    }
                    else if (stareViraj != Viraj.Drept && ultimulViraj == Viraj.Dreapta)
                    {
                        stareViraj = Viraj.Drept;
                        ultimulViraj = Viraj.Drept;
                        esteCurba = false;
                        ignoraSenzor = IgnoraSenzor.IgnoraStanga;
                    }
                    else if (stareViraj == Viraj.Drept)
                    {
                        if (linieInstabila == 0 && CitesteCronometru(CombinatieSenzori.LiniaDreapta) >= pragLateralMs)
                        {
                            ultimulViraj = Viraj.Stanga;
                        }

                        stareViraj = Viraj.Drept;
                    }
                    else
                    {
                        if (ultimulViraj != Viraj.Stanga)
                        {
                            tStartViraj = millis();
                            esteCurba = false;
                        }

                        ultimulViraj = Viraj.Stanga;
                        esteCurba = CitesteCronometruStartViraj() >= pragCurba ? true : esteCurba;
                        
                        stareViraj = Viraj.Stanga;
                    }
                }
                if (combinatieSenzoriAcum == CombinatieSenzori.LiniaDreapta)
                {

                    //if (antiOscilareActiv == 1)
                    //{
                    //    if (ultimLateral == 1 && (millis() - tUltimLateral) <= pragOscilareMs)
                    //    {
                    //        linieInstabila = 1;
                    //    }

                    //    ultimLateral = 2;
                    //    tUltimLateral = millis();
                    //}

                    if (ignoraSenzor == IgnoraSenzor.IgnoraDreapta)
                    {
                        stareViraj = Viraj.Drept;
                    }
                    else if (stareViraj != Viraj.Drept && ultimulViraj == Viraj.Stanga)
                    {
                        stareViraj = Viraj.Drept;
                        ultimulViraj = Viraj.Drept;
                        esteCurba = false;
                        ignoraSenzor = IgnoraSenzor.IgnoraDreapta;
                    }
                    else if (stareViraj == Viraj.Drept)
                    {
                        if (linieInstabila == 0 && CitesteCronometru(CombinatieSenzori.LiniaDreapta) >= pragLateralMs)
                        {
                            ultimulViraj = Viraj.Dreapta;
                        }

                        stareViraj = Viraj.Drept;
                    }
                    else
                    {
                        if (ultimulViraj != Viraj.Dreapta)
                        {
                            tStartViraj = millis();
                            esteCurba = false;
                        }

                        ultimulViraj = Viraj.Dreapta;
                        esteCurba = CitesteCronometruStartViraj() >= pragCurba ? true : esteCurba;

                        stareViraj = Viraj.Dreapta;
                    }
                }
                if (combinatieSenzoriAcum == CombinatieSenzori.NicioLinie)
                {

                    ignoraSenzor = 0;

                    if (linieInstabila == 1)
                    {
                        stareViraj = Viraj.Drept;
                    }
                    else if (ultimulViraj != Viraj.Drept)
                    {
                        if (stareViraj != Viraj.Drept)
                        {
                            if (CitesteCronometruStartViraj() >= pragCurba)
                            {
                                esteCurba = true;
                            }

                            stareViraj = ultimulViraj;
                        }
                        else if ((millis() - tStart00) >= prag00Ms)
                        {
                            if (stareViraj == 0)
                            {
                                tStartViraj = millis();
                                esteCurba = false;
                            }

                            if (CitesteCronometruStartViraj() >= pragCurba)
                            {
                                esteCurba = true;
                            }

                            stareViraj = ultimulViraj;
                        }
                        else
                        {
                            stareViraj = 0;
                        }
                    }
                    else
                    {
                        stareViraj = 0;
                    }
                }

                combinatieSenzoriAnterioara = combinatieSenzoriAcum;

                if (linieInstabila == 1 && stareViraj != 0)
                {
                    stareViraj = 0;
                    esteCurba = false;
                }

                if (stareViraj == 0)
                {
                    motorStanga = vitezaMare + compensareDrept;
                    motorDreapta = vitezaMare;
                }
                else if (stareViraj == Viraj.Stanga)
                {
                    if (esteCurba == true)
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
                    if (esteCurba == true)
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

                if (stareViraj != stareMotor || esteCurba != curbaTrimisa)
                {
                    stareMotor = stareViraj;
                    curbaTrimisa = esteCurba;
                    Engine.SetSpeed(motorStanga, motorDreapta);

                }
            }
        }
    }

    private static long CitesteCronometruStartViraj()
    {
        return millis() - tStartViraj;
    }
    private static void StartCronometre(CombinatieSenzori stareaCurenta)
    {

        if (stareaCurenta == CombinatieSenzori.AmbeleLinii && combinatieSenzoriAnterioara != stareaCurenta)
        {
            timpStartStabil = millis();
        }


        if (stareaCurenta == CombinatieSenzori.LiniaStanga && combinatieSenzoriAnterioara != stareaCurenta)
        {
            tStartLateral = millis();
        }

        if (stareaCurenta == CombinatieSenzori.LiniaDreapta && combinatieSenzoriAnterioara != stareaCurenta)
        {
            tStartLateral = millis();
        }

        if (stareaCurenta == CombinatieSenzori.NicioLinie && combinatieSenzoriAnterioara != stareaCurenta)
        {
            tStart00 = millis();
        }

    }
    public static long CitesteCronometru(CombinatieSenzori pentruStarea)
    {
        long timpCurent = 0;
        if (pentruStarea == CombinatieSenzori.AmbeleLinii)
        {
            timpCurent = millis() - timpStartStabil;
        }
        if (pentruStarea == CombinatieSenzori.LiniaStanga || pentruStarea == CombinatieSenzori.LiniaDreapta)
        {
            timpCurent = millis() - tStartLateral;
        }
        if (pentruStarea == CombinatieSenzori.NicioLinie)
        {
            timpCurent = millis() - tStart00;
        }
        return timpCurent;
    }

    private static CombinatieSenzori CitesteCombinatieSenzori()
    {
        CombinatieSenzori stareSenzoriAcum;
        if (senzorStanga == 1 && senzorDreapta == 1)
        {
            stareSenzoriAcum = CombinatieSenzori.AmbeleLinii;
        }
        else if (senzorStanga == 1 && senzorDreapta == 0)
        {
            stareSenzoriAcum = CombinatieSenzori.LiniaStanga;
        }
        else if (senzorStanga == 0 && senzorDreapta == 1)
        {
            stareSenzoriAcum = CombinatieSenzori.LiniaDreapta;
        }
        else
        {
            stareSenzoriAcum = CombinatieSenzori.NicioLinie;
        }

        return stareSenzoriAcum;
    }

    public static void loop()
    {
    }
}
