int leftFootPin = 1;
int rightFootPin = 2;
int leftVal = 0;
int rightVal = 0;

void setup() {
  Serial.begin(9600);
}

void loop() {
  leftVal = analogRead(leftFootPin);
  rightVal = analogRead(rightFootPin);
  Serial.print(leftVal);
  Serial.print(",");
  Serial.print(rightVal);
  Serial.println();
  delay(5);
}
 

