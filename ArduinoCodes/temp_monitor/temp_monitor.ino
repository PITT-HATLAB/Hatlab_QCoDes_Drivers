
/**************************************************************************/
/*!
This is a demo for the Adafruit MCP9808 breakout
----> http://www.adafruit.com/products/1782
Adafruit invests time and resources providing this open source code,
please support Adafruit and open-source hardware by purchasing
products from Adafruit!
*/
/**************************************************************************/

#include <Wire.h>            // Used to establish serial communication on the I2C bus
#include <SparkFun_TMP117.h> // Used to send and recieve specific information from our sensor

// The default address of the device is 0x48 = (GND)

byte addresses[4] = {0x48, 0x49, 0x4A, 0x4B};
TMP117 sensors[4];

int incomingByte;

void setup() {
  Wire.begin();
  Serial.begin(115200);    // Start serial communication at 115200 baud
  Wire.setClock(400000);   // Set clock speed to be the fastest for better communication (fast mode)
  
  Serial.print("connected sensors: ");

  for (int i=0; i<4; i++) {
    int addr = addresses[i];

    if (sensors[i].begin(addr) == true) // Function to check if the sensor will correctly self-identify with the proper Device ID/Address
    { 
      Serial.print(1);
    }
    else
    {
      Serial.print(0);
    }
    
    sensors[i].setConversionCycleBit(6);
    sensors[i].setConversionAverageMode(4);
  }

  Serial.println("");
}

void loop() {
  if (Serial.available() > 0) {
    incomingByte = Serial.read();
    if (incomingByte == 'A') {
      for (int i=0; i<4; i++) {
        // Read and print out the temperature
        float c = sensors[i].readTempC();
        if (i < 3 ){
        Serial.print(c, 4);
        Serial.print(',');
        }
        else{
          Serial.println(c, 4);
        }
      }
    }
  }
}
