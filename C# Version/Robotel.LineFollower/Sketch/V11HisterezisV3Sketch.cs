using Robotel.LineFollower.Helpers;
using Robotel.LineFollower.Simulated.Arduino;
using Robotel.Utils;

namespace Robotel.LineFollower.Sketch;

/// <summary>
/// Each loop reads the sensors, starts a timer when the sensor pattern changes,
/// chooses the current turn from that pattern and from the remembered turn,
/// then sends wheel speeds.
/// </summary>
public static class V11HisterezisV3Sketch
{
    public static int senzorStanga;
    public static int senzorDreapta;
    public static byte vitezaMica;
    public static byte vitezaMare;
    // Inner-wheel speed during a hard turn. The outer wheel stays at vitezaMare.
    public static byte vitezaStationara;
    public static int compensareDrept;
    public static int compensareVitMica;
    public static int compensareVitMare;
    public static int pragCurba;
    public static int prag00Ms;
    //public static int antiOscilareActiv;
    public static int pragOscilareMs;
    public static int pragStabilMs;
    public static int pragLateralMs;
    public static Viraj virajCurent;
    // Side of the line stored while both wheels still run straight. Used when both sensors leave the line.
    public static ParteLinie parteMemorata;
    public static bool esteCurbaTare;
    public static long momentInceputViraj;
    public static IgnoraSenzor senzorDeIgnorat;
    // Last wheel speeds written to the motors.
    public static int vitezaTrimisaStanga;
    public static int vitezaTrimisaDreapta;

    public static int stareButonCurenta;
    public static int robotPornit;
    public static int durataPornire;
    public static long tStartButon;
    public static int stareButonAnterior;
    public static CombinatieSenzori combinatieSenzoriAnterioara;
    // public static int linieInstabila;
    //  public static int ultimLateral;
    //  public static long tUltimLateral;
    public static long momentInceputDeraiere;
    public static long momentInceputLateral;
    public static long momentInceputStabil;

    // Turn for each new 00, in order. The first new 00 uses the first entry. After the last entry, 00 uses parteMemorata from the sensors.
    private static readonly Viraj[] virajeSuprascriseLa00 =
    {
       /* Viraj.Stanga,
        Viraj.Stanga,
        Viraj.Dreapta,
        Viraj.Stanga,
        Viraj.Stanga,
        Viraj.Stanga,
        Viraj.Dreapta*/
    };
    private static int indexVirajSuprascris;

    // Desktop simulator only. Do not translate this method to Mixly.
    public static void ResetStare()
    {
        senzorStanga = 0;
        senzorDreapta = 0;
        virajCurent = Viraj.Inainte;
        parteMemorata = ParteLinie.Niciuna;
        esteCurbaTare = false;
        momentInceputViraj = 0;
        senzorDeIgnorat = IgnoraSenzor.Niciunul;
        vitezaTrimisaStanga = 0;
        vitezaTrimisaDreapta = 0;
        combinatieSenzoriAnterioara = CombinatieSenzori.Necunoscut;
        momentInceputDeraiere = 0;
        momentInceputLateral = 0;
        momentInceputStabil = 0;
        indexVirajSuprascris = 0;
    }

    // Desktop simulator only. One decision step with sensors already read. Do not translate this method to Mixly.
    public static void Pas(int stanga, int dreapta)
    {
        senzorStanga = stanga;
        senzorDreapta = dreapta;
        var combinatieSenzoriAcum = CitesteCombinatieSenzori();
        PornesteCronometre(combinatieSenzoriAcum);
        ActualizeazaViraj(combinatieSenzoriAcum);
        AplicaMotoare();
        combinatieSenzoriAnterioara = combinatieSenzoriAcum;
    }

    public static void setup()
    {
        senzorStanga = 0;
        senzorDreapta = 0;
        vitezaMica = 40;
        vitezaMare = 240;
        vitezaStationara = 0;
        compensareDrept = 0;
        compensareVitMica = 0;
        compensareVitMare = 0;
        pragCurba = 70;
        prag00Ms = 8;
        //antiOscilareActiv = 1;
        pragOscilareMs = 120;
        pragStabilMs = 80;
        pragLateralMs = 0;
        virajCurent = Viraj.Inainte;
        parteMemorata = ParteLinie.Niciuna;
        esteCurbaTare = false;
        momentInceputViraj = 0;
        senzorDeIgnorat = IgnoraSenzor.Niciunul;
        vitezaTrimisaStanga = 0;
        vitezaTrimisaDreapta = 0;

        stareButonCurenta = 0;
        robotPornit = 0;
        durataPornire = 2000;
        tStartButon = 0;
        stareButonAnterior = 0;
        combinatieSenzoriAnterioara = CombinatieSenzori.Necunoscut;
        //linieInstabila = 0;
        // ultimLateral = 0;
        // tUltimLateral = 0;
        momentInceputDeraiere = 0;
        momentInceputLateral = 0;
        momentInceputStabil = 0;
        indexVirajSuprascris = 0;

        Pin.SetPinMode(Pins.SenzorStanga, PinMode.Input);
        Pin.SetPinMode(Pins.SenzorDreapta, PinMode.Input);
        Pin.SetPinMode(Pins.BecDreapta, PinMode.Output);
        Pin.SetPinMode(Pins.BecStanga, PinMode.Output);
        Pin.SetPinMode(Pins.Buton, PinMode.Input);

        Serial.begin(9600);

        Engine.SetSpeed(0, 0);

        while (true)
        {
            CitesteenSenzorii();
            if (robotPornit == 1)
            {
                CombinatieSenzori combinatieSenzoriAcum = CitesteCombinatieSenzori();
                PornesteCronometre(combinatieSenzoriAcum);
                ActualizeazaViraj(combinatieSenzoriAcum);
                AplicaMotoare();
                combinatieSenzoriAnterioara = combinatieSenzoriAcum;
            }
        }
    }

    private static void CitesteenSenzorii()
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
    }

    private static void ActualizeazaViraj(CombinatieSenzori combinatieSenzoriAcum)
    {
        if (combinatieSenzoriAcum == CombinatieSenzori.AmbeleLinii)
        {
            Caz11();
        }
        if (combinatieSenzoriAcum == CombinatieSenzori.LiniaStanga)
        {
            Caz10();
        }
        if (combinatieSenzoriAcum == CombinatieSenzori.LiniaDreapta)
        {
            Caz01();
        }
        if (combinatieSenzoriAcum == CombinatieSenzori.NicioLinie)
        {
            Caz00();
        }

        //if (/*linieInstabila == 1 &&*/ virajCurent != Viraj.Inainte)
        //{
        //    virajCurent = Viraj.Inainte;
        //    esteCurbaTare = false;
        //}
    }

    private static void Caz11()
    {
        //if (antiOscilareActiv == 1 && (millis() - momentInceputStabil) >= pragStabilMs)
        //{
        //    linieInstabila = 0;
        //}

        //  ultimLateral = 0;
        virajCurent = Viraj.Inainte;
        parteMemorata = ParteLinie.Niciuna;
        esteCurbaTare = false;
        senzorDeIgnorat = IgnoraSenzor.Niciunul;
    }

    private static void Caz10()
    {
        var virajAnterior = virajCurent;
        //if (antiOscilareActiv == 1)
        //{
        //    if (ultimLateral == 2 && (millis() - tUltimLateral) <= pragOscilareMs)
        //    {
        //        linieInstabila = 1;
        //    }

        //    ultimLateral = 1;
        //    tUltimLateral = millis();
        //}

        if (senzorDeIgnorat == IgnoraSenzor.IgnoraStanga)
        {
            virajCurent = Viraj.Inainte;
            return;
        }

        if (virajAnterior == Viraj.Inainte)
        {
            if (/*linieInstabila == 0 &&*/ CitesteCronometru(CombinatieSenzori.LiniaDreapta) >= pragLateralMs)
            {
                parteMemorata = ParteLinie.Stanga;
            }

            virajCurent = Viraj.Inainte;
            return;
        }

        if (virajAnterior != Viraj.Inainte && parteMemorata == ParteLinie.Dreapta)
        {
            virajCurent = Viraj.Inainte;
            parteMemorata = ParteLinie.Niciuna;
            esteCurbaTare = false;
            senzorDeIgnorat = IgnoraSenzor.IgnoraStanga;
            return;
        }



        if (parteMemorata != ParteLinie.Stanga)
        {
            momentInceputViraj = millis();
            esteCurbaTare = false;
        }

        parteMemorata = ParteLinie.Stanga;
        esteCurbaTare = CitesteCronometruStartViraj() >= pragCurba ? true : esteCurbaTare;

        virajCurent = Viraj.Stanga;

    }

    private static void Caz01()
    {
        var virajAnterior = virajCurent;
        //if (antiOscilareActiv == 1)
        //{
        //    if (ultimLateral == 1 && (millis() - tUltimLateral) <= pragOscilareMs)
        //    {
        //        linieInstabila = 1;
        //    }

        //    ultimLateral = 2;
        //    tUltimLateral = millis();
        //}

        if (senzorDeIgnorat == IgnoraSenzor.IgnoraDreapta)
        {
            virajCurent = Viraj.Inainte;
            return;
        }
        if (virajAnterior == Viraj.Inainte)
        {
            if (/*linieInstabila == 0 &&*/ CitesteCronometru(CombinatieSenzori.LiniaDreapta) >= pragLateralMs)
            {
                parteMemorata = ParteLinie.Dreapta;
            }

            virajCurent = Viraj.Inainte;
            return;
        }

        if (virajAnterior != Viraj.Inainte && parteMemorata == ParteLinie.Stanga)
        {
            virajCurent = Viraj.Inainte;
            parteMemorata = ParteLinie.Niciuna;
            esteCurbaTare = false;
            senzorDeIgnorat = IgnoraSenzor.IgnoraDreapta;
            return;
        }

        if (parteMemorata != ParteLinie.Dreapta)
        {
            momentInceputViraj = millis();
            esteCurbaTare = false;
        }

        parteMemorata = ParteLinie.Dreapta;
        esteCurbaTare = CitesteCronometruStartViraj() >= pragCurba ? true : esteCurbaTare;

        virajCurent = Viraj.Dreapta;

    }

    private static void Caz00()
    {
        var virajAnterior = virajCurent;
        senzorDeIgnorat = IgnoraSenzor.Niciunul;
        AplicaSuprascriere00();
        /*
        if (linieInstabila == 1)
        {
            virajCurent = Viraj.Drept;
        }
        else 
            */
        if (parteMemorata != ParteLinie.Niciuna)
        {
            if (virajAnterior != Viraj.Inainte)
            {
                if (CitesteCronometruStartViraj() >= pragCurba)
                {
                    esteCurbaTare = true;
                }

                virajCurent = VirajDinParteMemorata();
            }
            else if ((millis() - momentInceputDeraiere) >= prag00Ms)
            {
                if (virajAnterior == Viraj.Inainte)
                {
                    momentInceputViraj = millis();
                    esteCurbaTare = false;
                }

                if (CitesteCronometruStartViraj() >= pragCurba)
                {
                    esteCurbaTare = true;
                }

                virajCurent = VirajDinParteMemorata();
            }
            else
            {
                virajCurent = Viraj.Inainte;
            }
        }
        else
        {
            virajCurent = Viraj.Inainte;
        }
    }

    private static void AplicaMotoare()
    {
        int vitezaMotorStanga = 0;
        int vitezaMotorDreapta = 0;
        switch (virajCurent)
        {
            case Viraj.Inainte:
                vitezaMotorStanga = vitezaMare + compensareDrept;
                vitezaMotorDreapta = vitezaMare;
                break;
            case Viraj.Stanga:
                if (esteCurbaTare == true)
                {
                    vitezaMotorStanga = vitezaStationara;
                    vitezaMotorDreapta = vitezaMare;
                }
                else
                {
                    vitezaMotorStanga = vitezaMica + compensareVitMica;
                    vitezaMotorDreapta = vitezaMare;
                }
                break;
            case Viraj.Dreapta:
                if (esteCurbaTare == true)
                {
                    vitezaMotorStanga = vitezaMare + compensareVitMare;
                    vitezaMotorDreapta = vitezaStationara;
                }
                else
                {
                    vitezaMotorStanga = vitezaMare + compensareVitMare;
                    vitezaMotorDreapta = vitezaMica;
                }
                break;
        }


        if (vitezaMotorStanga != vitezaTrimisaStanga || vitezaMotorDreapta != vitezaTrimisaDreapta)
        {
            vitezaTrimisaStanga = vitezaMotorStanga;
            vitezaTrimisaDreapta = vitezaMotorDreapta;
            Engine.SetSpeed(vitezaMotorStanga, vitezaMotorDreapta);
        }
    }

    private static long CitesteCronometruStartViraj()
    {
        return millis() - momentInceputViraj;
    }

    // On the first loop of a new 00, store the next listed side into parteMemorata.
    private static void AplicaSuprascriere00()
    {
        if (combinatieSenzoriAnterioara == CombinatieSenzori.NicioLinie)
        {
            return;
        }

        if (indexVirajSuprascris >= virajeSuprascriseLa00.Length)
        {
            return;
        }

        var viraj = virajeSuprascriseLa00[indexVirajSuprascris];
        indexVirajSuprascris++;
        if (viraj == Viraj.Stanga)
        {
            parteMemorata = ParteLinie.Stanga;
        }
        else if (viraj == Viraj.Dreapta)
        {
            parteMemorata = ParteLinie.Dreapta;
        }
    }

    private static Viraj VirajDinParteMemorata()
    {
        if (parteMemorata == ParteLinie.Stanga)
        {
            return Viraj.Stanga;
        }

        if (parteMemorata == ParteLinie.Dreapta)
        {
            return Viraj.Dreapta;
        }

        return Viraj.Inainte;
    }

    private static void PornesteCronometre(CombinatieSenzori stareaCurenta)
    {
        if (stareaCurenta == CombinatieSenzori.AmbeleLinii && combinatieSenzoriAnterioara != stareaCurenta)
        {
            momentInceputStabil = millis();
        }

        if (stareaCurenta == CombinatieSenzori.LiniaStanga && combinatieSenzoriAnterioara != stareaCurenta)
        {
            momentInceputLateral = millis();
        }

        if (stareaCurenta == CombinatieSenzori.LiniaDreapta && combinatieSenzoriAnterioara != stareaCurenta)
        {
            momentInceputLateral = millis();
        }

        if (stareaCurenta == CombinatieSenzori.NicioLinie && combinatieSenzoriAnterioara != stareaCurenta)
        {
            momentInceputDeraiere = millis();
        }
    }

    public static long CitesteCronometru(CombinatieSenzori pentruStarea)
    {
        long timpCurent = 0;
        if (pentruStarea == CombinatieSenzori.AmbeleLinii)
        {
            timpCurent = millis() - momentInceputStabil;
        }
        if (pentruStarea == CombinatieSenzori.LiniaStanga || pentruStarea == CombinatieSenzori.LiniaDreapta)
        {
            timpCurent = millis() - momentInceputLateral;
        }
        if (pentruStarea == CombinatieSenzori.NicioLinie)
        {
            timpCurent = millis() - momentInceputDeraiere;
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
