// V12 - senzori LATERALI (de o parte si de alta a liniei), cu memorie.
// Senzori: pin 9 stanga, pin 3 dreapta. 1 = negru (linie), 0 = alb.
// Montaj: distanta dintre senzori putin mai mare decat latimea liniei,
// deci robot centrat pe linie = 00.
//
// 11 -> linie perpendiculara / intersectie: inainte.
// 10 -> linia e sub senzorul stang: vireaza stanga (bland; dupa pragCurba ms, tare).
// 01 -> linia e sub senzorul drept: vireaza dreapta (bland; dupa pragCurba ms, tare).
// 00 -> are doua sensuri, decise in momentul in care linia iese de sub senzor:
//    DREPT   - linia a stat sub senzor cel putin pragTraversareMs: robotul a
//              apucat sa corecteze si linia a iesit spre interior (centrat);
//    PIERDUT - linia a trecut pe sub senzor mai repede de pragTraversareMs:
//              a "sarit" peste el (de obicei la un colt de 90 grade). Robotul
//              pivoteaza spre partea memorata pana regaseste linia.
// Dupa PIERDUT, urmatorul 00 e mereu DREPT (linia revine din exterior spre centru).
// Daca in PIERDUT o vede senzorul opus, de fapt eram centrati: se corecteaza singur.
// Daca linia nu apare in pragCautareMs, robotul se opreste si asteapta din nou butonul.
//
// mod: 0 DREPT, 1 CORECTIE (bland), 2 CURBA (tare), 3 PIERDUT (cautare), 4 OPRIT
// parte: -1 stanga, 1 dreapta, 0 niciuna (memoria virajului)

volatile byte CodMotor;
volatile byte codViteza;
volatile int senzorStanga;
volatile int senzorDreapta;
volatile byte vitezaMica;
volatile byte vitezaMare;
volatile byte vitezaCautare;
volatile int compensareDrept;
volatile int pragCurba;
volatile int pragTraversareMs;
volatile int pragCautareMs;
volatile int mod;
volatile int parte;
volatile int revenire;
volatile int patternAcum;
volatile int patternPrev;
volatile long tStartLateral;
volatile long tStartPierdut;
volatile int comanda;
volatile int comandaTrimisa;
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
  CodMotor = 254;
  codViteza = 240;
  senzorStanga = 0;
  senzorDreapta = 0;
  vitezaMica = 40;
  vitezaMare = 200;
  vitezaCautare = 160;
  compensareDrept = 0;
  pragCurba = 70;
  pragTraversareMs = 40;
  pragCautareMs = 1500;
  mod = 0;
  parte = 0;
  revenire = 0;
  patternAcum = 0;
  patternPrev = -1;
  tStartLateral = 0;
  tStartPierdut = 0;
  comanda = 0;
  comandaTrimisa = 99;
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
    } else {
      // 1. Combinatia de senzori: 3 = 11, 2 = 10, 1 = 01, 0 = 00
      if (senzorStanga == 1 && senzorDreapta == 1) {
        patternAcum = 3;
      } else if (senzorStanga == 1 && senzorDreapta == 0) {
        patternAcum = 2;
      } else if (senzorStanga == 0 && senzorDreapta == 1) {
        patternAcum = 1;
      } else {
        patternAcum = 0;
      }

      // 2. Decizia
      if (patternAcum == 3) {
        // intersectie / linie perpendiculara: inainte, uita memoria
        mod = 0;
        parte = 0;
        revenire = 0;
      } else if (patternAcum == 2 || patternAcum == 1) {
        if (patternAcum != patternPrev) {
          tStartLateral = millis();
          if (mod == 3) {
            revenire = 1;   // linia revine dupa ce o pierdusem
          } else {
            revenire = 0;
          }
        }
        if (patternAcum == 2) {
          parte = -1;
        } else {
          parte = 1;
        }
        if ((millis() - tStartLateral) >= pragCurba) {
          mod = 2;
        } else {
          mod = 1;
        }
      } else {
        if (patternPrev == 1 || patternPrev == 2) {
          // linia tocmai a iesit de sub senzor: centrat sau pierdut?
          if (revenire == 1) {
            mod = 0;
            revenire = 0;
          } else if ((millis() - tStartLateral) < pragTraversareMs) {
            mod = 3;
            tStartPierdut = millis();
          } else {
            mod = 0;
          }
        } else if (mod == 3) {
          if ((millis() - tStartPierdut) >= pragCautareMs) {
            mod = 4;
          }
        }
      }
      patternPrev = patternAcum;

      // 3. Vitezele rotilor
      if (mod == 0) {
        motorStanga = vitezaMare + compensareDrept;
        motorDreapta = vitezaMare;
      } else if (mod == 1) {
        if (parte == -1) {
          motorStanga = vitezaMica;
          motorDreapta = vitezaMare;
        } else {
          motorStanga = vitezaMare + compensareDrept;
          motorDreapta = vitezaMica;
        }
      } else if (mod == 2) {
        if (parte == -1) {
          motorStanga = 0;
          motorDreapta = vitezaMare;
        } else {
          motorStanga = vitezaMare + compensareDrept;
          motorDreapta = 0;
        }
      } else if (mod == 3) {
        if (parte == -1) {
          motorStanga = 0;
          motorDreapta = vitezaCautare;
        } else {
          motorStanga = vitezaCautare;
          motorDreapta = 0;
        }
      } else {
        motorStanga = 0;
        motorDreapta = 0;
      }

      // 4. Trimite la motoare doar cand s-a schimbat ceva
      comanda = mod * 10 + parte;
      if (comanda != comandaTrimisa) {
        comandaTrimisa = comanda;
        Serial.write(CodMotor);
        Serial.write(1);
        Serial.write(codViteza);
        Serial.write(motorStanga);
        Serial.write(CodMotor);
        Serial.write(2);
        Serial.write(codViteza);
        Serial.write(motorDreapta);
      }

      // 5. OPRIT: asteapta din nou apasarea butonului
      if (mod == 4) {
        pornit = 0;
        butonFaza = 0;
        mod = 0;
        parte = 0;
        revenire = 0;
        patternPrev = -1;
        comandaTrimisa = 99;
      }
    }
  }
}

void loop() {
}
