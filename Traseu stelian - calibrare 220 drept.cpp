// Straight run at a fixed speed. Sensors are not read.
// Pin 7 momentary button. Pressed value is butonApasat (1 on this board).
// After press then release, both wheels go forward at viteza with
// compensareStanga on the left and stay there.

volatile byte CodMotor;
volatile byte codViteza;
volatile byte viteza;
volatile int compensareStanga;
volatile int butonApasat;
volatile int buton;
volatile int motorStanga;
volatile int motorDreapta;

void setup() {
  CodMotor = 254;
  codViteza = 240;
  viteza = 220;
  compensareStanga = 0;
  butonApasat = 1;
  buton = 0;
  motorStanga = 0;
  motorDreapta = 0;

  pinMode(7, INPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  Serial.begin(9600);

  Serial.write(CodMotor);
  Serial.write(1);
  Serial.write(codViteza);
  Serial.write(0);
  Serial.write(CodMotor);
  Serial.write(2);
  Serial.write(codViteza);
  Serial.write(0);

  digitalWrite(6, HIGH);
  digitalWrite(5, LOW);
  while (true) {
    buton = digitalRead(7);
    if (buton == butonApasat) {
      break;
    }
    delay(20);
  }

  digitalWrite(5, HIGH);
  while (true) {
    buton = digitalRead(7);
    if (buton != butonApasat) {
      break;
    }
    delay(20);
  }
  delay(200);

  motorStanga = viteza + compensareStanga;
  motorDreapta = viteza;
  digitalWrite(6, HIGH);
  digitalWrite(5, HIGH);
  Serial.write(CodMotor);
  Serial.write(1);
  Serial.write(codViteza);
  Serial.write(motorStanga);
  Serial.write(CodMotor);
  Serial.write(2);
  Serial.write(codViteza);
  Serial.write(motorDreapta);

  while (true) {
  }
}

void loop() {
}
