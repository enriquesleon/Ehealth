#include <eHealth.h>
#include <PinChangeInt.h>

int cont = 0;
unsigned long ntimeValue =0;
unsigned long ctimeValue =0;
int i = 1;
unsigned int baud = 9600;
const char cts = 'o';
char buf[64];
unsigned int time_d =100;
boolean connection_open = false;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(baud);
  PCintPort::attachInterrupt(6, readPulsioximeter, RISING);


}

void loop() {

  /*while(!connection_open){
    boolean connection_status = handshake();
    if (connection_status){
      connection_open = true;
    }
  }*/
  ctimeValue = millis();
  if((ctimeValue/time_d) != (ntimeValue/time_d)){
      Serial.print(String(ctimeValue));
      Serial.print(ecg());
      Serial.print(airflow());
      Serial.print(bpm());
      Serial.print(O2S());
      Serial.print('\n');
  }
  ntimeValue = ctimeValue;
}

String ecg(){
  return "+ECG:"+ String(eHealth.getECG());
}
String airflow(){
  return "+AFS:" + String(eHealth.getAirFlow());
}
String bpm(){
  return "+BPM:"+String(eHealth.getBPM());
}
String O2S(){
  return "+O2S:" + String(eHealth.getOxygenSaturation());
}
void sendECG(unsigned long timeValue){
  String reading = String(eHealth.getECG());
  sendReading("ECG:",reading,timeValue);
}
void sendAirflow(unsigned long timeValue){
  String reading = String(eHealth.getAirFlow());
  sendReading("AFS:",reading,timeValue);
}
void sendReading(String sensorType,String reading,unsigned long timeValue){
  String line = String(sensorType + timeValue + "," + reading);
  Serial.println(line); 
}
void sendBPM(unsigned long timeValue){
  String reading = String(eHealth.getBPM());
  sendReading("BPM:",reading,timeValue);
}
void sendO2S(unsigned long timeValue){
  String reading = String(eHealth.getOxygenSaturation());
  sendReading("O2S:",reading,timeValue);
}
boolean handshake(){
  Serial.print('c');
  delay(100);
  if (Serial.available() > 0){
    char c = Serial.read();
    if (c == cts){
      return true;
    }
  }
  return false;
 
}
//Include always this code when using the pulsioximeter sensor
//=========================================================================
void readPulsioximeter(){  

  cont ++;

  if (cont == 50) { //Get only of one 50 measures to reduce the latency
    eHealth.readPulsioximeter();  
    cont = 0;
  }
}
