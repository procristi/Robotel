// V11 follow rules. 11 goes straight. 10/01 use the V6 turn rules.
// 00 keeps ultimaDirectie. Sensors and LEDs run from power-on.
// Motors stay at 0 until pin 7 shows a press edge, then durataPornire ms later.
// Pin 7 momentary button. Pressed value is butonApasat (1 on this board).
// butonPrev 99 skips the first sample so a held or floating pin at boot is not a press.

volatile int ServiceMode;
volatile byte CodMotor;
volatile byte codViteza;
volatile int senzorStanga;
volatile int senzorDreapta;
volatile byte vitezaMica;
volatile byte vitezaMare;
volatile int compensareStanga;
volatile int pragCurba;
volatile int stare;
volatile int ultimaDirectie;
volatile int esteCurba;
volatile long tStartViraj;
volatile int ignoraSenzor;
volatile int stareMotor;
volatile int curbaTrimisa;
volatile int motorStanga;
volatile int motorDreapta;
volatile int butonApasat;
volatile int buton;
volatile int pornit;
volatile int butonFaza;
volatile int durataPornire;
volatile long tStartButon;
volatile int butonPrev;

void setup() {
  ServiceMode = 0;
  CodMotor = 254;
  codViteza = 240;
  senzorStanga = 0;
  senzorDreapta = 0;
  vitezaMica = 40;
  vitezaMare = 180;
  compensareStanga = 0;
  pragCurba = 70;
  stare = 0;
  ultimaDirectie = 0;
  esteCurba = 0;
  tStartViraj = 0;
  ignoraSenzor = 0;
  stareMotor = 99;
  curbaTrimisa = 99;
  motorStanga = 0;
  motorDreapta = 0;
  butonApasat = 1;
  buton = 0;
  pornit = 0;
  butonFaza = 0;
  durataPornire = 2000;
  tStartButon = 0;
  butonPrev = 99;

  pinMode(9, INPUT);
  pinMode(3, INPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  pinMode(7, INPUT);
  Serial.begin(9600);

  Serial.write(CodMotor);
  Serial.write(1);
  Serial.write(codViteza);
  Serial.write(0);
  Serial.write(CodMotor);
  Serial.write(2);
  Serial.write(codViteza);
  Serial.write(0);

  while (true) {
    senzorStanga = digitalRead(9);
    senzorDreapta = digitalRead(3);

    if (senzorDreapta == 1) {
      digitalWrite(5, HIGH);
    } else {
      digitalWrite(5, LOW);
    }
    if (senzorStanga == 1) {
      digitalWrite(6, HIGH);
    } else {
      digitalWrite(6, LOW);
    }

    buton = digitalRead(7);
    if (pornit == 0) {
      if (butonPrev == 99) {
        butonPrev = buton;
      } else {
        if (butonPrev != butonApasat && buton == butonApasat) {
          tStartButon = millis();
          butonFaza = 1;
        }
        butonPrev = buton;
      }
      if (butonFaza == 1) {
        if ((millis() - tStartButon) >= durataPornire) {
          pornit = 1;
        }
      }
    } else if (ServiceMode == 0) {
      if (senzorStanga == 1 && senzorDreapta == 1) {
        stare = 0;
        ultimaDirectie = 0;
        esteCurba = 0;
        ignoraSenzor = 0;
      } else if (senzorStanga == 1 && senzorDreapta == 0) {
        if (ignoraSenzor == 1) {
          stare = 0;
        } else if (ultimaDirectie == 1) {
          stare = 0;
          ultimaDirectie = 0;
          esteCurba = 0;
          ignoraSenzor = 1;
        } else {
          if (ultimaDirectie != -1) {
            tStartViraj = millis();
            esteCurba = 0;
          }
          ultimaDirectie = -1;
          if ((millis() - tStartViraj) >= pragCurba) {
            esteCurba = 1;
          }
          stare = -1;
        }
      } else if (senzorStanga == 0 && senzorDreapta == 1) {
        if (ignoraSenzor == 2) {
          stare = 0;
        } else if (ultimaDirectie == -1) {
          stare = 0;
          ultimaDirectie = 0;
          esteCurba = 0;
          ignoraSenzor = 2;
        } else {
          if (ultimaDirectie != 1) {
            tStartViraj = millis();
            esteCurba = 0;
          }
          ultimaDirectie = 1;
          if ((millis() - tStartViraj) >= pragCurba) {
            esteCurba = 1;
          }
          stare = 1;
        }
      } else {
        ignoraSenzor = 0;
        if (ultimaDirectie != 0) {
          if ((millis() - tStartViraj) >= pragCurba) {
            esteCurba = 1;
          }
          stare = ultimaDirectie;
        } else {
          stare = 0;
        }
      }

      if (stare == 0) {
        motorStanga = vitezaMare + compensareStanga;
        motorDreapta = vitezaMare;
      } else if (stare == -1) {
        if (esteCurba == 1) {
          motorStanga = 0;
          motorDreapta = vitezaMare + 10;
        } else {
          motorStanga = vitezaMica;
          motorDreapta = vitezaMare;
        }
      } else {
        if (esteCurba == 1) {
          motorStanga = vitezaMare + compensareStanga + 15;
          motorDreapta = 0;
        } else {
          motorStanga = vitezaMare + compensareStanga;
          motorDreapta = vitezaMica;
        }
      }

      if (stare != stareMotor || esteCurba != curbaTrimisa) {
        stareMotor = stare;
        curbaTrimisa = esteCurba;
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
}

void loop() {
}
