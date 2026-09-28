// V11 hysteresis v2: symmetric wheel speeds, no outer-wheel boost.
// Straight: both vitezaMare (left optional compensareDrept at high speed).
// Soft turn: (vitezaMica+compensareVitMica)/vitezaMare left, (vitezaMare+compensareVitMare)/vitezaMica right.
// Hard turn (esteCurba): 0/vitezaMare left, (vitezaMare+compensareVitMare)/0 right.
// Enter turn on 00 from memory only after pragCitiri00 consecutive 00 reads (while straight).
// Optional anti-oscillation: force straight while 10/01 flip faster than pragOscilareMs;
// clear unstable after pragStabilCitiri consecutive 11 reads.

volatile int ServiceMode;
volatile byte CodMotor;
volatile byte codViteza;
volatile int senzorStanga;
volatile int senzorDreapta;
volatile byte vitezaMica;
volatile byte vitezaMare;
volatile int compensareDrept;
volatile int compensareVitMica;
volatile int compensareVitMare;
volatile int pragCurba;
volatile int pragCitiri00;
volatile int antiOscilareActiv;
volatile int pragOscilareMs;
volatile int pragStabilCitiri;
volatile int pragCitiriLateral;
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
volatile int contor00;
volatile int contorLateral;
volatile int patternLateral;
volatile int linieInstabila;
volatile int contorStabil11;
volatile int ultimLateral;
volatile long tUltimLateral;

void setup() {
  ServiceMode = 0;
  CodMotor = 254;
  codViteza = 240;
  senzorStanga = 0;
  senzorDreapta = 0;
  vitezaMica = 40;
  vitezaMare = 240;
  compensareDrept = 0;
  compensareVitMica = 0;
  compensareVitMare = 0;
  pragCurba = 70;
  pragCitiri00 = 3;
  antiOscilareActiv = 1;
  pragOscilareMs = 120;
  pragStabilCitiri = 4;
  pragCitiriLateral = 1;
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
  contor00 = 0;
  contorLateral = 0;
  patternLateral = 0;
  linieInstabila = 0;
  contorStabil11 = 0;
  ultimLateral = 0;
  tUltimLateral = 0;

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
        contor00 = 0;
        contorStabil11 = contorStabil11 + 1;
        if (antiOscilareActiv == 1 && contorStabil11 >= pragStabilCitiri) {
          linieInstabila = 0;
        }
        ultimLateral = 0;
        contorLateral = 0;
        patternLateral = 0;
        stare = 0;
        ultimaDirectie = 0;
        esteCurba = 0;
        ignoraSenzor = 0;
      } else {
        contorStabil11 = 0;

        if (senzorStanga == 1 && senzorDreapta == 0) {
          contor00 = 0;
          if (antiOscilareActiv == 1) {
            if (ultimLateral == 2 && (millis() - tUltimLateral) <= pragOscilareMs) {
              linieInstabila = 1;
            }
            ultimLateral = 1;
            tUltimLateral = millis();
          }
          if (patternLateral != 1) {
            patternLateral = 1;
            contorLateral = 1;
          } else {
            contorLateral = contorLateral + 1;
          }

          if (ignoraSenzor == 1) {
            stare = 0;
          } else if (stare != 0 && ultimaDirectie == 1) {
            stare = 0;
            ultimaDirectie = 0;
            esteCurba = 0;
            ignoraSenzor = 1;
          } else if (stare == 0) {
            if (linieInstabila == 0 && contorLateral >= pragCitiriLateral) {
              ultimaDirectie = -1;
            }
            stare = 0;
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
          contor00 = 0;
          if (antiOscilareActiv == 1) {
            if (ultimLateral == 1 && (millis() - tUltimLateral) <= pragOscilareMs) {
              linieInstabila = 1;
            }
            ultimLateral = 2;
            tUltimLateral = millis();
          }
          if (patternLateral != 2) {
            patternLateral = 2;
            contorLateral = 1;
          } else {
            contorLateral = contorLateral + 1;
          }

          if (ignoraSenzor == 2) {
            stare = 0;
          } else if (stare != 0 && ultimaDirectie == -1) {
            stare = 0;
            ultimaDirectie = 0;
            esteCurba = 0;
            ignoraSenzor = 2;
          } else if (stare == 0) {
            if (linieInstabila == 0 && contorLateral >= pragCitiriLateral) {
              ultimaDirectie = 1;
            }
            stare = 0;
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
          contor00 = contor00 + 1;
          ignoraSenzor = 0;
          patternLateral = 0;
          contorLateral = 0;

          if (linieInstabila == 1) {
            stare = 0;
          } else if (ultimaDirectie != 0) {
            if (stare != 0) {
              if ((millis() - tStartViraj) >= pragCurba) {
                esteCurba = 1;
              }
              stare = ultimaDirectie;
            } else if (contor00 >= pragCitiri00) {
              if (contor00 == pragCitiri00) {
                tStartViraj = millis();
                esteCurba = 0;
              }
              if ((millis() - tStartViraj) >= pragCurba) {
                esteCurba = 1;
              }
              stare = ultimaDirectie;
            } else {
              stare = 0;
            }
          } else {
            stare = 0;
          }
        }
      }

      if (linieInstabila == 1 && stare != 0) {
        stare = 0;
        esteCurba = 0;
      }

      if (stare == 0) {
        motorStanga = vitezaMare + compensareDrept;
        motorDreapta = vitezaMare;
      } else if (stare == -1) {
        if (esteCurba == 1) {
          motorStanga = 0;
          motorDreapta = vitezaMare;
        } else {
          motorStanga = vitezaMica + compensareVitMica;
          motorDreapta = vitezaMare;
        }
      } else {
        if (esteCurba == 1) {
          motorStanga = vitezaMare + compensareVitMare;
          motorDreapta = 0;
        } else {
          motorStanga = vitezaMare + compensareVitMare;
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
