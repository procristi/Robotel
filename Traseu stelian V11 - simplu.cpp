// Straight on 11, normal left on 10, normal right on 01, sharp left on 00.
// Headlights follow the sensors from boot. Motors stay stopped until pin 7
// is pressed and durataPornire has elapsed. A new motor command is sent only
// when the sensor case changes.

volatile byte CodMotor;
volatile byte codViteza;
volatile int senzorStanga;
volatile int senzorDreapta;
volatile byte vitezaMica;
volatile byte vitezaMare;
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
  vitezaMare = 240;
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
      if (senzorStanga == 1 && senzorDreapta == 1) {
        comanda = 0;
        motorStanga = vitezaMare;
        motorDreapta = vitezaMare;
      } else if (senzorStanga == 1 && senzorDreapta == 0) {
        comanda = 1;
        motorStanga = vitezaMica;
        motorDreapta = vitezaMare;
      } else if (senzorStanga == 0 && senzorDreapta == 1) {
        comanda = 2;
        motorStanga = vitezaMare;
        motorDreapta = vitezaMica;
      } else {
        comanda = 3;
        motorStanga = 0;
        motorDreapta = vitezaMare;
      }

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
    }
  }
}

void loop() {
}
