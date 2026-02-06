/*

  $$$$$$$\                                                  
  $$  __$$\                                                             
  $$ |  $$ | $$$$$$\   $$$$$$\ $$\    $$\  $$$$$$\  $$$$$$$$\  $$$$$$\  
  $$$$$$$  |$$  __$$\ $$  __$$\\$$\  $$  |$$  __$$\ \____$$  |$$  __$$\ 
  $$  ____/ $$ |  \__|$$$$$$$$ |\$$\$$  / $$$$$$$$ |  $$$$ _/ $$$$$$$$ |
  $$ |      $$ |      $$   ____| \$$$  /  $$   ____| $$  _/   $$   ____|
  $$ |      $$ |      \$$$$$$$\   \$  /   \$$$$$$$\ $$$$$$$$\ \$$$$$$$\ 
  \__|      \__|       \_______|   \_/     \_______|\________| \_______|

              - IFLE3 Remote Operating Vehicle (ROV) Project -       

  Project Information

  Last Updated: 2024

  Contributors:
  - Barkın Özsoy
  - Murat Emir Bilgetay
  - Ömer Yapucu
  - Yağız Efe Erdem
  - Yavuz Selim Karahan
  
  Sensors and Modules:
  - Accelerometer and Gyroscope: MPU6050
  - CAN Bus Controller: MCP2515
  - 6 Thruster: M1 Brushless Motor
  - 2 ESC: Racerstar REV35 Special Edition
  - Torpedo Launch Module

*/                                                                   
                

#include <Servo.h>
#include <Adafruit_MCP2515.h>
#include <Adafruit_MPU6050.h>

// Constants
#define CAN_BAUDRATE 250000
#define TORPEDO_LAUNCH_DURATION 100
#define NUMBER_OF_TORPEDOS 3
#define COMM_DEADLINE 1000
#define THRESHOLD 0.07

// Pin definitions
#define FL_PIN 3
#define FR_PIN 4
#define BL_PIN 5
#define BR_PIN 6
#define UL_PIN 7
#define UR_PIN 8
#define CAM_PIN 11
#define TL1_PIN 30
#define TL2_PIN 32
#define TL3_PIN 34
#define TH1_PIN 31
#define TH2_PIN 33
#define TH3_PIN 35
#define NEM_PIN 36
#define MCP_CS_PIN 53

// Object definitions
Adafruit_MCP2515 mcp(MCP_CS_PIN);
Adafruit_MPU6050 mpu;
Servo FL, FR, BL, BR, UL, UR, camServo;

// Variables
float ax, ay, az, gx, gy, gz;           // Accelerometer and gyroscope data
int FLValue, FRValue;                   // Thruster Values
int BLValue, BRValue;
int ULValue, URValue;
int camAngle;
int currentTorpedo;
bool launch = false;                    // Torpedo launch flag
bool nem = false;
unsigned long torpedoLaunchTime = 0;    // Time of torpedo launch
unsigned long lastRecieveTime = 0;      // Time of the last recieved message

// Torpedo pins
int TORPEDO_LAUNCH_PINS[] = {TL1_PIN, TL2_PIN, TL3_PIN};
int TORPEDO_HOLD_PINS[] = {TH1_PIN, TH2_PIN, TH3_PIN};

// Main Functions
void setup();
void loop();

// Initialization Functions
void initializeThrusters();
void initializeTorpedos();
void initializeMCP();
void initializeMPU();

// Torpedo Functions
void launchTorpedo();
void stopTorpedo();

// Communication Functions
void readMCP();
void readMPU();
void readRaspi();
void writeRaspi();

// Movement Functions
void assignMotorValues();
void rotateCam();

// ###########################################################


// Setup function
void setup() {
  Serial.begin(115200);
  Serial.setTimeout(100);

  Serial.println("");

  initializeThrusters();
  initializeTorpedos();
  initializeMCP();
  initializeMPU();
  pinMode(NEM_PIN, INPUT);

  Serial.println("Initialization complete.");
}

// Main loop
void loop() {

  nem = !(digitalRead(NEM_PIN));

  if(nem){
    ULValue = 1750;
    URValue = 1750;
    assignMotorValues();
    while(1);
  }

  readMCP();
  readMPU();

  if(millis()-lastRecieveTime >= COMM_DEADLINE){
    FLValue = 1500;
    FRValue = 1500;
    BLValue = 1500;
    BRValue = 1500;
    ULValue = 1500;
    URValue = 1500;
    assignMotorValues();
  }

  else{

    if (launch) {
      if (millis() - torpedoLaunchTime >= TORPEDO_LAUNCH_DURATION) {
        stopTorpedo();
      } else {
        launchTorpedo();
      }
    }

    assignMotorValues();
    rotateCam();

  }

  writeRaspi();
}

// Initialize and calibrate thrusters and servo
void initializeThrusters() {

  int thrusterPins[] = {FL_PIN, FR_PIN, BL_PIN, BR_PIN, UL_PIN, UR_PIN};
  Servo* thrusters[] = {&FL, &FR, &BL, &BR, &UL, &UR};

  camServo.attach(CAM_PIN);

  for (uint8_t i = 0; i < 6; i++) {
    thrusters[i]->attach(thrusterPins[i]);
    thrusters[i]->writeMicroseconds(1000);
    delay(500);
    thrusters[i]->writeMicroseconds(2000);
    delay(500);
    thrusters[i]->writeMicroseconds(1500);
  }

  Serial.println("ESC1 and ESC2 armed and initialized.");
  
}

// Initialize Torpedos
void initializeTorpedos() {
  for(int i = 0; i<3; i++){
    pinMode(TORPEDO_LAUNCH_PINS[i], OUTPUT);
    pinMode(TORPEDO_HOLD_PINS[i], OUTPUT);
    digitalWrite(TORPEDO_LAUNCH_PINS[i], LOW);
    digitalWrite(TORPEDO_HOLD_PINS[i], HIGH);
  }
  Serial.println("Torpedos initialized.");
}

// Initialize MCP2515 CAN bus
void initializeMCP() {
  if (!mcp.begin(CAN_BAUDRATE)) {
    Serial.println("Error initializing MCP2515.");
    while (1);  // Halt execution
  }
  Serial.println("MCP2515 initialized.");
}

// Initialize MPU6050 sensor
void initializeMPU() {
  if (!mpu.begin()) {
    Serial.println("Error initializing MPU6050.");
    while (1);  // Halt execution
  }
  Serial.println("MPU6050 initialized.");
}

// Launch torpedo
void launchTorpedo() {
  if (currentTorpedo < NUMBER_OF_TORPEDOS) {
    digitalWrite(TORPEDO_HOLD_PINS[currentTorpedo], LOW);
    digitalWrite(TORPEDO_LAUNCH_PINS[currentTorpedo], HIGH);
    torpedoLaunchTime = millis();
  }
}

// Stop current torpedo launch
void stopTorpedo() {
  if (currentTorpedo < NUMBER_OF_TORPEDOS) {
    digitalWrite(TORPEDO_LAUNCH_PINS[currentTorpedo], LOW);
    currentTorpedo++;
    launch = false;
    Serial.print("Torpedo launched successfully with "); Serial.print(millis()-torpedoLaunchTime); Serial.println("ms");
    torpedoLaunchTime = 0;
  }
}

// Read data from CAN bus
void readMCP() {
  int packetSize = mcp.parsePacket();

  if (packetSize) {
    lastRecieveTime = millis();
    
    if (mcp.packetId() == 0x13) {
      int values[8];

      for (uint8_t i = 0; i < 8; i++) {
        values[i] = (mcp.read() + 100) * 10;
      }

      FLValue  = values[0];
      FRValue  = values[1];
      BLValue  = values[2];
      BRValue  = values[3];
      ULValue  = values[4];
      URValue  = values[5];
      camAngle = map(values[6], 0, 255, 1000, 2000);
      launch  = values[7];

    }
  }
}

// Read data from MPU6050
void readMPU() {
  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  ax = a.acceleration.x;
  ay = a.acceleration.y;
  az = a.acceleration.z;
  gx = g.gyro.x;
  gy = g.gyro.y;
  gz = g.gyro.z;
}

// Read data from Raspberry Pi
void readRaspi() {
  
  if(Serial.available()){
    lastRecieveTime = millis();
    String message = Serial.readString();
    String parts[6];
    int index = 0;

    while (message.length() > 0 && index < 6) {
      int commaIndex = message.indexOf(',');
      if (commaIndex == -1) {
        parts[index++] = message;
        break;
      }
      parts[index++] = message.substring(0, commaIndex);
      message = message.substring(commaIndex + 1);
    }

    FLValue  = parts[0].toFloat();
    FRValue  = parts[1].toFloat();
    BLValue  = parts[2].toFloat();
    BRValue  = parts[3].toFloat();
    ULValue  = parts[4].toFloat();
    URValue  = parts[5].toFloat();
  }
}

// Send data to Raspberry Pi
void writeRaspi() {

  Serial.print("*");

  Serial.print(FLValue); Serial.print(",");
  Serial.print(FRValue); Serial.print(",");
  Serial.print(BLValue); Serial.print(",");
  Serial.print(BRValue); Serial.print(",");
  Serial.print(ULValue); Serial.print(",");
  Serial.print(URValue);Serial.print(",");

  Serial.print(ax); Serial.print(",");
  Serial.print(ay); Serial.print(",");
  Serial.print(az); Serial.print(",");
  Serial.print(gx); Serial.print(",");
  Serial.print(gy); Serial.print(",");
  Serial.print(gz); Serial.print(",");
  
  Serial.print(3 - currentTorpedo); Serial.print(",");
  
  Serial.println(nem);
}

void assignMotorValues(){
    FL.writeMicroseconds(FLValue);
    FR.writeMicroseconds(FRValue);
    BL.writeMicroseconds(BLValue);
    BR.writeMicroseconds(BRValue);
    UL.writeMicroseconds(ULValue);
    UR.writeMicroseconds(URValue);
}

// Control camera rotation
void rotateCam(){
  camServo.writeMicroseconds(camAngle);
}



