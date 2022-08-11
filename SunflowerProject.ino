// ultraSound ref = https://create.arduino.cc/projecthub/abdularbi17/ultrasonic-sensor-hc-sr04-with-arduino-tutorial-327ff6
// infrared ref = https://create.arduino.cc/projecthub/biharilifehacker/how-to-use-ir-sensor-with-arduino-with-full-code-bihar-3f29c3
// pump ref = https://www.robotique.tech/robotics/control-a-water-pump-by-arduino/
// pt ref = https://roboticsbackend.com/arduino-protothreads-tutorial/#Install_the_Protothreads_library_for_Arduino

// Protothread library
#include <pt.h>

// Relay
#define RelayIn 7

// Infrared sensor
#define DigitalOut 4

// UltraSound sensor
#define TrigPin 3
#define EchoPin 2

// Both protothreads
static struct pt pt1;

// Time it took to hit the object by the UltraSound sensor
long duration;
int distance;

// Pump data
static unsigned long pump_last_used = 0;
static unsigned long pump_last_end = 0;
static bool pump_used = false;
static bool pump_end = false;

static long pump_duration = 1000;
static long pump_cooldown = 1500;

// TODO: Implement threads and pump trigger

void setup() {
  // Set up pins
  pinMode(DigitalOut, INPUT);
  pinMode(TrigPin, OUTPUT);
  pinMode(EchoPin, INPUT);
  pinMode(RelayIn, OUTPUT);

  // Initialize the threads
  PT_INIT(&pt1)
  
  Serial.begin(9600); // Serial Communication is starting with 9600 of baudrate speed
}

void loop() {
  // Start the threads
  thread(&pt1);
  
  // Send an UltraSound signal
  digitalWrite(TrigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(TrigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(TrigPin, LOW);

  // Duration it took for the signal to reach the object
  duration = pulseIn(EchoPin, HIGH);

  // The distance between the sensor and object
  distance = duration * 0.017;

  Serial.println(distance);
}

static int thread(struct pt *pt) {
  static unsigned int lastTick;
  
  PT_BEGIN(pt);
  
  while (true) {
    if (digitalRead(DigitalOut) == LOW) {
      if (not pump_used && millis() - pump_last_end > pump_cooldown) {
        digitalWrite(RelayIn, HIGH);
    
        pump_last_used = millis();
        pump_used = true;
        pump_end = false;
      }
      else if (not pump_end && millis() - pump_last_used > pump_duration) {
        digitalWrite(RelayIn, LOW);
      
        pump_end = true;
        pump_last_end = millis();
      }
    }
    else {
      if (not pump_end) {
        digitalWrite(RelayIn, LOW);

        pump_end = true;
        pump_last_end = millis();
      }
    
      pump_used = false;
    }

    // I encountered a problem here, if x is too small.
    // The problem occurs when the infrared is in the middle of detecting an object,
    // the output would look like this: 0, 0, 0, 1, 0, 1, 1, 1.
    // And so it gets turned on, but then immediently gets turned off.
    //
    // Currently i don't have a fix for this, the best i can do is make it slower.
    lastTick = millis();
    PT_WAIT_UNTIL(pt, millis() - lastTick > 50);
  }
  
  PT_END(pt);
}
