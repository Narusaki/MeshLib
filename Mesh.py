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
		self.color = Vector3D(1.0, 1.0, 1.0)
	
	def __getitem__(self, key):
		return self.pos[key]
	def __setitem__(self, key, value):
		self.pos[key] = value

# Face class
# fields: 
#     verts	---- vertices
#     edges	---- adjacent edges
#     normal	---- face normals
#     area	---- face area
class Face:
	def __init__(self, vertList):
		self.verts = vertList[:]
		self.edges = list(range(0, 3))
		self.normal = Vector3D()
		self.area = 0.0

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
		self.lines = []
		self.center = Vector3D()
		self.scale = 1.0
		self.mtllibFile = 'texture.mtl'

	def LoadMesh(self, fileName, rmReduntVerts = False, constructAdjacency = True):
		'''
		Load mesh
		'''
		self.__init__()
		suffix = fileName[fileName.rfind('.'):].lower()
		if suffix == '.obj': 
			(self.verts, self.faces, self.normals, self.textures, self.lines, self.mtllibFile) = MeshLib.utils.OBJMesh.LoadOBJFile(fileName, rmReduntVerts)
		elif suffix == '.off': 
			(self.verts, self.faces, self.normals, self.textures, self.lines) = MeshLib.utils.OFFMesh.LoadOFFFile(fileName, rmReduntVerts)
		elif suffix == '.ply':
			(self.verts, self.faces, self.normals, self.textures, self.lines) = MeshLib.utils.PLYMesh.LoadPLYFile(fileName, rmReduntVerts)
		elif suffix == '.m':
			(self.verts, self.faces, self.normals, self.textures, self.lines) = MeshLib.utils.MMesh.LoadMFile(fileName, rmReduntVerts)
		# construct adjacency
		if constructAdjacency: self.__construct()
		self.__calcNormals()
		# calculate bounding box
		vMax = Vector3D(-1e30, -1e30, -1e30)
		vMin = Vector3D(1e30, 1e30, 1e30)
		for v in self.verts:
			for i in range(0, 3):
				vMax[i] = max(vMax[i], v[i])
				vMin[i] = min(vMin[i], v[i])
		self.center = (vMax + vMin) / 2.0
		self.scale = -1.0
		for i in range(0, 3):
			self.scale = max(self.scale, vMax[i] - vMin[i])
		self.scale = 1.0 / self.scale
	
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
		if suffix == '.obj': MeshLib.utils.OBJMesh.SaveOBJFile(fileName, self.verts, self.faces, self.lines, self.normals, self.textures)
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
					assert self.edges[edgeIndex].faces[1] == -1, \
							'Non-manifold edge found! At least three faces (%d, %d, %d) share a common edge.' % \
							(self.edges[edgeIndex].faces[0], self.edges[edgeIndex].faces[1], fIndex)
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

			# move a boundary edge (if exist) to front
			boundaryEdgeIdx = -1
			for i in range(0, len(vertex.edges)):
				if self.edges[vertex.edges[i]].faces[0] == -1 or \
				self.edges[vertex.edges[i]].faces[1] == -1:
					boundaryEdgeIdx = i
					break
			if boundaryEdgeIdx != -1:
				tmp = vertex.edges[0]
				vertex.edges[0] = vertex.edges[boundaryEdgeIdx]
				vertex.edges[boundaryEdgeIdx] = tmp

			# now re-order the vertex's adjacent edges
			for i in range(0, len(vertex.edges)-1):
				edgeIndex0 = vertex.edges[i]
				found = False

				for j in range(i+1, len(vertex.edges)):
					edgeIndex1 = vertex.edges[j]
					f0 = self.edges[edgeIndex0].faces[0]
					f1 = self.edges[edgeIndex0].faces[1]
					f2 = self.edges[edgeIndex1].faces[0]
					f3 = self.edges[edgeIndex1].faces[1]
					if f0 == f2 and f0 != -1 or f0 == f3 and f0 != -1 or\
					f1 == f2 and f0 != -1 or f1 == f3 and f0 != -1:
						found = True
						break
				if found: 
					# swap
					tmp = vertex.edges[i+1]; vertex.edges[i+1] = vertex.edges[j]; vertex.edges[j] = tmp
				else:
					# find the next boundary edge in the remaining edges
					for j in range(i+1, len(vertex.edges)):
						if self.edges[vertex.edges[j]].faces[0] == -1 or \
						self.edges[vertex.edges[j]].faces[1] == -1:
							tmp = vertex.edges[i+1]
							vertex.edges[i+1] = vertex.edges[j]
							vertex.edges[j] = tmp
							break

			# set idxAtVert list
			for j in range(0, len(vertex.edges)):
				idx = 0 if self.edges[vertex.edges[j]][0] == vi else 1
				self.edges[vertex.edges[j]].idxAtVert[idx] = j
		# check for boundary edges and verts
		for edge in self.edges:
			if edge.faces[1] == -1: 
				edge.isBoundary = True
				self.verts[edge[0]].isBoundary = True
				self.verts[edge[1]].isBoundary = True

	def __calcNormals(self):
		# calculate face normals
		faceNormals = []
		for f in self.faces:
			vec0 = self.verts[f[1]].pos - self.verts[f[0]].pos
			vec1 = self.verts[f[-1]].pos - self.verts[f[0]].pos
			f.normal = vec0 ^ vec1
			f.area = f.normal.normalize() / 2.0
		# if no vertex normals, calculate them by average each vertex's adjacent faces' normals
		if len(self.normals) != 0: return
		# if adjacency is not built, then cannot calculate vertex normal
		if len(self.edges) == 0: return
		for v in self.verts:
			vNorm = Vector3D()
			totalArea = 0.0
			for i in range(0, len(v.edges)):
				e0 = v.edges[i]
				e1 = v.edges[(i+1)%len(v.edges)]
				fi = self.__edgeCoFace(e0, e1)
				if fi == -1: continue
				vNorm += self.faces[fi].normal * self.faces[fi].area
				totalArea += self.faces[fi].area
			if totalArea != 0.0:
				vNorm /= totalArea; 
				vNorm.normalize()
			self.normals.append(vNorm)

	# find common face of two edges
	def __edgeCoFace(self, e0, e1):
		for i in range(0, 2):
			for j in range(0, 2):
				if self.edges[e0].faces[i] == self.edges[e1].faces[j]:
					return self.edges[e0].faces[i]
		print(self.edges[e0][0], self.edges[e0][1])
		print(self.edges[e1][0], self.edges[e1][1])
		print(self.edges[e0].faces)
		print(self.edges[e1].faces)
		print(e0, e1)
		assert False, 'edge %d and %d does not have common face.' % (e0, e1)


	
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


