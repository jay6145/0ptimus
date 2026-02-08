#define BUZZER_PIN 8
const float TEMP_THRESHOLD_C = 26.5;

#include "DHT.h"
#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

const int BEEP_COUNT = 5;
bool alarmLatched = false;   // true once we've done the 5 beeps for the current "over temp" event

void beepOnce() {
  digitalWrite(BUZZER_PIN, HIGH);
  delay(200);
  digitalWrite(BUZZER_PIN, LOW);
  delay(200);
}

void setup() {
  Serial.begin(9600);
  Serial.println(F("DHTxx test!"));

  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  dht.begin();
}

void loop() {
  delay(1000);

  float h = dht.readHumidity();
  float t = dht.readTemperature();
  float f = dht.readTemperature(true);

  if (isnan(h) || isnan(t) || isnan(f)) {
    Serial.println(F("Failed to read from DHT sensor!"));
    return;
  }

  Serial.print("{\"store_id\":1,\"sensor\":\"cooler_temp_c\",\"value\":");
  Serial.print(t);
  Serial.println("}");

  // Reset latch once temp is back under threshold (so it can trigger again later)
  if (t <= TEMP_THRESHOLD_C) {
    alarmLatched = false;
    digitalWrite(BUZZER_PIN, LOW);
    return;
  }

  // Over threshold: beep 5 times only once per "over temp event"
  if (!alarmLatched) {
    for (int i = 0; i < BEEP_COUNT; i++) {
      beepOnce();
    }
    alarmLatched = true;
  } else {
    digitalWrite(BUZZER_PIN, LOW);
  }
}
