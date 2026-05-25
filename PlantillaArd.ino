const int numSensores = 5;
int pines[numSensores] = {A0, A1, A2, A3, A4};

void setup() {
  Serial.begin(115200); // BAUD debe coincidir con Python
}

void loop() {
  for (int i = 0; i < numSensores; i++) {
    int valorADC = analogRead(pines[i]);
    Serial.print(valorADC);
    if (i < numSensores - 1) Serial.print(","); // separador
  }
  Serial.println(); // fin de línea
  delay(100);       // ajusta la frecuencia de muestreo
}