/* ESP8266 AWS IoT 
   Use esp8266 version 2.5.0
   This example needs https://github.com/esp8266/arduino-esp8266fs-plugin
*/
#include <string.h>
#include "FS.h"
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include "DHT.h"

#define DHTTYPE DHT11
#define DHTPIN D5

// Set WiFi credentials
const char* ssid = "<YOUR_WIFI_SSID>";
const char* password = "<YOUR_WIFI_PASSWORD>";
// Set publish and subscribe topics
const char* pub_topic = "<YOUR_PUBLISH_TOPIC>";

// DHT11 temperature and humidity sensor
DHT dht(DHTPIN, DHTTYPE); 

WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org");

// Set AWS Endpoint and Thing name
const char* AWS_endpoint = "<YOUR_AWS_ENDPOINT>";
const char* AWS_thing = "<YOUR_THING_NAME>";

// Callback triggered on recieving a message
void callback(char* topic, byte* payload, unsigned int length) {
}

// Initialize WiFi and MQTT clients
WiFiClientSecure espClient;
PubSubClient client(AWS_endpoint, 8883, callback, espClient);
char msg[100];


// Connect to WiFi
void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  espClient.setBufferSizes(512, 512);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  timeClient.begin();
  while(!timeClient.update()){
    timeClient.forceUpdate();
  }
  espClient.setX509Time(timeClient.getEpochTime());
}


// Load AWS certificates
void load_certificates() {
  if (!SPIFFS.begin()) {
    Serial.println("Failed to mount file system");
    return;
  }
  Serial.print("Heap: ");
  Serial.println(ESP.getFreeHeap());
 
  // Load certificate file
  File cert = SPIFFS.open("/cert.der", "r");
  if (!cert)
    Serial.println("Failed to open cert file");
  else
    Serial.println("Success to open cert file");
  if (espClient.loadCertificate(cert))
    Serial.println("cert loaded");
  else
    Serial.println("cert not loaded");

  // Load private key file
  File private_key = SPIFFS.open("/private.der", "r");
  if (!private_key)
    Serial.println("Failed to open private cert file");
  else
    Serial.println("Success to open private cert file");
  if (espClient.loadPrivateKey(private_key))
    Serial.println("private key loaded");
  else
    Serial.println("private key not loaded");

  // Load CA file
  File ca = SPIFFS.open("/ca.der", "r");
  if (!ca)
    Serial.println("Failed to open ca ");
  else
    Serial.println("Success to open ca");
  if(espClient.loadCACert(ca))
    Serial.println("ca loaded");
  else
    Serial.println("ca failed");
}


// Setup funtion, set up WiFi, load certificates
void setup() {
  dht.begin();
  Serial.begin(9600);
  Serial.setDebugOutput(true);

  long start_time = millis();
  
  // Initialize WiFi Connection
  setup_wifi();
  
  delay(1000);

  // Update the WiFi Client with the AWS certificates
  load_certificates(); 

  // Get a time structure and extract year, month, day
  unsigned long epochTime = timeClient.getEpochTime();
  struct tm *ptm = gmtime ((time_t *)&epochTime); 
  int monthDay = ptm->tm_mday;
  int currentMonth = ptm->tm_mon+1;
  int currentYear = ptm->tm_year+1900;
  // Get time correctly formatted
  String formattedDate = timeClient.getFormattedTime();
  const char* timestamp = formattedDate.c_str();

  Serial.print("Attempting MQTT connection...");
  while (!client.connected()) {
    // Attempt to connect
    if (client.connect(AWS_thing)) {
      Serial.println("connected");
    }
  }
  // Read sensor values
  float h = dht.readHumidity();
  float t = dht.readTemperature();
  Serial.println(t);
  Serial.println(h);

  // Publish temperature
  snprintf(msg, 100, "{\"measurement\":\"temperature\",\n\"value\":%f,\n\"timestamp\":%d,\n\"uom\":\"°C\"}", t, epochTime, timestamp);
  client.publish(pub_topic, msg);
  Serial.print("Publish message: ");
  Serial.println(msg);

  // Publish humidity
  snprintf(msg, 100, "{\"measurement\":\"humidity\",\n\"value\":%f,\n\"timestamp\":%d,\n\"uom\":\"%%\"}", h, epochTime, timestamp);
  client.publish(pub_topic, msg);
  Serial.print("Publish message: ");
  Serial.println(msg);

  // Correct for time spent connecting and reading the sensor
  long delta_t = millis() - start_time;

  // Sleep
  ESP.deepSleep(30*60*1e6-int(delta_t*1e3));

}

// Loop function
void loop() {

}
