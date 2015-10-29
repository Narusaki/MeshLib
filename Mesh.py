from MeshLib.Geometry import *
import MeshLib.utils.OBJMesh
import MeshLib.utils.OFFMesh
import MeshLib.utils.PLYMesh
import MeshLib.utils.MMesh

# Vertex class
# fields: 
#     pos	---- geometry position
#     edges	---- adjacent edges
#     isBoundary---- whether is a boundary vertex
class Vertex:
	def __init__(self, point):
		self.pos = point
		self.edges = []
		self.isBoundary = False
	
	def __getitem__(self, key):
		return self.pos[key]
	def __setitem__(self, key, value):
		self.pos[key] = value

# Face class
# fields: 
#     verts	---- vertices
#     edges	---- adjacent edges
class Face:
	def __init__(self, vertList):
		self.verts = vertList[:]
		self.edges = list(range(0, 3))

	def __getitem__(self, key):
		return self.verts[key]
	def __setitem__(self, key, value):
		self.verts[key] = value
	def __len__(self):
		return len(self.verts)

# Edge class
# fields: 
#     verts	---- two end points
#     faces	---- adjacent faces; for boundary edge, there is one adjacent faces that is -1
#     idxAtVert	---- index at adjacent vertices's edge list
#     isBoundary---- whether is a boundary edge
class Edge:
	def __init__(self, vertPair):
		self.verts = vertPair[:]
		self.faces = [-1, -1]
		self.idxAtVert = [-1, -1]
		self.isBoundary = False

	def __getitem__(self, key):
		return self.verts[key]
	def __setitem__(self, key, value):
		self.verts[key] = value

class Mesh:
	def __init__(self):
		self.verts = []
		self.faces = []
		self.edges = []
		self.normals = []
		self.textures = []

	def LoadMesh(self, fileName, rmReduntVerts = False):
		'''
		Load mesh
		'''
		self.__init__()
		suffix = fileName[fileName.rfind('.'):].lower()
		if suffix == '.obj': 
			(self.verts, self.faces, self.normals, self.textures) = MeshLib.utils.OBJMesh.LoadOBJFile(fileName, rmReduntVerts)
		elif suffix == '.off': 
			(self.verts, self.faces, self.normals, self.textures) = MeshLib.utils.OFFMesh.LoadOFFFile(fileName, rmReduntVerts)
		elif suffix == '.ply':
			(self.verts, self.faces, self.normals, self.textures) = MeshLib.utils.PLYMesh.LoadPLYFile(fileName, rmReduntVerts)
		elif suffix == '.m':
			(self.verts, self.faces, self.normals, self.textures) = MeshLib.utils.MMesh.LoadMFile(fileName, rmReduntVerts)
		self.__construct()
	
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
		if suffix == '.obj': MeshLib.utils.OBJMesh.SaveOBJFile(fileName, self.verts, self.faces, self.normals, self.textures)
		elif suffix == '.off': MeshLib.utils.OFFMesh.SaveOFFFile(fileName, self.verts, self.faces, self.normals, self.textures)
		elif suffix == '.ply': MeshLib.utils.PLYMesh.SavePLYFile(fileName, self.verts, self.faces, self.normals, self.textures)
		elif suffix == '.m': MeshLib.utils.MMesh.SaveMFile(fileName, self.verts, self.faces, self.normals, self.textures)
	
	# constructing adjacent structure
	def __construct(self):
		print('Constructing...')
		for fIndex in range(0, len(self.faces)):
			f = self.faces[fIndex]
			for i in range(0, len(f)):
				v0 = f[i]; v1 = f[(i+1)%len(f)]
				# check if edge has already existed
				existEdge = -1

				for edgeIndex in self.verts[v0].edges:
					edge = self.edges[edgeIndex]
					if edge[0] == v0 and edge[1] == v1 or edge[0] == v1 and edge[1] == v0:
						existEdge = edgeIndex
						break

				if existEdge != -1:
					edgeIndex = existEdge
					self.edges[edgeIndex].faces[1] = fIndex
				else:
					edgeIndex = len(self.edges)
					curEdge = Edge((v0, v1))
					curEdge.faces[0] = fIndex
					self.edges.append(curEdge)
					self.verts[v0].edges.append(edgeIndex)
					self.verts[v1].edges.append(edgeIndex)

				self.faces[fIndex].edges[i] = edgeIndex
		# up to now, Face and Edge are all filled
		# Vertex's edges are filled but not ordered
		# now re-order Vertex's edges
		vi = -1
		for vertex in self.verts:
			vi += 1
			# isolated vertex, skip
			if len(vertex.edges) == 0: continue
			boundaryStart = -1
			for i in range(0, len(vertex.edges)-1):
				edgeIndex0 = vertex.edges[i]
				found = False
				coFace = -1
				for j in range(i+1, len(vertex.edges)):
					edgeIndex1 = vertex.edges[j]
					if self.edges[edgeIndex0].faces[0] == self.edges[edgeIndex1].faces[0] or \
						self.edges[edgeIndex0].faces[0] == self.edges[edgeIndex1].faces[1] or \
						self.edges[edgeIndex0].faces[1] == self.edges[edgeIndex1].faces[0] or \
						self.edges[edgeIndex0].faces[1] == self.edges[edgeIndex1].faces[1]:
							found = True
							if self.edges[edgeIndex0].faces[0] == self.edges[edgeIndex1].faces[0]:
								coFace = self.edges[edgeIndex0].faces[0]
							elif self.edges[edgeIndex0].faces[0] == self.edges[edgeIndex1].faces[1]:
								coFace = self.edges[edgeIndex0].faces[0]
							elif self.edges[edgeIndex0].faces[1] == self.edges[edgeIndex1].faces[0]:
								coFace = self.edges[edgeIndex0].faces[1]
							elif self.edges[edgeIndex0].faces[1] == self.edges[edgeIndex1].faces[1]:
								coFace = self.edges[edgeIndex0].faces[1]
							break
				if not found: print('Error occurs while re-order edges around a vertex!'); return
				# swap
				tmp = vertex.edges[i+1]; vertex.edges[i+1] = vertex.edges[j]; vertex.edges[j] = tmp

				if coFace == -1:
					boundaryStart = i+1
			# if is boundary vertex, shift edges to start from boundary edges
			if boundaryStart != -1:
				vertex.edges = vertex.edges[boundaryStart:] + vertex.edges[:boundaryStart]
			# set idxAtVert list
			for j in range(0, len(vertex.edges)):
				idx = 0 if self.edges[vertex.edges[j]][0] == vi else 1
				self.edges[vertex.edges[j]].idxAtVert[idx] = j
		# check for boundary edges and verts
		for edge in self.edges:
			if edge.faces[1] == -1: 
				edges.isBoundary = True
				verts[edges[0]].isBoundary = True
				verts[edges[1]].isBoundary = True
	
	# test code
if __name__ == '__main__':
	# load .obj
	mesh = Mesh()
	mesh.LoadMesh('bunny.unify.obj', True)
	print(len(mesh.verts), len(mesh.faces), len(mesh.normals), len(mesh.textures))
	mesh.SaveMesh('bunny.unify.out.obj')
	# load .off
	mesh.LoadMesh('test.off', True)
	print(len(mesh.verts), len(mesh.faces), len(mesh.normals), len(mesh.textures))
	mesh.SaveMesh('test.out.off')
	# load .m
	mesh.LoadMesh('fandisk.m', True)
	print(len(mesh.verts), len(mesh.faces), len(mesh.normals), len(mesh.textures))
	mesh.SaveMesh('fandisk.out.m')
	mesh.SaveMesh('fandisk.out.obj')
	# load .ply
	mesh.LoadMesh('test.ply', True)
	print(len(mesh.verts), len(mesh.faces), len(mesh.normals), len(mesh.textures))
	mesh.SaveMesh('test.out.ply')


