
#include <Adafruit_MCP2515.h>
#define MCP_PIN 10
#define CAN_BAUDRATE (250000)

#define J1X A0
#define J1Y A1
#define J2X A2
#define J2Y A3
#define CAM_PIN A4
#define TOR_PIN 2
#define MIN_VALUE 1050
#define MAX_VALUE 1950
#define SMOOTH 0.2

Adafruit_MCP2515 mcp(MCP_PIN);

uint8_t buffer[8];

float ux, uy, uz, yaw;
int camAngle;
bool torpedo;

// Thruster Values
int FLValue = 1500;
int FRValue = 1500;  
int BLValue = 1500;
int BRValue = 1500;    
int ULValue = 1500;
int URValue = 1500;
int prevFLValue = 1500;
int prevFRValue = 1500;  
int prevBLValue = 1500;
int prevBRValue = 1500;    
int prevULValue = 1500;
int prevURValue = 1500;                        

// need for transformation
float ix = 2*sqrt(2);
float iy = 2*sqrt(2);
float jx = -2*sqrt(2);
float jy = 2*sqrt(2);


void setup() {

  pinMode(J1X, INPUT);
  pinMode(J1Y, INPUT);
  pinMode(J2X, INPUT);
  pinMode(J2Y, INPUT);
  pinMode(CAM_PIN, INPUT);
  pinMode(TOR_PIN, INPUT);

  Serial.begin(115200);
  while(!Serial) delay(10);

  Serial.println("IFLE3 - MCP2515 CAN BUS COMPRESSED INT SENDER AND RECIEVER");

  if (!mcp.begin(CAN_BAUDRATE)) {
    Serial.println("Error initializing MCP2515.");
    while(1) delay(10);
  }

  Serial.println("MCP2515 chip found");

}

void sendPacket() {

  while (Serial.available()) {
    
    int values[6] = {FLValue, FRValue, BLValue, BRValue, ULValue, URValue};
    
    // 1023 => 1020 olarak iletilir, tek pakette 8 motor verisi göndermek için son basamaktan feragat edilir, bknz. Lossy Compression.

    for(uint8_t i = 0; i < 6; i++){
      uint8_t compressedValue = (values[i] / 10) - 100;
      buffer[i] = compressedValue;
    }

    buffer[6] = camAngle;
    buffer[7] = torpedo;

    mcp.beginPacket(0x13);
    mcp.write(buffer, sizeof(buffer));
    mcp.endPacket();

  }

}

void convertMotorValues() {

  prevFLValue = FLValue;
  prevFRValue = FRValue;
  prevBLValue = BLValue;
  prevBRValue = BRValue;
  prevULValue = ULValue;
  prevURValue = URValue;

  FLValue = 1500;
  FRValue = 1500;
  BLValue = 1500;
  BRValue = 1500;
  ULValue = 1500;
  URValue = 1500;

  FLValue += 500 * (ux * jx + uy * jy);
  FRValue += 500 * (ux * ix + uy * iy);
  BLValue -= 500 * (ux * ix + uy * iy);
  BRValue -= 500 * (ux * jx + uy * jy);

  FLValue += 500 * yaw;
  FRValue -= 500 * yaw;
  BLValue -= 500 * yaw;
  BRValue += 500 * yaw;

  ULValue += 500 * uz;
  URValue += 500 * uz;

  FLValue = constrain(SMOOTH*prevFLValue + (1-SMOOTH)*FLValue, MIN_VALUE, MAX_VALUE);
  FRValue = constrain(SMOOTH*prevFRValue + (1-SMOOTH)*FRValue, MIN_VALUE, MAX_VALUE);
  BLValue = constrain(SMOOTH*prevBLValue + (1-SMOOTH)*BLValue, MIN_VALUE, MAX_VALUE);
  BRValue = constrain(SMOOTH*prevBRValue + (1-SMOOTH)*BRValue, MIN_VALUE, MAX_VALUE);
  ULValue = constrain(SMOOTH*prevULValue + (1-SMOOTH)*ULValue, MIN_VALUE, MAX_VALUE);
  URValue = constrain(SMOOTH*prevURValue + (1-SMOOTH)*URValue, MIN_VALUE, MAX_VALUE);

}

void loop() {
  
  camAngle = analogRead(CAM_PIN);
  torpedo = digitalRead(TOR_PIN);

  ux  = map(analogRead(J1X), 0, 1023, -1, 1); 
  uy  = map(analogRead(J1Y), 0, 1023, -1, 1); 
  yaw = map(analogRead(J2X), 0, 1023, -1, 1); 
  uz  = map(analogRead(J2Y), 0, 1023, -1, 1); 
  
  convertMotorValues();
  sendPacket();

}



