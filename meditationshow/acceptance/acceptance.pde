import codeanticode.syphon.*;

import processing.video.*;
import java.nio.file.*;

PShader chroma;
Looper looper;
SyphonServer server;
Waveform tri;
int TOTALHANDS = 10;
BG bg;

void settings() {
  size(1280, 720, P3D);
  PJOGL.profile=1;
}

void setup() {
  frameRate(24);
  server = new SyphonServer(this, "meditation");
  chroma = loadShader("chroma.glsl");
  tri = new Waveform(Waveform.TRIANGLE, 3000, 0);
  //looper = new Looper("capitalist.mp4", 0, 0.0, 5, 25, this);
  bg = new BG(this);
  //randomHand();
}

void movieEvent(Movie m) {
  m.read();
}

void draw() {  
  background(10, 10, 10);
  //background(255, 0, 100);
  bg.display();
  
  if (looper != null) {
    looper.run();
    image(looper.buffer, 0, 0);
  }

  server.sendScreen();
}

void randomHand() {
  String[] folders = {"close", "wide", "slow"};
  String path = folders[int(random(folders.length))] + "/hand" + int(random(1, 10)) + ".mp4";
  println(path);
  int offset = int(random(3, 10));
  int total = int(random(7, 20));
  if (looper != null) {
    looper.reset(path, 0, 0.0, offset, total, this);
  } else {
    looper = new Looper(path, 0, 0.0, offset, total, this);
  }
}

void mousePressed() {
  //looper = null;
  randomHand();
}

class Looper {
  float x, y;
  int offset, total;
  Movie m;
  PGraphics buffer;
  int currentBuffer = 0;
  int life = 0;
  ArrayList<PGraphics> buffers = new ArrayList<PGraphics>();
  PApplet sketch;
  int totalFrames;
  float xs = 10;
  color bgcolor;
  int displayType;

  Looper(String path, float _x, float _y, int _offset, int _total, PApplet _sketch) {
    x = _x;
    y = _y;
    sketch = _sketch;
    total = _total;
    offset = _offset;

    m = new Movie(sketch, path);
    m.frameRate(24);
    m.volume(0);

    m.loop();
    totalFrames = int(m.duration() * 24);

    buffer = createGraphics(width, height, P3D);

    bgcolor = color(10, 10, 10, 0);

    displayType = int(random(0, 3));
  }

  void reset(String path, float _x, float _y, int _offset, int _total, PApplet _sketch) {
    m.stop();  
    x = _x;
    y = _y;
    sketch = _sketch;
    total = _total;
    offset = _offset;

    m = new Movie(sketch, path);
    m.frameRate(24);
    m.volume(0);
    m.loop();
    totalFrames = int(m.duration() * 24);
    currentBuffer = 0;
    buffer = createGraphics(width, height, P3D);
    buffers = new ArrayList<PGraphics>();
    bgcolor = color(10, 10, 10, 0);
    displayType = int(random(0, 3));
  }

  void updateBuffers() {
    if (buffers.size() < totalFrames) {
      PGraphics cb = createGraphics(width, height, P3D);
      cb.beginDraw();
      cb.clear();
      cb.shader(chroma);
      cb.image(m, x, y, 1280, 720);
      cb.endDraw();
      buffers.add(cb);
    }
  }

  void run() {
    updateBuffers();
    display0();
    //switch (displayType) {
    //case 0:  
    //  display0();
    //  break;
    //case 1:  
    //  display1();
    //  break;
    //case 2:  
    //  display2();
    //  break;

    //default: 
    //  display0();
    //  break;
    //}

    currentBuffer ++;
    if (currentBuffer >= totalFrames) currentBuffer = 0;
  }
  
  void display() {
    float _x = x;
    float _y = y;
    float x_dist = tri.next()*80 - 10;
        

    for (int i = 0; i < total; i++) {
      int frameNum = (currentBuffer + i*offset) % (totalFrames);
      if (buffers.size() > frameNum) {
        pushMatrix();
        scale(sin((float(i)+float(frameNum))/600.0)*2.0 + 1);
        //tint(255, abs(sin(map(frameNum, 0, totalFrames, 0.0, PI))*250));
        image(buffers.get(frameNum), _x, _y, width, height);
        //noTint();
        popMatrix();
        _x += x_dist;
      }
    }
  }

  void display0() {
    float _x = x;
    float _y = y;
    float x_dist = tri.next()*80 - 10;
    buffer.beginDraw();
    buffer.clear();
    //buffer.background(bgcolor);
    

    for (int i = 0; i < total; i++) {
      int frameNum = (currentBuffer + i*offset) % (totalFrames);
      if (buffers.size() > frameNum) {
        buffer.pushMatrix();
        buffer.scale(sin((float(i)+float(frameNum))/600.0)*2.0 + 1);
        buffer.tint(255, abs(sin(map(frameNum, 0, totalFrames, 0.0, PI))*250));
        buffer.image(buffers.get(frameNum), _x, _y, width, height);
        buffer.noTint();
        buffer.popMatrix();
        _x += x_dist;
      }
    }
    buffer.shader(chroma);
    buffer.endDraw();
  }

  void display1() {
    float _x = x;
    float _y = y;
    float x_dist = tri.next()*80 - 10;
    buffer.beginDraw();
    buffer.clear();
    //buffer.background(bgcolor);
    

    for (int i = 0; i < total; i++) {
      int frameNum = (currentBuffer + i*offset) % (totalFrames);
      if (buffers.size() > frameNum) {
        buffer.pushMatrix();
        //buffer.tint(255, abs(sin(map(frameNum, 0, totalFrames, 0.0, PI))*250));
        buffer.translate(width/2, height/2);
        buffer.scale(sin((float(i)+float(frameNum))/600.0)*2.0 + 1);
        buffer.rotate(TWO_PI * (float(i)/float(total)));
        buffer.image(buffers.get(frameNum), x, y, width, height);
        //buffer.noTint();
        buffer.popMatrix();
        _x += x_dist;
      }
    }
    buffer.endDraw();
  }

  void display2() {
    float _x = x;
    float _y = y;
    float x_dist = tri.next()*80 - 10;
    buffer.beginDraw();
    buffer.clear();
    buffer.background(bgcolor);
    
    for (int i = 0; i < total; i++) {
      int frameNum = (currentBuffer + i*offset) % (totalFrames);
      if (buffers.size() > frameNum) {
        buffer.tint(255, abs(sin(map(frameNum, 0, totalFrames, 0.0, PI))*250));

        //buffer.pushMatrix();
        buffer.translate(sin(float(frameCount)/100)*10, cos(float(frameCount)/100)*10);
        //buffer.scale(1, -1); 

        //buffer.rotate(TWO_PI * (float(i)/float(total)));

        buffer.image(buffers.get(frameNum), 0, 0, width, height);
        //buffer.popMatrix();
        buffer.noTint();

        _x += x_dist;
      }
    }
    buffer.endDraw();
  }
}

class BG {
  Movie bgmovie;
  color bgcolor;
  float opacity;

  BG(PApplet _sketch) {
    bgcolor = color(random(255), 255, 255, 255);
    bgmovie = new Movie(_sketch, setMovie());
    bgmovie.play();
    bgmovie.loop();
    opacity = 0;
  }
  
  String setMovie() {
    opacity = 0;
    String[] paths = {"slowcapitalist.mp4", "bgs/sunset1.mp4", "bgs/sunset2.mp4", "bgs/sunset3.mp4", "bgs/sunset4.mp4"};
    String path = paths[int(random(0, paths.length))];
    println(path);
    return path;
  }

  void swap() {
    opacity = 0;
    bgcolor = color(random(255), 255, 255, 255);
  }

  void display() {
    opacity = lerp(opacity, 255, 0.01);
    
    tint(255, opacity);
    color(bgcolor);
    image(bgmovie, 0, 0, width, height);
    noTint();
  }
}