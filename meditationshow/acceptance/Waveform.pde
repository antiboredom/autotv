class Waveform {
  static final int SINE =0;
  static final int SQUARE =1;
  static final int TRIANGLE =2;
  static final int SAWTOOTH =3;
  static final int RAMP =4;

  int period;
  int offset;
  int wave_type;

  Waveform (int wave_type0, int period0, int offset0) {
    wave_type=wave_type0;
    period=period0;
    offset=offset0;
  }

  float next(){
    float phase;

    switch(wave_type)
    {
    case 0: // sine
      phase=(frameCount+offset+0.5)%period;
      break;

    case 3: // sawtooth
      phase=(frameCount+offset)%(period+1);
      break;
    case 4: // ramp
      phase=(frameCount+offset)%(period+1);
      break;
    default : 
      phase=(frameCount+offset)%period;
      break;

    }

    float fp=phase/period;
    float sample=0.0f;
    
    switch(wave_type)
    {
    case 0: // sine
      sample=(sin(fp*TWO_PI)+1)/2.0f;
      break;
    case 1: // square
      if(fp<0.5f)
        sample=0.0f;
      else
        sample=1.0f;
      break;
    case 2: // triangle
      if(fp<0.5f)
        sample=fp*2;
      else
        sample=1.0f-(fp-0.5f)*2.0f;
      break;
    case 3: // sawtooth
      sample=1.0f-fp;
      break;
    case 4: // ramp
      sample=fp;
      break;
    }
    return sample;
  }
}