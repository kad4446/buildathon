#include <Servo.h>
#include <dht.h>

dht DHT;

#define DHT11_PIN 2

Servo door;
Servo window;

int myValues[5]={0, 0, 0, 0, 0};

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  
  door.attach(9);//door
  window.attach(8);//window
  pinMode(5,OUTPUT);//light
  digitalWrite(5, HIGH);
  //turn on green light
  pinMode(7,OUTPUT); digitalWrite(7, HIGH);
  pinMode(6, OUTPUT);digitalWrite(6, LOW);

}

void loop() {

   //turn on green light
   int doorshut=70;
   int dooropen=180;
   int windowopen=120;
   int windowshut=140;
   int chk=DHT.read11(DHT11_PIN);
   int lightstatus=1;
   int doorstatus=analogRead(A0);
   int windowstatus=analogRead(A1);

  delay(1000);
  //write out to python program- sends windowstatus, doorstatus, lightstatus, temperature, humidity, time
  
  if(windowstatus>=1019){windowstatus=0;} else {windowstatus=1;}
  Serial.print(windowstatus,1);
  Serial.print(",\t");
  
  if(doorstatus<=30){doorstatus=0;}else {doorstatus=1;}
  Serial.print(doorstatus,1);
  Serial.print(",\t");
  
  Serial.print(lightstatus,1);
  Serial.print(",\t");
  
  Serial.print(DHT.temperature,1);
  Serial.print(",\t");
  
  Serial.print(DHT.humidity,1);
  Serial.print("\n");

  
  delay(6000);
  
  //read in from python program
  while (Serial.available()) {
    if (Serial.read() == 'a') {
      for (int i = 0; i < 6; i++) {
        myValues[i] = Serial.read() - 48;
          if (i==0 &&(myValues[i] ==0 || myValues[i]==2)){
            //THEN THESE PEEPS ARE AWAY OR ENERGY EFFICIENT
            //turn fan on
            //analogWrite(3, 50);
  
             //turn yellow light off (THEM WASTERS LEFT THE LIGHTS ON)
            if(i==3 && myValues[i]==1)
              digitalWrite(5,LOW); 
  
             //higher thermostat limit (THEM BITCHES WANT IT COLD, BUT THEY ARENT HERE)
            / /turn on red light 
            if(i==4 && myValues[i]==1)
            {digitalWrite(6,HIGH);
          //turn off green light
          digitalWrite(7,LOW);}
  
          //open door/ window (LETS GET SOME GOOD AIR FLOW, SAVE SOME ENERGY)
          if(i==2 && myValues[i]==0)
          door.write(dooropen);
          if(i==1 && myValues[i]==0)
          window.write(windowopen);
    }
      
      }
      break;
    }
  }
  //put the other while loop to get rid of extra characters
   
  

 
    
  delay(6000);

  //window.write(windowshut); 
  //door.write(doorshut);

}
