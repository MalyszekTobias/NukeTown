#version 330 core

in vec2 fragTexCoord;
in vec4 fragColor;

uniform sampler2D texture0;
uniform vec2 resolution;

#define MAX_LIGHTS 10

uniform vec3 lights[MAX_LIGHTS]; // x, y, radius
uniform vec4 light_colors[MAX_LIGHTS];
uniform int num_lights;

out vec4 finalColor;

void main() {
    vec4 base_color = texture(texture0, fragTexCoord);
    if (base_color.a == 0.0) {
        discard;
    }

    vec3 light_effect = vec3(0.0);
    vec2 frag_pos_screen = gl_FragCoord.xy;

    for (int i = 0; i < num_lights; i++) {
        float dist = distance(lights[i].xy, frag_pos_screen);
        float radius = lights[i].z;
        if (dist < radius) {
            float attenuation = 1.0 - (dist / radius);
            light_effect += light_colors[i].rgb * attenuation;
        }
    }

    // For now, just add the light effect. A better model would be multiplicative.
    base_color.rgb += light_effect;

    finalColor = base_color;
}

