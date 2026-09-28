using Robotel.LineFollower.Simulated.Arduino;
using Robotel.Utils;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Robotel.LineFollower.Helpers
{
    public static class Engine
    {
        public static void SetSpeed(int leftSpeed, int rightSpeed)
        {
            Serial.write(Constants.CodMotor);
            Serial.write(1);
            Serial.write(Constants.CodViteza);
            Serial.write(leftSpeed);
            Serial.write(Constants.CodMotor);
            Serial.write(2);
            Serial.write(Constants.CodViteza);
            Serial.write(rightSpeed);
        }
    }
}
