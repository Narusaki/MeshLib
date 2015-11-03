#version 430 core

in vec3 vPosition;
in vec3 vNormal;

uniform mat4 scaleMatrix;
uniform mat4 mvMatrix, projMatrix;

out vec3 position;
out vec3 normal;

void main()
{
	gl_Position = projMatrix * mvMatrix * scaleMatrix * vec4(vPosition, 1.0);
	position = vec3(mvMatrix * scaleMatrix * vec4(vPosition, 1.0));
	normal = vec3(mvMatrix * vec4(vNormal, 0.0));
}
