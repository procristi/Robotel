volatile int ServiceMode;

volatile byte CodMotor;

volatile byte codViteza;

volatile byte inapoi;

volatile int stare;

volatile int senzorStanga;

volatile int senzorDreapta;

volatile byte vitezaMica;

volatile byte vitezaMare;

volatile int ajustareRotatie;



void setup(){

  ServiceMode = 0;

  CodMotor = 254;

  codViteza = 240;

  inapoi = 186;

  stare = 0;

  senzorStanga = 0;

  senzorDreapta = 0;

  vitezaMica = 0;

  vitezaMare = 80;

  ajustareRotatie = 0;

  pinMode(9, INPUT);

  pinMode(3, INPUT);

  pinMode(5, OUTPUT);

  pinMode(6, OUTPUT);

  Serial.begin(9600);

  pinMode(3, INPUT);

  pinMode(9, INPUT);

  pinMode(5, OUTPUT);

  pinMode(6, OUTPUT);

  while (true) {

    senzorStanga = digitalRead(9);

    senzorDreapta = digitalRead(3);

    if (senzorDreapta == 1) {

      digitalWrite(5,HIGH);



    } else {

      digitalWrite(5,LOW);



    }

    if (senzorStanga == 1) {

      digitalWrite(6,HIGH);



    } else {

      digitalWrite(6,LOW);



    }

    if (senzorStanga == 1 && senzorDreapta == 1) {

      stare = -1;



    }

    if (senzorStanga == 0 && senzorDreapta == 1) {

      stare = 1;



    }

    if (senzorStanga == 1 && senzorDreapta == 0) {

      stare = -1;



    }

    if (ServiceMode == 0) {

      switch (stare) {

       case 1:

        Serial.write(CodMotor);

        Serial.write(1);

        Serial.write(codViteza);

        Serial.write(((vitezaMare + 0) + ajustareRotatie));

        Serial.write(CodMotor);

        Serial.write(2);

        Serial.write(codViteza);

        Serial.write(vitezaMica);

        break;

       case -1:

        Serial.write(CodMotor);

        Serial.write(1);

        Serial.write(codViteza);

        Serial.write((vitezaMica + 15));

        Serial.write(CodMotor);

        Serial.write(2);

        Serial.write(codViteza);

        Serial.write((vitezaMare + ajustareRotatie));

        break;

       default:

        Serial.write(CodMotor);

        Serial.write(1);

        Serial.write(codViteza);

        Serial.write((vitezaMare + 19));

        Serial.write(CodMotor);

        Serial.write(2);

        Serial.write(codViteza);

        Serial.write(vitezaMare);

        break;

      }



    }

  }

}



void loop(){

  pinMode(A3, OUTPUT);



  if (senzorStanga == 1) {

    if (senzorDreapta == 1) {

      stare = -1;



    } else {

      stare = -1;



    }



  } else if (senzorDreapta == 1) {

    if (senzorDreapta == 1) {

      stare = 1;



    } else {

      stare = 0;



    }

  }



}