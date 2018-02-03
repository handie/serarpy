void setup() {
  // start serial port at 9600 bps:
  Serial.begin(9600);
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
  }
  
  pinMode(2, INPUT_PULLUP);
  pinMode(3, INPUT_PULLUP);
  pinMode(4, INPUT_PULLUP);
  pinMode(5, INPUT_PULLUP);
  pinMode(6, INPUT_PULLUP);
  pinMode(7, INPUT_PULLUP);
  pinMode(8, INPUT_PULLUP);
  
}

void loop() {
  int sensorVal = 0;
  int i;
  byte b1 = 0x80;
  i = 0;
  while( i < 8 ){
    sensorVal = digitalRead(i+2);
    if (sensorVal == HIGH) {
      bitClear(b1,i);
    } else {
      bitSet(b1,i);
    }  
    i = i + 1;
  }
  Serial.write(b1);
  Serial.write(0x80);
  Serial.write(0x80);
  Serial.write(0x80);
  Serial.write(0x0A);
  delay(100);
}
