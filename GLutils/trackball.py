from MeshLib.Mesh import *
from math import sqrt, acos, pi, exp, tan
import numpy

class TrackBall:
	def __init__(self, width, height):
		self.width = width / 2.0
		self.height = height / 2.0
		self.prevPoint2D = Vector2D()
		self.prevPoint3D = Vector3D()
		self.zoomCenter = Vector3D()
		self.mvMatrix = []
		for i in range(0, 16):
			self.mvMatrix.append(1.0 if i%5 == 0 else 0.0)
		self.mvMatrix = numpy.reshape(self.mvMatrix, (4, 4))
	
	def Resize(self, width, height):
		self.width = width / 2.0
		self.height = height / 2.0
	
	def __mapToSphere(self, v2d):
		v3d = Vector3D()
		v3d.x = (v2d.x - self.width) / self.width
		v3d.y = (self.height - v2d.y) / self.height
		v3dLen = v3d.length()
		if v3dLen < 1.0:
			v3d.z = sqrt(1.0 - v3dLen*v3dLen)
		else:
			v3d /= v3dLen
		return v3d

	def MouseMoveRotate(self, v2d):
		currentPoint2D = v2d
		currentPoint3D = self.__mapToSphere(v2d)
		axis = self.prevPoint3D ^ currentPoint3D
		if axis.length() < 1e-7: return
		axis.normalize()
		angle = acos(self.prevPoint3D * currentPoint3D)
		self.__rotate(axis, 2.0 * angle)
		self.prevPoint2D = currentPoint2D
		self.prevPoint3D = currentPoint3D
	
	def MouseMoveScale(self, v2d):
		currentPoint2D = v2d
		scaleFactor = exp(-(currentPoint2D - self.prevPoint2D).y/100.0)
		self.__scale(scaleFactor)
		self.prevPoint2D = currentPoint2D

	def MouseMoveTranslate(self, v2d):
		currentPoint2D = v2d
		shift2D = (self.zoomCenter.z) * (currentPoint2D - self.prevPoint2D) * tan(45.0 / 180.0 * pi / 2.0) / self.height
		shift2D.y = -shift2D.y
		self.__translate(Vector3D(-shift2D.x, -shift2D.y, 0.0))
		self.prevPoint2D = currentPoint2D

	def MousePress(self, v2d, v3d = Vector3D()):
		self.prevPoint2D = v2d
		self.prevPoint3D = self.__mapToSphere(v2d)
		self.zoomCenter = v3d
	
	def __rotate(self, axis, angle):
		shift = Vector3D()
		for i in range(0, 3):
			shift[i] = self.mvMatrix[i][3]
			self.mvMatrix[i][3] = 0.0
		rotateM = self.__constructRotateMatrix(axis, angle)
		self.mvMatrix = numpy.dot(rotateM, self.mvMatrix)
		for i in range(0, 3):
			self.mvMatrix[i][3] = shift[i]

	def __scale(self, scaleFactor):
		for i in range(0, 3):
			self.mvMatrix[i][3] -= self.zoomCenter[i]
		scaleM = self.__constructScaleMatrix(scaleFactor)
		self.mvMatrix = numpy.dot(scaleM, self.mvMatrix)
		for i in range(0, 3):
			self.mvMatrix[i][3] += self.zoomCenter[i]
	
	def __translate(self, shift):
		for i in range(0, 3):
			self.mvMatrix[i][3] += shift[i]

	def __constructRotateMatrix(self, axis, angle):
		c = cos(angle); s = sin(angle)
		ax = axis.x; ay = axis.y; az = axis.z
		m = []
		m.append([c+(1-c)*ax*ax, (1-c)*ax*ay-s*az, (1-c)*ax*az+s*ay, 0.0])
		m.append([(1-c)*ay*ax+s*az, c+(1-c)*ay*ay, (1-c)*ay*az-s*ax, 0.0])
		m.append([(1-c)*az*ax-s*ay, (1-c)*az*ay+s*ax, c+(1-c)*az*az, 0.0])
		m.append([0.0, 0.0, 0.0, 1.0])
		return numpy.reshape(m, (4, 4))

	def __constructShiftMatrix(self, shift):
		m = []
		for i in range(0, 16):
			m.append(1.0 if i%5 == 0 else 0.0)
		m[3] = shift.x; m[7] = shift.y; m[11] = shift.z
		return numpy.reshape(m, (4, 4))

	def __constructScaleMatrix(self, scaleFactor):
		m = []
		for i in range(0, 16):
			m.append(1.0 if i%5 == 0 else 0.0)
		m[0] = scaleFactor; m[5] = scaleFactor; m[10] = scaleFactor
		return numpy.reshape(m, (4, 4))
