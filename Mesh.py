from MeshLib.Geometry import *
from MeshLib.OBJMesh import *
from MeshLib.OFFMesh import *
from MeshLib.PLYMesh import *

class Mesh:

	def __init__(self):
		self.verts = []
		self.faces = []
		self.normals = []
		self.textures = []

	def LoadMesh(self, fileName, rmReduntVerts = False):
		'''
		Load mesh
		'''
		self.__init__()
		suffix = fileName[fileName.rfind('.'):].lower()
		if suffix == '.obj': 
			(self.verts, self.faces, self.normals, self.textures) = LoadOBJFile(fileName, rmReduntVerts)
		elif suffix == '.off': 
			(self.verts, self.faces, self.normals, self.textures) = LoadOFFFile(fileName, rmReduntVerts)
		elif suffix == '.ply':
			(self.verts, self.faces, self.normals, self.textures) = LoadPLYFile(fileName, rmReduntVerts)
	
	
	def SaveMesh(self, fileName):
		'''
		Save mesh
		'''
		nVert = len(self.verts)
		nNorm = len(self.normals)
		nTex = len(self.textures)
		if nVert != nNorm: print('Warnning: nVert != nNorm')
		if nVert != nTex: print('Warnning: nVert != nTex')
		if nNorm != nTex: print('Warnning: nNorm != nTex')
	
		suffix = fileName[fileName.rfind('.'):].lower()
		if suffix == '.obj': SaveOBJFile(fileName, self.verts, self.faces, self.normals, self.textures)
		elif suffix == '.off': SaveOFFFile(fileName, self.verts, self.faces, self.normals, self.textures)
		elif suffix == '.ply': SavePLYFile(fileName, self.verts, self.faces, self.normals, self.textures)
	
	# test code
if __name__ == '__main__':
	# load .obj
	mesh = Mesh()
	mesh.LoadMesh('bunny.unify.obj')
	print(len(mesh.verts), len(mesh.faces), len(mesh.normals), len(mesh.textures))
	mesh.SaveMesh('bunny.unify.out.obj')
	# load .off
	mesh.LoadMesh('test.off')
	print(len(mesh.verts), len(mesh.faces), len(mesh.normals), len(mesh.textures))
	mesh.SaveMesh('test.out.off')


