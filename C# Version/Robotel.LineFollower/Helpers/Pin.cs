using Robotel.LineFollower.Simulated.Arduino;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Robotel.LineFollower.Helpers
{
    public static class Pin
    {
        public static void SetPinMode(Pins pin, PinMode mode)
        {
            ArduinoApi.pinMode((int)pin, (int)mode);
        }

        public static void On(Pins pin)
        {
            ArduinoApi.digitalWrite((int)pin, (int)PinState.High);
        }
        public static void Off(Pins pin)
        {
            ArduinoApi.digitalWrite((int)pin, (int)PinState.Low);
        }
        public static void DigitalWrite(Pins pin, PinState state)
        {
            ArduinoApi.digitalWrite((int)pin, (int)state);
        }
        public static void DigitalWrite(int pin, PinState state)
        {
            ArduinoApi.digitalWrite(pin, (int)state);
        }
        public static int Citeste(Pins pin)
        {
            return ArduinoApi.digitalRead((int)pin);
        }
        public static int DigitalRead(int pin)
        {
            return ArduinoApi.digitalRead(pin);
        }
    }
}
