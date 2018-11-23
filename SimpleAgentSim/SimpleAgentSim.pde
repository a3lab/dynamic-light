/**
 * oscP5sendreceive by andreas schlegel
 * example shows how to send and receive osc messages.
 * oscP5 website at http://www.sojamo.de/oscP5
 */
 
import oscP5.*;
import netP5.*;
  
OscP5 oscP5;
NetAddress myRemoteLocation;

float x; // position of the agent

final float SPREAD = 0.05;
final float STEP = 0.01;
final float LIGHT_INTENSITY = 1.0;
final float LIGHT_DECAY     = 50.0;

float cellLeftX;
float cellRightX;

void setup() {
  size(640, 480);

  /* start oscP5, listening for incoming messages at port 12000 */
  oscP5 = new OscP5(this, 8001);
  
  /* myRemoteLocation is a NetAddress. a NetAddress takes 2 parameters,
   * an ip address and a port number. myRemoteLocation is used as parameter in
   * oscP5.send() when sending osc packets to another computer, device, 
   * application. usage see below. for testing purposes the listening port
   * and the port of the remote location address are the same, hence you will
   * send messages back to this sketch.
   */
  myRemoteLocation = new NetAddress("127.0.0.1", 8000);
  
  oscP5.plug(this, "action", "/env/action");

  x = SPREAD;
  
  cellLeftX  = 0.5 - SPREAD;
  cellRightX = 0.5 + SPREAD;
  
  sendObservation();
}

public void action(int a) {
  println("Received action: " + a);
  // Update x.
  x += (a-1) * STEP;
  println(x);
  while (x < 0) x++;
  while (x > 1) x--;
  
  // Update observations.
  sendObservation();
}

void sendObservation() {
  OscMessage msg = new OscMessage("/env/observation");
  
  float leftLight  = incomingLight(x, cellLeftX);
  float rightLight = incomingLight(x, cellRightX);
  float reward = 0.5 * (leftLight + rightLight);
  msg.add(reward);
  msg.add(x);
  msg.add(leftLight);
  msg.add(rightLight);
  oscP5.send(msg, myRemoteLocation);   
}

float incomingLight(float source, float dest) {
  return LIGHT_INTENSITY / (1 + LIGHT_DECAY * distance(source, dest));
}

float distance(float x1, float x2) {
  return sq(x1 - x2);
}

int toAbsolute(float xPos) {
  return round(map(xPos, 0, 1, 0, width));
}

void drawCell(float xPos) {
  fill(255, 0, 0, 64);
  ellipse(toAbsolute(xPos), height/2, 100, 100); 
}

void draw() {
  background(0);
  drawCell(cellLeftX);
  drawCell(cellRightX);
  fill(255, 255, 255, 128);
  ellipse(toAbsolute(x), height/2, 20, 20);
}

void mousePressed() {
  sendObservation();
}


/* incoming osc message are forwarded to the oscEvent method. */
void oscEvent(OscMessage theOscMessage) {
  /* print the address pattern and the typetag of the received OscMessage */
  print("### received an osc message.");
  print(" addrpattern: "+theOscMessage.addrPattern());
  println(" typetag: "+theOscMessage.typetag());
}
