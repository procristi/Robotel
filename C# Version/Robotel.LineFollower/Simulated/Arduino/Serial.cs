namespace Robotel.LineFollower.Simulated.Arduino;

/// <summary>
/// Arduino Serial stubs for authoring (Mixly: serial write / begin blocks).
/// </summary>
public static class Serial
{
    public static void begin(int baudRate)
    {
        _ = baudRate;
    }

    public static void write(byte value)
    {
    }

    public static void write(int value) => write((byte)value);
}
