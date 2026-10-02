namespace Robotel.Simulator.Simulation;

/// <summary>
/// Physical sizes in centimeters. Lateral sensor edges are signed: negative is left of the longitudinal axis, positive is right.
/// Track width is the distance between wheel centers: total outer width minus one wheel width.
/// </summary>
public sealed class RobotGeometry
{
    public double LatimeRoataCm { get; init; }
    public double LatimeTotalaCm { get; init; }
    public double LungimeTotalaCm { get; init; }
    public double SpatePanaLaAxCm { get; init; }
    public double DetectieAproapeCm { get; init; }
    public double DetectieDeparteCm { get; init; }
    public double StangaDeLaCm { get; init; }
    public double StangaPanaLaCm { get; init; }
    public double DreaptaDeLaCm { get; init; }
    public double DreaptaPanaLaCm { get; init; }
    public int VitezaMica { get; init; }
    public int VitezaMare { get; init; }
    public int VitezaStationara { get; init; }
    public int CompensareDrept { get; init; }
    public int CompensareVitMica { get; init; }
    public int CompensareVitMare { get; init; }
    public int PragCurbaMs { get; init; }
    public int Prag00Ms { get; init; }
    public int PragLateralMs { get; init; }
    public double CmPerSecLa40 { get; init; }
    public double CmPerSecLa50 { get; init; }
    public double CmPerSecLa100 { get; init; }
    public double CmPerSecLa230 { get; init; }
    public double CmPerSecLa239 { get; init; }
    public double CmPerSecLa240 { get; init; }

    public double TrackCm => Math.Max(0.1, LatimeTotalaCm - LatimeRoataCm);

    public double FataDeLaAxCm => Math.Max(0, LungimeTotalaCm - SpatePanaLaAxCm);

    public double LatimeCorpCm => Math.Max(0.1, LatimeTotalaCm - (2 * LatimeRoataCm));

    public double CmPerSecond(double speedByte)
    {
        var speed = Math.Max(0, speedByte);
        (double At, double Cm)[] points =
        [
            (0, 0),
            (40, CmPerSecLa40),
            (50, CmPerSecLa50),
            (100, CmPerSecLa100),
            (230, CmPerSecLa230),
            (239, CmPerSecLa239),
            (240, CmPerSecLa240)
        ];
        if (speed >= points[^1].At)
        {
            return points[^1].Cm;
        }

        for (var i = 1; i < points.Length; i++)
        {
            if (speed <= points[i].At)
            {
                var span = points[i].At - points[i - 1].At;
                var t = span <= 0 ? 0 : (speed - points[i - 1].At) / span;
                return points[i - 1].Cm + (t * (points[i].Cm - points[i - 1].Cm));
            }
        }

        return points[^1].Cm;
    }

    public (double Near, double Far) ForwardBand()
    {
        var near = Math.Min(DetectieAproapeCm, DetectieDeparteCm);
        var far = Math.Max(DetectieAproapeCm, DetectieDeparteCm);
        return (near, far);
    }

    public (double From, double To) LeftSpan()
    {
        return (Math.Min(StangaDeLaCm, StangaPanaLaCm), Math.Max(StangaDeLaCm, StangaPanaLaCm));
    }

    public (double From, double To) RightSpan()
    {
        return (Math.Min(DreaptaDeLaCm, DreaptaPanaLaCm), Math.Max(DreaptaDeLaCm, DreaptaPanaLaCm));
    }
}
