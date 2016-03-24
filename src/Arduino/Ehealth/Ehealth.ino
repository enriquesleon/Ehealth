#include <eHealth.h>
#include <PinChangeInt.h>

int cont = 0;
double timeValue =0;
int i = 1;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  PCintPort::attachInterrupt(6, readPulsioximeter, RISING);


}

void loop() {
  timeValue = millis(); 
  sendECG(timeValue);
  sendAirflow(timeValue);
  if (i == 1){
    sendBPM(timeValue);
    sendO2S(timeValue);
  }
  
  
  i++;
  i = i%100;
  
  delay(.5);
}
void sendECG(double timeValue){
  String reading = String(eHealth.getECG());
  sendReading("ECG:",reading,timeValue);
}
void sendAirflow(double timeValue){
  String reading = String(eHealth.getAirFlow());
  sendReading("AFS:",reading,timeValue);
}
void sendReading(String sensorType,String reading,double timeValue){
  String line = String(sensorType + timeValue + "," + reading);
  Serial.println(line); 
}
void sendBPM(double timeValue){
  String reading = String(eHealth.getBPM());
  sendReading("BPM:",reading,timeValue);
}
void sendO2S(double timeValue){
  String reading = String(eHealth.getOxygenSaturation());
  sendReading("O2S:",reading,timeValue);
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
