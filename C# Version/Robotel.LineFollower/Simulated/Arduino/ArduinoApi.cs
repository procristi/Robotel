namespace Robotel.LineFollower.Simulated.Arduino;

/// <summary>
/// Arduino-style API stubs for authoring only (translate to Mixly blocks; not executed on PC).
/// Global using: static Robotel.LineFollower.Simulated.Arduino.ArduinoApi
/// </summary>
public static class ArduinoApi
{
    public const int INPUT = ArduinoDefs.INPUT;
    public const int OUTPUT = ArduinoDefs.OUTPUT;
    public const int LOW = ArduinoDefs.LOW;
    public const int HIGH = ArduinoDefs.HIGH;

    public static void pinMode(int pin, int mode)
    {
    }

    public static int digitalRead(int pin) => 0;

    public static void digitalWrite(int pin, int value)
    {
    }

    // Clock advanced by the track simulator. Stays at 0 while authoring the sketch.
    public static long TimpSimulat { get; set; }

    public static long millis() => TimpSimulat;
}
