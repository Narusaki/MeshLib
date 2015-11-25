#version 430 core

in vec3 position;
in vec3 normal;
in vec2 texCoord;

// light parameters
uniform bool lightingOn;
uniform vec3 Ambient; 
uniform vec3 Diffuse; 
uniform vec3 Specular;
uniform vec3 LightPosition;
uniform float Shininess; 
uniform float Strength;
uniform vec3 color;

// attenuation coefficience
uniform float ConstantAttenuation;
uniform float LinearAttenuation; 
uniform float QuadraticAttenuation;

// texture parameters
uniform bool textureOn;
uniform sampler2D tex;

void main()
{
	if (lightingOn)
	{
		vec3 lightDirection = LightPosition - position; 
		float lightDistance = length(lightDirection);
		lightDirection = lightDirection / lightDistance;
		
		float attenuation = 1.0 / (ConstantAttenuation + LinearAttenuation * lightDistance + QuadraticAttenuation * lightDistance * lightDistance);
		
		vec3 halfVector = normalize(lightDirection + vec3(0.0, 0.0, 1.0));
		float diffuse = max(0.0, dot(normal, lightDirection)); 
		float specular = max(0.0, dot(normal, halfVector));
	
		if (diffuse == 0.0) specular = 0.0;
		else specular = pow(specular, Shininess) * Strength;
	
		vec3 actualColor = color;
		if (textureOn) actualColor = vec3(texture(tex, texCoord));
		vec3 rgb = min(actualColor * (Ambient + Diffuse * diffuse * attenuation + Specular * specular * attenuation), vec3(1.0));
		
		gl_FragColor = vec4(rgb, 1.0);
	}
	else
	{
		vec3 actualColor = color;
		if (textureOn) actualColor = vec3(texture(tex, texCoord));
		gl_FragColor = vec4(actualColor, 1.0);
	}
}
