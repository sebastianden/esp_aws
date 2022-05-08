// ESP8266 AWS IoT 

#include <string.h>
#include "FS.h"
#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include "DHT.h"
#include "secrets.h"

#define DHTTYPE DHT11
#define DHTPIN D5

// DHT11 temperature and humidity sensor
DHT dht(DHTPIN, DHTTYPE); 

WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org");

// Callback triggered on recieving a message
void callback(char* topic, byte* payload, unsigned int length) {
}

// Initialize WiFi and MQTT clients
WiFiClientSecure espClient;
PubSubClient client(AWS_endpoint, 8883, callback, espClient);
char msg[100];

// Load AWS certs
BearSSL::X509List cert(cacert);
BearSSL::X509List client_crt(client_cert);
BearSSL::PrivateKey key(privkey);

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


// Setup funtion, set up WiFi, load certificates, publish message
void setup() {
  Serial.begin(115200);
  Serial.setDebugOutput(true);

  dht.begin();
  
  // Initialize WiFi Connection
  setup_wifi();
  
  delay(1000);

  Serial.println("Trying to load AWS certificates");
  // Update the WiFi Client with the AWS certificates
  espClient.setTrustAnchors(&cert);
  espClient.setClientRSACert(&client_crt, &key);
  Serial.println("AWS certificates loaded");

  Serial.print("Attempting MQTT connection...");
  while (!client.connected()) {
    // Attempt to connect
    if (client.connect(AWS_thing)) {
      Serial.println("connected");
    }
  }
  // Get a time structure and extract year, month, day
  unsigned long epochTime = timeClient.getEpochTime();
  // Read sensor values
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  // Publish message
  snprintf(msg, 100, "{\"timestamp\":%d,\n\"temperature\":%f,\n\"humidity\":%f}", epochTime, t, h);
  client.publish(pub_topic, msg);
  Serial.print("Publish message: ");
  Serial.println(msg);

  // Sleep
  ESP.deepSleep(30*1e6);
}

// Dummy loop function, not used due to deepSleep
void loop() {

}
