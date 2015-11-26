from math import sqrt, pi, cos, sin

class Vector2D:
	'''
	2D Vector class
	'''

	def __init__(self, x0 = 0.0, y0 = 0.0):
		self.x = float(x0)
		self.y = float(y0)
	def __str__(self):
		return '(%f, %f)' % (self.x, self.y)
	
	# mathematical operations
	# addition
	def __add__(self, right):
		return Vector2D(self.x+right.x, self.y+right.y)
	# substraction
	def __sub__(self, right):
		return Vector2D(self.x-right.x, self.y-right.y)
	# dot product
	def __mul__(self, right):
		if isinstance(right, Vector2D): 
			return self.x*right.x + self.y*right.y
		else: 
			return Vector2D(self.x*right, self.y*right)
	# division
	def __div__(self, right):
		return Vector2D(self.x/right, self.y/right)
	def __truediv__(self, right):
		return Vector2D(self.x/right, self.y/right)
	# cross product
	def __xor__(self, right):
		return self.x*right.y-self.y*right.x

	# inplace mathematical operations
	def __iadd__(self, right):
		self = self + right
		return self
	def __isub__(self, right):
		self = self - right
		return self
	def __imul__(self, right):
		self = self * right
		return self
	def __idiv__(self, right):
		self = self / right
		return self
	def __itruediv__(self, right):
		self = self / right
		return self
	def __ixor__(self, right):
		self = self ^ right
		return self

	# right-hand multiplication
	def __rmul__(self, left):
		return Vector2D(left*self.x, left*self.y)

	def length2(self):
		return self.x*self.x + self.y*self.y
	def length(self):
		return sqrt(self.length2())
	def normalize(self):
		vLen = self.length()
		self.x /= vLen; self.y /= vLen; 
		return vLen
	
	# index operations
	def __getitem__(self, key):
		if key == 0: return self.x
		elif key == 1: return self.y
		else: return None

	def __setitem__(self, key, value):
		if key == 0: self.x = float(value)
		elif key == 1: self.y = float(value)
class Vector3D:
	'''
	3D Vector class
	'''

	def __init__(self, x0 = 0.0, y0 = 0.0, z0 = 0.0):
		self.x = float(x0)
		self.y = float(y0)
		self.z = float(z0)
	def __str__(self):
		return '(%f, %f, %f)' % (self.x, self.y, self.z)
	
	# mathematical operations
	# addition
	def __add__(self, right):
		return Vector3D(self.x+right.x, self.y+right.y, self.z+right.z)
	# substraction
	def __sub__(self, right):
		return Vector3D(self.x-right.x, self.y-right.y, self.z-right.z)
	# dot product
	def __mul__(self, right):
		if isinstance(right, Vector3D): 
			return self.x*right.x + self.y*right.y + self.z*right.z
		else: 
			return Vector3D(self.x*right, self.y*right, self.z*right)
	# division
	def __div__(self, right):
		return Vector3D(self.x/right, self.y/right, self.z/right)
	def __truediv__(self, right):
		return Vector3D(self.x/right, self.y/right, self.z/right)
	# cross product
	def __xor__(self, right):
		return Vector3D(self.y*right.z-self.z*right.y, self.z*right.x-self.x*right.z, self.x*right.y-self.y*right.x)

	# inplace mathematical operations
	def __iadd__(self, right):
		self = self + right
		return self
	def __isub__(self, right):
		self = self - right
		return self
	def __imul__(self, right):
		self = self * right
		return self
	def __idiv__(self, right):
		self = self / right
		return self
	def __itruediv__(self, right):
		self = self / right
		return self
	def __ixor__(self, right):
		self = self ^ right
		return self

	# right-hand multiplication
	def __rmul__(self, left):
		return Vector3D(left*self.x, left*self.y, left*self.z)

	def length2(self):
		return self.x*self.x + self.y*self.y + self.z*self.z
	def length(self):
		return sqrt(self.length2())
	def normalize(self):
		vLen = self.length()
		if vLen == 0.0: return 0.0
		self.x /= vLen; self.y /= vLen; self.z /= vLen
		return vLen
	
	# index operations
	def __getitem__(self, key):
		if key == 0: return self.x
		elif key == 1: return self.y
		elif key == 2: return self.z
		else: return None

	def __setitem__(self, key, value):
		if key == 0: self.x = float(value)
		elif key == 1: self.y = float(value)
		elif key == 2: self.z = float(value)

def Rotate(verts, ax, ay, az, angle):
	'''
	Rotate a group of the vertices
	'''
	angle = angle / 180.0 * pi
	c = cos(angle); s = sin(angle)
	m = []
	row = [c+(1-c)*ax*ax, (1-c)*ax*ay-s*az, (1-c)*ax*az+s*ay]
	m.append(row)
	row = [(1-c)*ay*ax+s*az, c+(1-c)*ay*ay, (1-c)*ay*az-s*ax]
	m.append(row)
	row = [(1-c)*az*ax-s*ay, (1-c)*az*ay+s*ax, c+(1-c)*az*az]
	m.append(row)

	newVerts = verts[:]

	for i in range(0, len(newVerts)):
		newV = Vector3D()
		for j in range(0, 3):
			newV[j] = 0.0
			for k in range(0, 3):
				newV[j] += m[j][k] * newVerts[i][k]
		newVerts[i] = newV
	return newVerts

if __name__ == '__main__':
	v0 = Vector3D(1, 2, 3)
	v1 = Vector3D(4, 5, 6)

	print(v0); print(v1)
	print(v0 + v1)
	print(v0 - v1)
	print(v0 * v1)
	print(v0 * 3)
	print(v0 * 3.0)
	print(v0 / 3)
	print(v0 / 3.0)
	print(v0 ^ v1)

	print(v0[0], v0[1], v0[2])
	v0[0] = 10
	print(v0[0], v0[1], v0[2])

	v0 += v1
	print(v0)

	print(v0.length2())
	print(v0.length())

	v0 = Vector3D()
	print(v0)
	

