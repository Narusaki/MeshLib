import OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
from MeshLib.Mesh import *
from math import pi, tan, sin, cos, sqrt
import ctypes
import numpy
import sys, os

if len(sys.argv) < 2:
	print('USAGE: [.py] [mesh1] ...')
	sys.exit(-1)

# load models
objList = []
for i in range(1, len(sys.argv)):
	mesh = Mesh()
	mesh.LoadMesh(sys.argv[i])
	objList.append(mesh)

OpenGL.ERROR_CHECKING = False

# some global variables
dkey = False
showWire = True

program = None
vertArrayObjs = []
vertBufObjs = []
faceBufObjs = []
scaleMatrices = []
positionId = -1; scaleMatrixId = -1; mvMatrixId = -1; projMatrixId = -1
DEPTHEPS = 0.0001


# vertex and fragment shader content
vertShaderContent = '''
#version 430 core

in vec3 position;
uniform mat4 scaleMatrix;
uniform mat4 mvMatrix, projMatrix;

void main()
{
	gl_Position = projMatrix * mvMatrix * scaleMatrix * vec4(position, 1);
}
'''

fragShaderContent = '''
#version 430 core
void main()
{
	gl_FragColor = vec4(0, 1, 0, 1);
}
'''

def constructPerspectiveMatrix(fovy, aspect, zNear, zFar):
	height = tan(fovy / 180.0 * pi / 2.0) * zNear * 2.0
	width = height * aspect
	m = []
	for i in range(0, 16): m.append(0.0)
	m[0] = 2.0 * zNear / width;
	m[5] = 2.0 * zNear / height;
	m[10] = (zFar + zNear) / (zNear - zFar);
	m[11] = -1.0;
	m[14] = 2.0 * zFar * zNear / (zNear - zFar);
	return m

def constructScaleMatrix(model):
	m = []
	for i in range(0, 16): m.append(0.0)
	m[0] = model.scale;
	m[5] = model.scale;
	m[10] =  model.scale;
	m[12] = -model.center.x * model.scale;
	m[13] = -model.center.y * model.scale;
	m[14] = -model.center.z * model.scale;
	m[15] = 1.0;
	return m

def initGL():
	global vertArrayObjs
	global vertBufObjs
	global positionId
	global scaleMatrixId
	global mvMatrixId
	global projMatrixId
	global program
	# compile shaders and program
	VERTEX_SHADER = shaders.compileShader(vertShaderContent, GL_VERTEX_SHADER)
	FRAGMENT_SHADER = shaders.compileShader(fragShaderContent, GL_FRAGMENT_SHADER)
	program = shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER)
	shaders.glUseProgram(program)
	
	# vao
	for obj in objList:
		# construct arrays
		verts = []; faces = []
		for v in obj.verts:
			verts.append(v[0]); verts.append(v[1]); verts.append(v[2])
		for f in obj.faces:
			faces.append(f[0]); faces.append(f[1]); faces.append(f[2])
		verts = numpy.array(verts, dtype=numpy.float32)
		faces = numpy.array(faces, dtype=numpy.uint32)
		# generate vao
		vertArrayObj = glGenVertexArrays(1)
		vertArrayObjs.append(vertArrayObj)
		glBindVertexArray(vertArrayObj)
		# bo for vertices
		vertBufObj = glGenBuffers(1)
		vertBufObjs.append(vertBufObj)
		# send data to server
		glBindBuffer(GL_ARRAY_BUFFER, vertBufObj)
		glBufferData(GL_ARRAY_BUFFER, len(verts)*4, verts, GL_STATIC_DRAW)
		# bo for faces
		faceBufObj = glGenBuffers(1)
		faceBufObjs.append(faceBufObj)
		# send data to server
		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, faceBufObj)
		glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(faces)*4, faces, GL_STATIC_DRAW)
		# scale matrices
		scaleMatrices.append(numpy.array(constructScaleMatrix(obj), dtype=numpy.float32))

	positionId = glGetAttribLocation(program, 'position')
	scaleMatrixId = glGetUniformLocation(program, 'scaleMatrix')
	mvMatrixId = glGetUniformLocation(program, 'mvMatrix')
	projMatrixId = glGetUniformLocation(program, 'projMatrix')

	# assign data layout
	glVertexAttribPointer(positionId, 3, GL_FLOAT, False, 0, ctypes.c_void_p(0))
	glEnableVertexAttribArray(positionId)

	identity = []
	for i in range(0, 16):
		identity.append(1.0 if i%5 == 0 else 0.0)
	identity[14] = -2.0
	identity = numpy.array(identity, dtype=numpy.float32)
	glUniformMatrix4fv(mvMatrixId, 1, False, identity)
	
	# glEnableClientState(GL_VERTEX_ARRAY)

	glClearColor(1.0, 1.0, 1.0, 1.0)
	glShadeModel(GL_SMOOTH)
	glClearDepth(1.0)
	glEnable(GL_DEPTH_TEST)


def display():
	global program
	global vertArrayObjs
	global scaleMatrixId
	global scaleMatrices

	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glUseProgram(program)
	glUniformMatrix4fv(scaleMatrixId, 1, False, scaleMatrices[0])
	glBindVertexArray(vertArrayObjs[0])
	glDrawElements(GL_TRIANGLES, len(objList[0].faces)*3, GL_UNSIGNED_INT, ctypes.c_void_p(0))
	glutSwapBuffers()

def reshape(width, height):
	global projMatrixId
	glViewport(0, 0, width, height)
	glUniformMatrix4fv(projMatrixId, 1, False, constructPerspectiveMatrix(45.0, width/height, 0.1, 1000.0))

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
