// Authoring-only C# sketch — copy logic into Mixly (blocks map 1:1 to calls below).
//
// Mixly                          | C# / Arduino
// -------------------------------|----------------------------------
// variable (global)              | static fields on sketch class
// Arduino run first (setup)      | void setup() { ... }
// repeat while true (in setup)   | while (true) { ... }
// loop (often empty)             | void loop() { }
// set pin mode                   | pinMode(pin, INPUT|OUTPUT)
// read / write digital           | digitalRead / digitalWrite(pin, LOW|HIGH)
// serial begin                   | Serial.begin(9600)
// serial write number            | Serial.write(n)
// if / else                      | if / else
// compare numbers                | ==, !=, &lt;, &gt;, &gt;=, &lt;=
// math                           | +, -, *, etc.
// millis / time difference       | millis(), (millis() - t0) >= pragMs
//
// Example:
//   pinMode(3, INPUT);
//   Serial.write(Constants.CodMotor);
//   while (true) {
//     digitalWrite(5, LOW);
//   }

namespace Robotel.LineFollower.Simulated.Arduino;

internal static class ArduinoUsageExample
{
}
