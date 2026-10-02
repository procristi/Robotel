using System.Windows;
using Robotel.LineFollower.Simulated.Arduino;
using Robotel.LineFollower.Sketch;

namespace Robotel.Simulator.Simulation;

/// <summary>
/// Robot pose on the photo. Heading 0 faces the top of the image. Positive heading is a left turn.
/// </summary>
public sealed class CourseSimulator
{
    public double AxleX { get; set; }
    public double AxleY { get; set; }
    public double Heading { get; set; }
    public bool LeftSeesLine { get; private set; }
    public bool RightSeesLine { get; private set; }
    public List<Point> Trail { get; } = new();

    public void ResetMotion(double axleX, double axleY, double heading)
    {
        AxleX = axleX;
        AxleY = axleY;
        Heading = heading;
        LeftSeesLine = false;
        RightSeesLine = false;
        ArduinoApi.TimpSimulat = 0;
        V11HisterezisV3Sketch.ResetStare();
        Trail.Clear();
        Trail.Add(new Point(axleX, axleY));
    }

    public void Step(TrackMap map, RobotGeometry geometry, double cmPerPixel, double dtSeconds)
    {
        ReadSensors(map, geometry, cmPerPixel);
        var zoneStanga = LeftSeesLine;
        var zoneDreapta = RightSeesLine;

        ApplySketchParameters(geometry);
        ArduinoApi.TimpSimulat += (long)Math.Round(dtSeconds * 1000.0);
        V11HisterezisV3Sketch.Pas(zoneStanga ? 1 : 0, zoneDreapta ? 1 : 0);

        var (leftCm, rightCm) = (
            geometry.CmPerSecond(V11HisterezisV3Sketch.vitezaTrimisaStanga),
            geometry.CmPerSecond(V11HisterezisV3Sketch.vitezaTrimisaDreapta));
        var centerCm = (leftCm + rightCm) / 2.0;
        var track = Math.Max(0.1, geometry.TrackCm);
        var omega = (rightCm - leftCm) / track;

        Heading += omega * dtSeconds;
        var forwardX = -Math.Sin(Heading);
        var forwardY = -Math.Cos(Heading);
        var pixels = (centerCm * dtSeconds) / cmPerPixel;
        AxleX += forwardX * pixels;
        AxleY += forwardY * pixels;

        Trail.Add(new Point(AxleX, AxleY));
        if (Trail.Count > 8000)
        {
            Trail.RemoveRange(0, Trail.Count - 8000);
        }
    }

    public Point ToScreen(double lateralCm, double forwardCm, double cmPerPixel)
    {
        var forwardX = -Math.Sin(Heading);
        var forwardY = -Math.Cos(Heading);
        var rightX = -forwardY;
        var rightY = forwardX;
        var lateralPx = lateralCm / cmPerPixel;
        var forwardPx = forwardCm / cmPerPixel;
        return new Point(
            AxleX + (rightX * lateralPx) + (forwardX * forwardPx),
            AxleY + (rightY * lateralPx) + (forwardY * forwardPx));
    }

    private static void ApplySketchParameters(RobotGeometry geometry)
    {
        V11HisterezisV3Sketch.vitezaMica = (byte)Math.Clamp(geometry.VitezaMica, 0, 255);
        V11HisterezisV3Sketch.vitezaMare = (byte)Math.Clamp(geometry.VitezaMare, 0, 255);
        V11HisterezisV3Sketch.vitezaStationara = (byte)Math.Clamp(geometry.VitezaStationara, 0, 255);
        V11HisterezisV3Sketch.compensareDrept = geometry.CompensareDrept;
        V11HisterezisV3Sketch.compensareVitMica = geometry.CompensareVitMica;
        V11HisterezisV3Sketch.compensareVitMare = geometry.CompensareVitMare;
        V11HisterezisV3Sketch.pragCurba = geometry.PragCurbaMs;
        V11HisterezisV3Sketch.prag00Ms = geometry.Prag00Ms;
        V11HisterezisV3Sketch.pragLateralMs = geometry.PragLateralMs;
    }

    public void ReadSensors(TrackMap map, RobotGeometry geometry, double cmPerPixel)
    {
        LeftSeesLine = ZoneSeesBlack(map, geometry, cmPerPixel, geometry.LeftSpan());
        RightSeesLine = ZoneSeesBlack(map, geometry, cmPerPixel, geometry.RightSpan());
    }

    // The measured rectangle sees the line when any sample inside it is black.
    private bool ZoneSeesBlack(TrackMap map, RobotGeometry geometry, double cmPerPixel, (double From, double To) span)
    {
        var (near, far) = geometry.ForwardBand();
        var step = Math.Max(cmPerPixel * 0.5, 0.05);
        for (var forward = near; forward <= far + 1e-9; forward += step)
        {
            for (var lateral = span.From; lateral <= span.To + 1e-9; lateral += step)
            {
                var point = ToScreen(lateral, forward, cmPerPixel);
                if (map.IsBlack((int)Math.Round(point.X), (int)Math.Round(point.Y)))
                {
                    return true;
                }
            }
        }

        return false;
    }
}
