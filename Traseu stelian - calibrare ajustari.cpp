// Straight-line motor compensation test. Sensors are not read.
// Pin 7 is a momentary button. Pressed value is butonApasat (1 on this board).
// After press then release, left/right stay forward: 4 s at vitezaMica with
// compensareStangaMica, then 4 s at vitezaMare with compensareStangaMare, repeat.
// LED 6 on = low-speed phase. Both LEDs on = high-speed phase.

volatile byte CodMotor;
volatile byte codViteza;
volatile byte vitezaMica;
volatile byte vitezaMare;
volatile int compensareStangaMica;
volatile int compensareStangaMare;
volatile int durataFaza;
volatile int butonApasat;
volatile int buton;
volatile int faza;
volatile long tStartFaza;
volatile int fazaTrimisa;
volatile int motorStanga;
volatile int motorDreapta;

void setup() {
  CodMotor = 254;
  codViteza = 240;
  vitezaMica = 40;
  vitezaMare = 100;
  compensareStangaMica = 6;
  compensareStangaMare = 8;
  durataFaza = 4000;
  butonApasat = 1;
  buton = 0;
  faza = 0;
  tStartFaza = 0;
  fazaTrimisa = 99;
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
  tStartFaza = millis();

  while (true) {
    if ((millis() - tStartFaza) >= durataFaza) {
      tStartFaza = millis();
      if (faza == 0) {
        faza = 1;
      } else {
        faza = 0;
      }
    }

    if (faza == 0) {
      motorStanga = vitezaMica + compensareStangaMica;
      motorDreapta = vitezaMica;
      digitalWrite(6, HIGH);
      digitalWrite(5, LOW);
    } else {
      motorStanga = vitezaMare + compensareStangaMare;
      motorDreapta = vitezaMare;
      digitalWrite(6, HIGH);
      digitalWrite(5, HIGH);
    }

    if (faza != fazaTrimisa) {
      fazaTrimisa = faza;
      Serial.write(CodMotor);
      Serial.write(1);
      Serial.write(codViteza);
      Serial.write(motorStanga);
      Serial.write(CodMotor);
      Serial.write(2);
      Serial.write(codViteza);
      Serial.write(motorDreapta);
    }
  }
}

void loop() {
}
