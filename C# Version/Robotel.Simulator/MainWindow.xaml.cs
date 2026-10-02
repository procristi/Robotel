using System.Globalization;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Shapes;
using System.Windows.Threading;
using Microsoft.Win32;
using Robotel.LineFollower.Helpers;
using Robotel.LineFollower.Simulated.Arduino;
using Robotel.LineFollower.Sketch;
using Robotel.Simulator.Simulation;

namespace Robotel.Simulator;

public partial class MainWindow : Window
{
    private const string DefaultImage = @"D:\Work\Personale\Stelian\Robotel\Traseu Simulare.png";
    private const double SubstepSeconds = 0.005;

    private readonly CourseSimulator _course = new();
    private readonly DispatcherTimer _timer;
    private TrackMap? _map;
    private double _cmPerPixel = 0.05;
    private double _placeX;
    private double _placeY;
    private double _placeHeading;
    private Point? _dragStart;
    private bool _running;

    public MainWindow()
    {
        InitializeComponent();
        _timer = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(33) };
        _timer.Tick += Timer_Tick;
        if (File.Exists(DefaultImage))
        {
            LoadTrack(DefaultImage);
        }

        UpdateSpeedLabel();
    }

    private void LoadImage_Click(object sender, RoutedEventArgs e)
    {
        var dialog = new OpenFileDialog
        {
            Filter = "Imagini|*.png;*.jpg;*.jpeg;*.bmp|Toate|*.*"
        };
        if (dialog.ShowDialog() == true)
        {
            LoadTrack(dialog.FileName);
        }
    }

    private void LoadTrack(string path)
    {
        Pause_Click(this, new RoutedEventArgs());
        var threshold = ReadInt(DarknessBox, 100);
        _map = new TrackMap(path, (byte)Math.Clamp(threshold, 0, 255));
        TrackImage.Source = _map.Source;
        Scene.Width = _map.Width;
        Scene.Height = _map.Height;
        Overlay.Width = _map.Width;
        Overlay.Height = _map.Height;
        ImagePathText.Text = path;
        LineWidthPxBox.Text = _map.EstimateLineWidthPixels().ToString(CultureInfo.InvariantCulture);
        ApplyScale();
        _placeX = _map.Width / 2.0;
        _placeY = _map.Height * 0.85;
        _placeHeading = 0;
        _course.ResetMotion(_placeX, _placeY, _placeHeading);
        DrawOverlay();
    }

    private void DetectWidth_Click(object sender, RoutedEventArgs e)
    {
        if (_map == null)
        {
            return;
        }

        _map.DarknessThreshold = (byte)Math.Clamp(ReadInt(DarknessBox, 100), 0, 255);
        LineWidthPxBox.Text = _map.EstimateLineWidthPixels().ToString(CultureInfo.InvariantCulture);
        ApplyScale();
        DrawOverlay();
    }

    private void ScaleInput_LostFocus(object sender, RoutedEventArgs e)
    {
        if (_map != null)
        {
            _map.DarknessThreshold = (byte)Math.Clamp(ReadInt(DarknessBox, 100), 0, 255);
        }

        ApplyScale();
        DrawOverlay();
    }

    private void Redraw_LostFocus(object sender, RoutedEventArgs e)
    {
        UpdateTrackLabel();
        UpdateSpeedLabel();
        DrawOverlay();
    }

    private void ApplyScale()
    {
        var lineCm = ReadDouble(LineWidthCmBox, 2);
        var linePx = Math.Max(1, ReadDouble(LineWidthPxBox, 1));
        _cmPerPixel = lineCm / linePx;
        var pxPerCm = 1.0 / _cmPerPixel;
        ScaleText.Text = $"Scară: 1 cm = {pxPerCm:0.0} px. Linia neagră are {lineCm:0.##} cm.";
        UpdateTrackLabel();
    }

    private void UpdateTrackLabel()
    {
        var wheel = ReadDouble(WheelWidthBox, 2.7);
        var total = ReadDouble(TotalWidthBox, 13.5);
        var length = ReadDouble(LengthBox, 17);
        var rear = ReadDouble(RearToAxleBox, 7.7);
        var track = Math.Max(0.1, total - wheel);
        var front = Math.Max(0, length - rear);
        TrackText.Text =
            $"Centre roți: {track:0.00} cm. Corp: {Math.Max(0.1, total - (2 * wheel)):0.00} cm lățime. " +
            $"Față, de la ax până la vârf: {front:0.00} cm.";
    }

    private void Start_Click(object sender, RoutedEventArgs e)
    {
        if (_map == null)
        {
            return;
        }

        _running = true;
        _timer.Start();
    }

    private void Pause_Click(object sender, RoutedEventArgs e)
    {
        _running = false;
        _timer.Stop();
    }

    private void MemorizeStart_Click(object sender, RoutedEventArgs e)
    {
        _placeX = _course.AxleX;
        _placeY = _course.AxleY;
        _placeHeading = _course.Heading;
        StatusText.Text = "Poziția de start este cea de acum. Reset readuce robotul aici.";
    }

    private void Reset_Click(object sender, RoutedEventArgs e)
    {
        Pause_Click(sender, e);
        _course.ResetMotion(_placeX, _placeY, _placeHeading);
        DrawOverlay();
        StatusText.Text = "Robotul e în poziția plasată.";
    }

    private void Timer_Tick(object? sender, EventArgs e)
    {
        if (_map == null || !_running)
        {
            return;
        }

        var geometry = ReadGeometry();
        var scale = TimeScaleSlider.Value;
        var simulated = 0.033 * scale;
        var steps = Math.Max(1, (int)Math.Round(simulated / SubstepSeconds));
        var dt = simulated / steps;
        for (var i = 0; i < steps; i++)
        {
            _course.Step(_map, geometry, _cmPerPixel, dt);
        }

        DrawOverlay();
        var pattern = V11HisterezisV3Sketch.combinatieSenzoriAnterioara switch
        {
            CombinatieSenzori.AmbeleLinii => "11",
            CombinatieSenzori.LiniaStanga => "10",
            CombinatieSenzori.LiniaDreapta => "01",
            CombinatieSenzori.NicioLinie => "00",
            _ => "--"
        };
        StatusText.Text =
            $"Senzori {pattern}   viraj {V11HisterezisV3Sketch.virajCurent}   curbă tare {(V11HisterezisV3Sketch.esteCurbaTare ? "da" : "nu")}   " +
            $"viteze {V11HisterezisV3Sketch.vitezaTrimisaStanga}/{V11HisterezisV3Sketch.vitezaTrimisaDreapta}   t {ArduinoApi.TimpSimulat} ms";
    }

    private void Scene_MouseLeftButtonDown(object sender, MouseButtonEventArgs e)
    {
        if (_map == null)
        {
            return;
        }

        _dragStart = e.GetPosition(Scene);
        Scene.CaptureMouse();
    }

    private void Scene_MouseMove(object sender, MouseEventArgs e)
    {
        if (_dragStart == null || e.LeftButton != MouseButtonState.Pressed)
        {
            return;
        }

        var point = e.GetPosition(Scene);
        ApplyDrag(_dragStart.Value, point, commit: false);
    }

    private void Scene_MouseLeftButtonUp(object sender, MouseButtonEventArgs e)
    {
        if (_dragStart == null)
        {
            return;
        }

        var point = e.GetPosition(Scene);
        ApplyDrag(_dragStart.Value, point, commit: true);
        _dragStart = null;
        Scene.ReleaseMouseCapture();
    }

    private void ApplyDrag(Point start, Point end, bool commit)
    {
        var heading = _placeHeading;
        var dx = end.X - start.X;
        var dy = end.Y - start.Y;
        if ((dx * dx) + (dy * dy) > 36)
        {
            heading = Math.Atan2(-dx, -dy);
        }

        if (commit)
        {
            _placeX = start.X;
            _placeY = start.Y;
            _placeHeading = heading;
        }

        _course.ResetMotion(start.X, start.Y, heading);
        DrawOverlay();
    }

    private void DrawOverlay()
    {
        Overlay.Children.Clear();
        if (_map == null)
        {
            return;
        }

        var geometry = ReadGeometry();
        _course.ReadSensors(_map, geometry, _cmPerPixel);
        if (_course.Trail.Count > 1)
        {
            var trail = new Polyline
            {
                Stroke = Brushes.DodgerBlue,
                StrokeThickness = 2,
                Points = new PointCollection(_course.Trail)
            };
            Overlay.Children.Add(trail);
        }

        var wheel = geometry.LatimeRoataCm;
        var halfOuter = geometry.LatimeTotalaCm / 2.0;
        var halfInner = halfOuter - wheel;
        var halfBody = geometry.LatimeCorpCm / 2.0;
        DrawRect(-halfBody, halfBody, -geometry.SpatePanaLaAxCm, geometry.FataDeLaAxCm, new SolidColorBrush(Color.FromRgb(80, 80, 80)));
        DrawRect(-halfOuter, -halfInner, -wheel / 2, wheel / 2, Brushes.Black);
        DrawRect(halfInner, halfOuter, -wheel / 2, wheel / 2, Brushes.Black);

        DrawZone(geometry, leftSide: true, _course.LeftSeesLine ? Brushes.LimeGreen : Brushes.Yellow);
        DrawZone(geometry, leftSide: false, _course.RightSeesLine ? Brushes.LimeGreen : Brushes.Orange);

        var axleLeft = _course.ToScreen(-halfOuter, 0, _cmPerPixel);
        var axleRight = _course.ToScreen(halfOuter, 0, _cmPerPixel);
        Overlay.Children.Add(new Line
        {
            X1 = axleLeft.X,
            Y1 = axleLeft.Y,
            X2 = axleRight.X,
            Y2 = axleRight.Y,
            Stroke = Brushes.Red,
            StrokeThickness = 2
        });

        var nose = _course.ToScreen(0, geometry.FataDeLaAxCm, _cmPerPixel);
        var axle = _course.ToScreen(0, 0, _cmPerPixel);
        Overlay.Children.Add(new Line
        {
            X1 = axle.X,
            Y1 = axle.Y,
            X2 = nose.X,
            Y2 = nose.Y,
            Stroke = Brushes.Red,
            StrokeThickness = 1
        });

        var barCm = 10.0;
        var barPx = barCm / _cmPerPixel;
        var bar = new Line
        {
            X1 = 16,
            Y1 = 24,
            X2 = 16 + barPx,
            Y2 = 24,
            Stroke = Brushes.Black,
            StrokeThickness = 3
        };
        Overlay.Children.Add(bar);
        Overlay.Children.Add(new TextBlock
        {
            Text = "10 cm",
            Foreground = Brushes.Black,
            Margin = new Thickness(16, 28, 0, 0)
        });
    }

    private void DrawZone(RobotGeometry geometry, bool leftSide, Brush fill)
    {
        var (near, far) = geometry.ForwardBand();
        var (from, to) = leftSide ? geometry.LeftSpan() : geometry.RightSpan();
        var polygon = new Polygon
        {
            Fill = fill,
            Opacity = 0.45,
            Points = new PointCollection
            {
                _course.ToScreen(from, near, _cmPerPixel),
                _course.ToScreen(to, near, _cmPerPixel),
                _course.ToScreen(to, far, _cmPerPixel),
                _course.ToScreen(from, far, _cmPerPixel)
            }
        };
        Overlay.Children.Add(polygon);
    }

    private void DrawRect(double lateralMin, double lateralMax, double forwardMin, double forwardMax, Brush fill)
    {
        var polygon = new Polygon
        {
            Fill = fill,
            Points = new PointCollection
            {
                _course.ToScreen(lateralMin, forwardMin, _cmPerPixel),
                _course.ToScreen(lateralMax, forwardMin, _cmPerPixel),
                _course.ToScreen(lateralMax, forwardMax, _cmPerPixel),
                _course.ToScreen(lateralMin, forwardMax, _cmPerPixel)
            }
        };
        Overlay.Children.Add(polygon);
    }

    private RobotGeometry ReadGeometry()
    {
        return new RobotGeometry
        {
            LatimeRoataCm = ReadDouble(WheelWidthBox, 2.7),
            LatimeTotalaCm = ReadDouble(TotalWidthBox, 13.5),
            LungimeTotalaCm = ReadDouble(LengthBox, 17),
            SpatePanaLaAxCm = ReadDouble(RearToAxleBox, 7.7),
            DetectieAproapeCm = ReadDouble(NearBox, 7.5),
            DetectieDeparteCm = ReadDouble(FarBox, 9),
            StangaDeLaCm = ReadDouble(LeftFromBox, -1.2),
            StangaPanaLaCm = ReadDouble(LeftToBox, 0),
            DreaptaDeLaCm = ReadDouble(RightFromBox, -0.1),
            DreaptaPanaLaCm = ReadDouble(RightToBox, 1.9),
            VitezaMica = ReadInt(SlowBox, 40),
            VitezaMare = ReadInt(FastBox, 240),
            VitezaStationara = ReadInt(StationaryBox, 0),
            PragCurbaMs = ReadInt(PragCurbaBox, 70),
            Prag00Ms = ReadInt(Prag00Box, 8),
            PragLateralMs = ReadInt(PragLateralBox, 0),
            CmPerSecLa40 = CalibCmPerSec(40),
            CmPerSecLa50 = CalibCmPerSec(50),
            CmPerSecLa100 = CalibCmPerSec(100),
            CmPerSecLa230 = CalibCmPerSec(230),
            CmPerSecLa239 = CalibCmPerSec(239),
            CmPerSecLa240 = CalibCmPerSec(240)
        };
    }

    private void UpdateSpeedLabel()
    {
        var at40 = CalibCmPerSec(40);
        var at50 = CalibCmPerSec(50);
        var at100 = CalibCmPerSec(100);
        var at230 = CalibCmPerSec(230);
        var at239 = CalibCmPerSec(239);
        var at240 = CalibCmPerSec(240);
        SpeedCalibText.Text =
            $"40 → {at40:0.0} cm/s, 50 → {at50:0.0}, 100 → {at100:0.0}, 230 → {at230:0.0}, 239 → {at239:0.0}, 240 → {at240:0.0}.";
    }

    private double CalibCmPerSec(double speedByte)
    {
        var distance = ReadDouble(CalibDistanceBox, 111.9);
        var seconds = speedByte switch
        {
            40 => ReadDouble(Time40Box, 6.54),
            50 => ReadDouble(Time50Box, 5.12),
            100 => ReadDouble(Time100Box, 2.8),
            230 => ReadDouble(Time230Box, 2.82),
            239 => ReadDouble(Time239Box, 2.94),
            _ => ReadDouble(Time240Box, 2.96)
        };
        if (seconds <= 0)
        {
            return 0;
        }

        return distance / seconds;
    }

    private static double ReadDouble(System.Windows.Controls.TextBox box, double fallback)
    {
        var text = box.Text.Trim().Replace(',', '.');
        return double.TryParse(text, NumberStyles.Float, CultureInfo.InvariantCulture, out var value)
            ? value
            : fallback;
    }

    private static int ReadInt(System.Windows.Controls.TextBox box, int fallback)
    {
        var text = box.Text.Trim().Replace(',', '.');
        return int.TryParse(text, NumberStyles.Integer, CultureInfo.InvariantCulture, out var value)
            ? value
            : fallback;
    }
}
