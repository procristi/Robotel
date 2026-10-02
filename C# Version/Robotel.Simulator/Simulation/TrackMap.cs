using System.Windows.Media;
using System.Windows.Media.Imaging;

namespace Robotel.Simulator.Simulation;

/// <summary>
/// Black line on a white photo. Scale comes from the real width of that line.
/// </summary>
public sealed class TrackMap
{
    private readonly byte[] _luminance;
    private readonly int _stride;

    public TrackMap(string path, byte darknessThreshold)
    {
        var frame = BitmapFrame.Create(new Uri(path), BitmapCreateOptions.PreservePixelFormat, BitmapCacheOption.OnLoad);
        var converted = new FormatConvertedBitmap(frame, PixelFormats.Bgra32, null, 0);
        Width = converted.PixelWidth;
        Height = converted.PixelHeight;
        _stride = Width * 4;
        var pixels = new byte[_stride * Height];
        converted.CopyPixels(pixels, _stride, 0);
        _luminance = new byte[Width * Height];
        for (var i = 0; i < _luminance.Length; i++)
        {
            var p = i * 4;
            _luminance[i] = (byte)((pixels[p] + pixels[p + 1] + pixels[p + 2]) / 3);
        }

        DarknessThreshold = darknessThreshold;
        // One image pixel occupies one layout unit, so a sensor sample lands on the pixel under the drawn rectangle.
        Source = BitmapSource.Create(Width, Height, 96, 96, PixelFormats.Bgra32, null, pixels, _stride);
        Source.Freeze();
    }

    public int Width { get; }
    public int Height { get; }
    public byte DarknessThreshold { get; set; }
    public BitmapSource Source { get; }

    public bool IsInside(int x, int y)
    {
        return x >= 0 && y >= 0 && x < Width && y < Height;
    }

    public bool IsBlack(int x, int y)
    {
        if (!IsInside(x, y))
        {
            return false;
        }

        return _luminance[(y * Width) + x] <= DarknessThreshold;
    }

    /// <summary>
    /// Typical stroke width in pixels. Axis-aligned runs dominate the median, so a diagonal segment does not set the scale.
    /// </summary>
    public int EstimateLineWidthPixels()
    {
        var samples = new List<int>();
        for (var y = 0; y < Height; y += 3)
        {
            for (var x = 0; x < Width; x += 3)
            {
                if (!IsBlack(x, y))
                {
                    continue;
                }

                var horizontal = RunLength(x, y, 1, 0);
                var vertical = RunLength(x, y, 0, 1);
                var width = Math.Min(horizontal, vertical);
                if (width is > 0 and < 200)
                {
                    samples.Add(width);
                }
            }
        }

        if (samples.Count == 0)
        {
            return 1;
        }

        samples.Sort();
        return samples[samples.Count / 2];
    }

    private int RunLength(int x, int y, int stepX, int stepY)
    {
        var count = 1;
        var forward = 1;
        while (IsBlack(x + (stepX * forward), y + (stepY * forward)))
        {
            count++;
            forward++;
        }

        var backward = 1;
        while (IsBlack(x - (stepX * backward), y - (stepY * backward)))
        {
            count++;
            backward++;
        }

        return count;
    }
}
