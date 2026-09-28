// V11 hysteresis v2: symmetric wheel speeds, no outer-wheel boost.
// All debounce/stability thresholds are in milliseconds (millis).
// prag00Ms: stay on 00 before turn from memory (straight).
// pragLateralMs: stay on 10/01 before writing ultimaDirectie (straight).
// pragStabilMs: stay on 11 to clear linieInstabila.
// pragOscilareMs: max time between 10 and 01 flip to mark unstable line.
// pragCurba: time in turn before esteCurba (hard corner).
#include "Utils/Constants.h"

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
volatile int prag00Ms;
volatile int antiOscilareActiv;
volatile int pragOscilareMs;
volatile int pragStabilMs;
volatile int pragLateralMs;
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
volatile int patternPrev;
volatile int linieInstabila;
volatile int ultimLateral;
volatile long tUltimLateral;
volatile long tStart00;
volatile long tStartLateral;
volatile long tStartStabil11;


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
  prag00Ms = 8;
  antiOscilareActiv = 1;
  pragOscilareMs = 120;
  pragStabilMs = 80;
  pragLateralMs = 0;
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
  patternPrev = -1;
  linieInstabila = 0;
  ultimLateral = 0;
  tUltimLateral = 0;
  tStart00 = 0;
  tStartLateral = 0;
  tStartStabil11 = 0;
  
  pinMode(Constants::PinSenzorStanga, INPUT);
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
      int patternAcum;
      if (senzorStanga == 1 && senzorDreapta == 1) {
        patternAcum = 3;
      } else if (senzorStanga == 1 && senzorDreapta == 0) {
        patternAcum = 2;
      } else if (senzorStanga == 0 && senzorDreapta == 1) {
        patternAcum = 1;
      } else {
        patternAcum = 0;
      }

      if (patternAcum == 3) {
        if (patternPrev != 3) {
          tStartStabil11 = millis();
        }
        if (antiOscilareActiv == 1 && (millis() - tStartStabil11) >= pragStabilMs) {
          linieInstabila = 0;
        }
        ultimLateral = 0;
        stare = 0;
        ultimaDirectie = 0;
        esteCurba = 0;
        ignoraSenzor = 0;
      } else if (patternAcum == 2) {
        if (patternPrev != 2) {
          tStartLateral = millis();
        }
        if (antiOscilareActiv == 1) {
          if (ultimLateral == 2 && (millis() - tUltimLateral) <= pragOscilareMs) {
            linieInstabila = 1;
          }
          ultimLateral = 1;
          tUltimLateral = millis();
        }

        if (ignoraSenzor == 1) {
          stare = 0;
        } else if (stare != 0 && ultimaDirectie == 1) {
          stare = 0;
          ultimaDirectie = 0;
          esteCurba = 0;
          ignoraSenzor = 1;
        } else if (stare == 0) {
          if (linieInstabila == 0 && (millis() - tStartLateral) >= pragLateralMs) {
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
      } else if (patternAcum == 1) {
        if (patternPrev != 1) {
          tStartLateral = millis();
        }
        if (antiOscilareActiv == 1) {
          if (ultimLateral == 1 && (millis() - tUltimLateral) <= pragOscilareMs) {
            linieInstabila = 1;
          }
          ultimLateral = 2;
          tUltimLateral = millis();
        }

        if (ignoraSenzor == 2) {
          stare = 0;
        } else if (stare != 0 && ultimaDirectie == -1) {
          stare = 0;
          ultimaDirectie = 0;
          esteCurba = 0;
          ignoraSenzor = 2;
        } else if (stare == 0) {
          if (linieInstabila == 0 && (millis() - tStartLateral) >= pragLateralMs) {
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
        if (patternPrev != 0) {
          tStart00 = millis();
        }
        ignoraSenzor = 0;

        if (linieInstabila == 1) {
          stare = 0;
        } else if (ultimaDirectie != 0) {
          if (stare != 0) {
            if ((millis() - tStartViraj) >= pragCurba) {
              esteCurba = 1;
            }
            stare = ultimaDirectie;
          } else if ((millis() - tStart00) >= prag00Ms) {
            if (stare == 0) {
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

      patternPrev = patternAcum;

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
