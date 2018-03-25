#include <PubNub.h>
#include <SPI.h>
#include <EthernetV2_0.h>
#include <string.h>
byte mac[] = { WasMac };
byte gateway[] = { WasGate };
byte subnet[] = { WasNet };
IPAddress ip(WasIP);
char pubkey[] = "WasPub";
char subkey[] = "WasSub";
char channel[] = "WasChannel";
int RelayControl5 = 5;
int RelayControl6 = 6;
int RelayControl7 = 7;
int i;
EthernetClient *client;
#define W5200_CS  3
#define SDCARD_CS 4
// PubNub Dev Console text {"cmd":"RelayControl6:1"} or {"cmd":"RelayControl6:0"}
void setup()
{
  pinMode(SDCARD_CS, OUTPUT);
  digitalWrite(SDCARD_CS, HIGH);
  Serial.begin(9600);
  Serial.println("    Serial set up");
  while (!Ethernet.begin(mac)) {
    Serial.println("Ethernet setup error");
    delay(1000);
  }
  Serial.println("Ethernet set up");
  PubNub.begin(pubkey, subkey);
  Serial.println("PubNub set up");
  pinMode(RelayControl5, OUTPUT);
  pinMode(RelayControl6, OUTPUT);
  pinMode(RelayControl7, OUTPUT);
  reset();
}
void loop()
{
  Ethernet.maintain();
  PubSubClient *client;
  Serial.println("waiting for a message (subscribe)");
  client = PubNub.subscribe(channel);
  if (!client) {
    Serial.println("subscription error");
    return;
  }
  String messages[10];
  boolean inside_command = false;
  int num_commands = 0;
  String message = "";
  char c;
  while (client->wait_for_data()) {
    c = client->read();
    if (inside_command && c != '"') {
      messages[num_commands] += c;
    }
    if (c == '"') {
      if (inside_command) {
        num_commands = num_commands + 1;
        inside_command = false;

      } else {
        inside_command = true;
      }
    }
    message += c;
  }
  client->stop();
  for (i = 0; i < num_commands; i++) {
    int colonIndex = messages[i].indexOf(':');
    String subject = messages[i].substring(0, colonIndex);
    String valueString = messages[i].substring(colonIndex + 1, messages[i].length());
    boolean value = false;
    if (valueString == "1") {
      value = true;
    }
    if (subject == "RelayControl5") {
      Relay(RelayControl5, value);
    }
    if (subject == "RelayControl6") {
      Relay(RelayControl6, value);
    }
    if (subject == "RelayControl7") {
      Relay(RelayControl7, value);
    }
    if (subject == "blink") {
      blink(100, valueString.toInt());
    }
    Serial.println(subject);
    Serial.println(value);
  }
  Serial.print(message);
  Serial.println();
  delay(2000);
}
void Relay(int Swtich, boolean on) {
  if (on) {
    Serial.println("Relay HIGH");
    digitalWrite(Swtich, HIGH);
  } else {
    Serial.println("Relay low");
    digitalWrite(Swtich, LOW);
  }
}
void reset() {
  Serial.println("Void reset");
  Relay(RelayControl5, false);
  Relay(RelayControl6, false);
  Relay(RelayControl7, false);
}
void on() {
  Serial.println("Void on");
  Relay(RelayControl5, true);
  Relay(RelayControl6, true);
  Relay(RelayControl7, true);
}
void off() {
  Serial.println("Void off");
  Relay(RelayControl5, false);
  Relay(RelayControl6, false);
  Relay(RelayControl7, false);
}
