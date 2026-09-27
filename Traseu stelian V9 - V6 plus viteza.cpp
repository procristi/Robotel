// Same sensor/motor logic as V6. Speeds only: vitezaMare 100, vitezaMica 55,
// compensareStanga 25. 11 = forward. Opposite sensor ends the turn.

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

void setup() {
  ServiceMode = 0;
  CodMotor = 254;
  codViteza = 240;
  senzorStanga = 0;
  senzorDreapta = 0;
  vitezaMica = 55;
  vitezaMare = 100;
  compensareStanga = 25;
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

  pinMode(9, INPUT);
  pinMode(3, INPUT);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  Serial.begin(9600);

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

    if (ServiceMode == 0) {
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
