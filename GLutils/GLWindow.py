import OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from MeshLib.Mesh import *
import sys, os

OpenGL.ERROR_CHECKING = False

objList = []
dkey = False
showWire = True
DEPTHEPS = 0.0001

if len(sys.argv) < 2:
	print('USAGE: [.py] [mesh1] ...')
	sys.exit(-1)

for i in range(1, len(sys.argv)):
	mesh = Mesh()
	mesh.LoadMesh(sys.argv[i])
	objList.append(mesh)
	
def initGL():
	glClearColor(1.0, 1.0, 1.0, 1.0)
	glShadeModel(GL_SMOOTH)
	glClearDepth(1.0)
	glEnable(GL_DEPTH_TEST)

	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()

	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()

def RenderMeshes():
	for obj in objList:
		glPushMatrix()
		glScale(obj.scale, obj.scale, obj.scale)
		glTranslate(-obj.center.x, -obj.center.y, -obj.center.z)
		for f in obj.faces:
			glBegin(GL_POLYGON)
			for vi in f:
				glVertex3d(obj.verts[vi][0], obj.verts[vi][1], obj.verts[vi][2])
			glEnd()
		glPopMatrix()

def display():
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()
	glTranslate(0.0, 0.0, -2.0)
	# glRotate(90.0, 1.0, 0.0, 0.0)
	glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
	glColor3ub(255, 0, 0)
	glDepthRange(DEPTHEPS, 1.0)
	RenderMeshes()
	if showWire:
		glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
		glColor3ub(0, 0, 0)
		glDepthRange(0.0, 1.0 - DEPTHEPS)
		RenderMeshes()
	glutSwapBuffers()

def reshape(width, height):
	glViewport(0, 0, width, height)
	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()
	gluPerspective(45.0, width/height, 0.1, 100.0)
	glMatrixMode(GL_MODELVIEW)
	glLoadIdentity()

def keyboard(key, x, y):
	global dkey
	global showWire
	if key == b'd':
		if not dkey:
			dkey = True
			showWire = not showWire
	glutPostRedisplay()

def keyboardUp(key, x, y):
	global dkey
	if key == b'd':
		dkey = False
	glutPostRedisplay()

glutInit(sys.argv)
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGBA | GLUT_DEPTH)
glutInitWindowSize(640, 640)
glutCreateWindow(b'Narusaki\'s GLWindow')
initGL()
glutDisplayFunc(display)
glutReshapeFunc(reshape)
glutKeyboardFunc(keyboard)
glutKeyboardUpFunc(keyboardUp)
glutMainLoop()
