#version 430 core

in vec3 position;
uniform mat4 scaleMatrix;
uniform mat4 mvMatrix, projMatrix;

void main()
{
	gl_Position = projMatrix * mvMatrix * scaleMatrix * vec4(position, 1);
}
