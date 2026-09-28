using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Robotel.LineFollower.Helpers
{
    public enum PinMode
    {
        Input = 0,
        Output = 1
    }
    public enum PinState
    {
        Low = 0,
        High = 1
    }
    public enum Pins
    {
        BecStanga = 6,
        BecDreapta = 5,
        SenzorStanga = 9,
        SenzorDreapta = 3,
        Buton = 7
    }
}
