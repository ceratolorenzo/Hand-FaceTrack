#include <LedControl.h>

int DIN = 10;
int CS =  9;
int CLK  = 8;

/* Code explanation for the future me:
The Matrix array is fed to the led control for rendering, and it has a byte data type.
This is an example:
byte Matrix[8] = {0x00, 0x01, 0x03, 0x07, 0x0F, 0x1F, 0x3F, 0x7F};

The HEX value decides wether a pixel of that row will be lit up or not, and it works just like binary notation
E.g.: (1, 0, 1, 0, 0, 0, 0, 0) -> 0x05 (because it is 4+1)

The render() function does just that, it converts the two dimensional array to the corresponding hex value.
Since the matrix LED is rotated in the physical world, the algorithm is flipped.
Instead of 5 being (1, 0, 1, 0, 0, 0, 0, 0), it is (0, 0, 0, 0, 0, 1, 0, 1). You just read from right to left.
That is why the code has a Grid[i][7-j] instead of a Grid[i][j].
*/

byte Matrix[8];

float Grid[7][8] = {
  {0, 0, 0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0, 0, 0},
  {0, 0, 0, 0, 0, 0, 0, 0},
};

LedControl ledControl = LedControl(DIN, CLK, CS, 0);

struct Particle {
  int x;
  float y;
  float speed;

  //Default constructor
  Particle() : x(0), y(0), speed(0) {}

  Particle(int x, float y, float speed)
    : x(x), y(y), speed(speed) {}
};

const int MAX_PARTICLES = 4;
Particle particles[MAX_PARTICLES];

unsigned long currentTime;
unsigned long lastFrame = 0; // Stores the last time called
int frameRate = 60;  // frames per second

/* 
  Every frame the particleFrequency value gets added to the lastParticle float
  until it becomes >= 1, which triggers a new Particle to fall.
  Once the new particle is released, the lastParticle value drops back to 0 to ensure
  that overflow never happens. This allows the frequency between the falling particles
  to increase through time and to have a stable code that prevents any sort of anomalies.
*/
float lastParticle = 0; //last time the particle was called
float particleFrequency = 0.02; // e.g. 0.05 particles every frame
float particleSpeed = 0.045;

//FOR FUTURE: TWEAK PARTICLE FREQUENCY (ADD INCREASE OF IT), AND PARTICLE SPEED ON LINE 100

void setup() {
  Serial.begin(9600);
  ledControl.shutdown(0, false); //The MAX7219 is in power-saving mode on startup
  ledControl.setIntensity(0, 2); // Maximum brightness value is 15
  ledControl.clearDisplay(0); // and clear the  display

  currentTime = 0;

  for (int i = 0; i < MAX_PARTICLES; i++) {
    particles[i] = Particle(0, 0, 0);
  }

  render();
}

void loop() {
  if (Serial.available()) {
    byte fingerData = Serial.read();
    // Update the bottom row based on received finger data
    Matrix[7] = fingerData;

    render();
  }

  // Call CNF() based on framerate
  currentTime = millis();

  unsigned long frameInterval = 1000 / frameRate;  // Time between frames in milliseconds
  if (currentTime - lastFrame >= frameInterval) {
    //particle frequency gets biased by a range of max ± 0.03
    lastParticle += particleFrequency + calcRandomBias(0.03);
    if (lastParticle >= 1) {
      //create new Particle in the first free spot
      for (int i = 0; i < MAX_PARTICLES; i++) {
        if (particles[i].speed == 0) {
          //particles speed gets biased by a range of max ± 0.005
          int xPos = random(8);
          if ((xPos == 1 || xPos == 6) && random(3) == 0) {
            xPos = random(8); //make it less likely to come on ring fingers (harder to track when raising)
          }
          particles[i] = Particle(random(8), 0, particleSpeed + calcRandomBias(0.005));
          break;
        }
      }

      lastParticle -= 1;
    }

    CNF(currentTime);
    render();  // Render the new frame
    lastFrame = currentTime;  // Update the last frame time
  }
}

float calcRandomBias(float value) {
  //eg 0.05
  //0...10 * (?) = 0.1 -> - 0.05
  //0...(5 * 2) * ((0.05) / (5)) - 0.05
  float x = value;
  while (x < 1) {
    x *= 10;
  }

  return random(x * 2 + 1) * (value / x) - value;
}

void CNF(unsigned long currentTime) { //Calculate Next Frame
  for (int i = 0; i < MAX_PARTICLES; i++) {
    if (particles[i].speed > 0) {
      Grid[int(particles[i].y)][particles[i].x] = 0;
      particles[i].y += particles[i].speed; //will be a float but is going to get rounded to the nearest led

      if (int(particles[i].y) > 6) {
        particles[i].speed = 0;
      } else {
        Grid[int(particles[i].y)][particles[i].x] = 1;
      }
    }
  }
}

void render() {
  //translate the two dimensional array (grid) into the byte array (matrix)
  for (int i = 0; i < 7; i++) {
    int sum = 0;
    for (int j = 0; j < 8; j++) {
      sum += Grid[i][7-j] * (1 << j);
    }
    Matrix[i] = sum;
  }

  //render updated byte array
  int k = 0;
  for (int k = 0; k < 8; k++) {
    ledControl.setRow(0, k, Matrix[k]);
  }
}