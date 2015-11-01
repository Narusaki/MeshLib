import OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
import ctypes
import numpy
import sys, os

OpenGL.ERROR_CHECKING = False

program = None
vertArrayObj = None
vertBufObj = None
positionId = -1
DEPTHEPS = 0.0001

verts = numpy.array([
	0.6, 0.6, 0.0, 1.0, 
	-0.6, 0.6, 0.0, 1.0, 
	0.0, -0.6, 0.0, 1.0
], dtype=numpy.float32)

# vertex and fragment shader content
vertShaderContent = '''
#version 430 core
in vec4 position;
void main()
{
	gl_Position = position;
}
'''

fragShaderContent = '''
#version 430 core
void main()
{
	gl_FragColor = vec4(0, 1, 0, 1);
}
'''

def initGL():
	global vertArrayObj
	global vertBufObj
	global positionId
	global program
	# compile shaders and program
	VERTEX_SHADER = shaders.compileShader(vertShaderContent, GL_VERTEX_SHADER)
	FRAGMENT_SHADER = shaders.compileShader(fragShaderContent, GL_FRAGMENT_SHADER)
	program = shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER)
	
	# vao
	vertArrayObj = glGenVertexArrays(1)
	glBindVertexArray(vertArrayObj)
	# vbo for vertices
	vertBufObj = glGenBuffers(1)
	# send data to server
	glBindBuffer(GL_ARRAY_BUFFER, vertBufObj)
	glBufferData(GL_ARRAY_BUFFER, len(verts)*4, verts, GL_STATIC_DRAW)
	# assign data layout
	positionId = glGetAttribLocation(program, 'position')
	glVertexAttribPointer(positionId, 4, GL_FLOAT, False, 0, ctypes.c_void_p(0))
	glEnableVertexAttribArray(positionId)
	
	shaders.glUseProgram(program)
	# glEnableClientState(GL_VERTEX_ARRAY)

	glClearColor(1.0, 1.0, 1.0, 1.0)
	glShadeModel(GL_SMOOTH)
	glClearDepth(1.0)
	glEnable(GL_DEPTH_TEST)

def display():
	global vertArrayObj
	global vertBufObj
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glUseProgram(program)
	glBindVertexArray(vertArrayObj)
	glDrawArrays(GL_TRIANGLES, 0, 3)
	glutSwapBuffers()

def reshape(width, height):
	glViewport(0, 0, width, height)

def keyboard(key, x, y):
	pass

def keyboardUp(key, x, y):
	pass

glutInit(sys.argv)
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
glutInitWindowSize(640, 480)
glutInitContextVersion(4, 3)
glutInitContextProfile(GLUT_CORE_PROFILE);
glutCreateWindow(b'Narusaki\'s GLWindow')
initGL()
glutDisplayFunc(display)
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutKeyboardUpFunc(keyboardUp)
glutMainLoop()
