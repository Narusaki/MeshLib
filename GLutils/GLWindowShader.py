import OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo
from OpenGL.GL import shaders
from MeshLib.Mesh import *
from MeshLib.GLutils.trackball import *
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
	mesh.LoadMesh(sys.argv[i], False, True)
	objList.append(mesh)

OpenGL.ERROR_CHECKING = False

# some global variables
mouseButton = None
mouseState = None
dkey = False
lkey = False
showWire = True
lighting = False
selectedObjId = -1

program = None
vertArrayObjs = []
vertBufObjs = []
faceBufObjs = []
normBufObjs = []
scaleMatrices = []
vPositionId = -1; vNormal = -1; scaleMatrixId = -1; mvMatrixId = -1; projMatrixId = -1; colorId = -1
lightingOnId = -1; AmbientId = -1; DiffuseId = -1; SpecularId = -1; LightPositionId = -1; ShininessId = -1; StrengthId = -1
cAttenuationId = -1; bAttenuationId = -1; aAttenuationId = -1
projectMatrix = None
viewport = None
DEPTHEPS = 0.0001
trackball = TrackBall(640, 480, 45.0)

# vertex and fragment shader content
vertShaderContent = open(os.path.dirname(os.path.abspath(sys.argv[0])) + os.sep + 'shader.vert').read()
fragShaderContent = open(os.path.dirname(os.path.abspath(sys.argv[0])) + os.sep + 'shader.frag').read()

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
	global vertArrayObjs, vertBufObjs, faceBufObjs, normBufObjs
	global vPositionId, vNormalId, scaleMatrixId, mvMatrixId, projMatrixId, colorId
	global lightingOnId, AmbientId, DiffuseId, SpecularId, LightPositionId, ShininessId, StrengthId
	global cAttenuationId, bAttenuationId, aAttenuationId
	global program
	global selectedObjId
	# compile shaders and program
	VERTEX_SHADER = shaders.compileShader(vertShaderContent, GL_VERTEX_SHADER)
	FRAGMENT_SHADER = shaders.compileShader(fragShaderContent, GL_FRAGMENT_SHADER)
	program = shaders.compileProgram(VERTEX_SHADER, FRAGMENT_SHADER)
	shaders.glUseProgram(program)
	
	vPositionId = glGetAttribLocation(program, 'vPosition')
	vNormalId = glGetAttribLocation(program, 'vNormal')
	scaleMatrixId = glGetUniformLocation(program, 'scaleMatrix')
	mvMatrixId = glGetUniformLocation(program, 'mvMatrix')
	projMatrixId = glGetUniformLocation(program, 'projMatrix')
	colorId = glGetUniformLocation(program, 'color')
	lightingOnId = glGetUniformLocation(program, 'lightingOn')
	AmbientId = glGetUniformLocation(program, 'Ambient')
	DiffuseId = glGetUniformLocation(program, 'Diffuse')
	SpecularId = glGetUniformLocation(program, 'Specular')
	LightPositionId = glGetUniformLocation(program, 'LightPosition')
	ShininessId = glGetUniformLocation(program, 'Shininess')
	StrengthId = glGetUniformLocation(program, 'Strength')
	cAttenuationId = glGetUniformLocation(program, 'ConstantAttenuation')
	bAttenuationId = glGetUniformLocation(program, 'LinearAttenuation')
	aAttenuationId = glGetUniformLocation(program, 'QuadraticAttenuation')

	glUniform1i(lightingOnId, lighting)
	glUniform3f(AmbientId, 0.1, 0.1, 0.1)
	glUniform3f(DiffuseId, 0.7, 0.7, 0.7)
	glUniform3f(SpecularId, 0.3, 0.3, 0.3)
	glUniform3f(LightPositionId, 0.0, 0.0, 6.0)
	glUniform1f(ShininessId, 16.0)
	glUniform1f(StrengthId, 1.0)
	glUniform1f(cAttenuationId, 1.0); glUniform1f(bAttenuationId, 5e-4); glUniform1f(aAttenuationId, 5e-4)


	# vao
	for obj in objList:
		# construct arrays
		verts = []; faces = []; normals = []
		for v in obj.verts:
			verts.append(v[0]); verts.append(v[1]); verts.append(v[2])
		for f in obj.faces:
			faces.append(f[0]); faces.append(f[1]); faces.append(f[2])
		for n in obj.normals:
			normals.append(n[0]); normals.append(n[1]); normals.append(n[2])
		verts = numpy.array(verts, dtype=numpy.float32)
		faces = numpy.array(faces, dtype=numpy.uint32)
		normals = numpy.array(normals, dtype=numpy.float32)
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
		# assign data layout
		glVertexAttribPointer(vPositionId, 3, GL_FLOAT, False, 0, ctypes.c_void_p(0))
		glEnableVertexAttribArray(vPositionId)

		# bo for faces
		faceBufObj = glGenBuffers(1)
		faceBufObjs.append(faceBufObj)
		# send data to server
		glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, faceBufObj)
		glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(faces)*4, faces, GL_STATIC_DRAW)

		# bo for normals
		normBufObj = glGenBuffers(1)
		normBufObjs.append(normBufObj)
		# send data to server
		glBindBuffer(GL_ARRAY_BUFFER, normBufObj)
		glBufferData(GL_ARRAY_BUFFER, len(normals)*4, normals, GL_STATIC_DRAW)
		# assign data layout
		glVertexAttribPointer(vNormalId, 3, GL_FLOAT, False, 0, ctypes.c_void_p(0))
		glEnableVertexAttribArray(vNormalId)

		# scale matrices
		scaleMatrices.append(numpy.array(constructScaleMatrix(obj), dtype=numpy.float32))

	# shift along minus-z direction for 2 units
	trackball.mvMatrix[2][3] -= 2.0
	glUniformMatrix4fv(mvMatrixId, 1, True, trackball.mvMatrix)
	trackball.mvMatrix[2][3] += 2.0
	
	# glEnableClientState(GL_VERTEX_ARRAY)

	selectedObjId = 0
	glUniformMatrix4fv(scaleMatrixId, 1, False, scaleMatrices[selectedObjId])

	glClearColor(1.0, 1.0, 1.0, 1.0)
	glShadeModel(GL_SMOOTH)
	glClearDepth(1.0)
	glEnable(GL_DEPTH_TEST)


def display():
	global program
	global vertArrayObjs
	global scaleMatrixId
	global colorId

	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glUseProgram(program)

	glBindVertexArray(vertArrayObjs[selectedObjId])

	glUniform3f(colorId, 1.0, 0.0, 0.0)
	glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
	glDepthRange(DEPTHEPS, 1.0)
	glDrawElements(GL_TRIANGLES, len(objList[selectedObjId].faces)*3, GL_UNSIGNED_INT, ctypes.c_void_p(0))

	if showWire:
		glUniform3f(colorId, 0.0, 0.0, 0.0)
		glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
		glDepthRange(0.0, 1.0 - DEPTHEPS)
		glDrawElements(GL_TRIANGLES, len(objList[selectedObjId].faces)*3, GL_UNSIGNED_INT, ctypes.c_void_p(0))

	glutSwapBuffers()

def reshape(width, height):
	global projMatrixId, projectMatrix
	glViewport(0, 0, width, height)
	projectMatrix = constructPerspectiveMatrix(45.0, width/height, 0.1, 1000.0)
	glUniformMatrix4fv(projMatrixId, 1, False, projectMatrix)
	trackball.Resize(width, height, 45.0)

def keyboard(key, x, y):
	global selectedObjId
	global dkey, lkey
	global showWire, lighting
	if key == b'1':
		selectedObjId = 0
	elif key == b'2':
		selectedObjId = 1
	elif key == b'3':
		selectedObjId = 2
	elif key == b'd':
		if not dkey: 
			dkey = True
			showWire = not showWire
	elif key == b'l':
		if not lkey:
			lkey = True
			lighting = not lighting
	elif key == b'\x1b': sys.exit(0)
	if selectedObjId > len(sys.argv) - 2: selectedObjId = len(sys.argv) - 2
	glUniformMatrix4fv(scaleMatrixId, 1, False, scaleMatrices[selectedObjId])
	glUniform1i(lightingOnId, lighting)
	glutPostRedisplay()

def keyboardUp(key, x, y):
	global dkey, lkey
	if key == b'd':
		dkey = False
	elif key == b'l':
		lkey = False

def mouseClick(button, state, x, y):
	global mouseButton, mouseState
	global viewport
	mouseButton = button
	mouseState = state
	if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
		trackball.MousePress(Vector2D(x, y))
	elif (mouseButton == GLUT_RIGHT_BUTTON or mouseButton == GLUT_MIDDLE_BUTTON) and mouseState == GLUT_DOWN:
		viewport = numpy.array([1, 1, 1, 1], dtype=numpy.int32)
		glGetIntegerv(GL_VIEWPORT, viewport)
		z = numpy.array([1], dtype=numpy.float32)
		glReadPixels(x, viewport[3] - y, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT, z)
		if z == 1.0: mouseButton = -1; return
		mvMatrix = [1.0 if i % 5 == 0 else 0.0 for i in range(0, 16)]
		if mouseButton == GLUT_RIGHT_BUTTON: mvMatrix[14] = -2.0
		objCoord = gluUnProject(x, viewport[3] - y, z[0], \
				# numpy.reshape(numpy.transpose(numpy.dot(trackball.mvMatrix, numpy.transpose(numpy.reshape(scaleMatrices[selectedObjId], (4, 4))))), (1, 16)), \
				numpy.array(mvMatrix), \
				numpy.reshape(projectMatrix, (1, 16)), \
				viewport)
		trackball.MousePress(Vector2D(x, y), Vector3D(objCoord[0], objCoord[1], objCoord[2]))

def mouseMove(x, y):
	global mvMatrixId
	global viewport
	global scaleMatrices
	if mouseButton == GLUT_LEFT_BUTTON and mouseState == GLUT_DOWN:
		trackball.MouseMoveRotate(Vector2D(x, y))
	elif mouseButton == GLUT_RIGHT_BUTTON and mouseState == GLUT_DOWN:
		# gl_Position = projMatrix * mvMatrix * scaleMatrix * vec4(vPosition, 1);
		trackball.MouseMoveScale(Vector2D(x, y))
	elif mouseButton == GLUT_MIDDLE_BUTTON and mouseState == GLUT_DOWN:
		trackball.MouseMoveTranslate(Vector2D(x, y))

	trackball.mvMatrix[2][3] -= 2.0
	glUniformMatrix4fv(mvMatrixId, 1, True, trackball.mvMatrix)
	trackball.mvMatrix[2][3] += 2.0
	glutPostRedisplay()

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
glutMouseFunc(mouseClick)
glutMotionFunc(mouseMove)
glutMainLoop()
