#ifdef GL_ES
precision mediump float;
precision mediump int;
#endif

varying vec4 vertTexCoord;
uniform sampler2D texture;
//uniform vec3 color;

void main(void)
{
    vec3 color = vec3(1.000, 0.259, 0.259);
    vec3 tColor = texture2D(texture, vertTexCoord.st).rgb;
    float a = 1.0 - ((length(tColor - color) - 0.6) * 3.0);
    gl_FragColor = vec4(tColor, a);
    //gl_FragColor = vec4(0.0, 1.0, 0.0, 0.0);


}
