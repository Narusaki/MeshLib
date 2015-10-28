from MeshLib.Geometry import *
import MeshLib.Mesh

def LoadMFile(fileName, rmReduntVerts):
	'''
	Load a .m file, return vertices, faces, normals and textures.
	Right now only vertices and faces can be loaded.
	'''
	verts = []; faces = [];	normals = []; textures = []
	vert2index = dict()
	vertMap = dict()
	realIndex = []
	for curLine in open(fileName):
		curLine = curLine.rstrip()
		parts = [p for p in curLine.split(' ') if p != '']
		if len(parts) < 5: continue
		if parts[0] == 'Vertex':
			curLine = parts[2] + ' ' + parts[3] + ' ' + parts[4]
			if rmReduntVerts and curLine in vert2index:
				vertMap[int(parts[1])] = vert2index[curLine]
				continue
			if rmReduntVerts:
				vert2index[curLine] = len(verts)
			vertMap[int(parts[1])] = len(verts)
			verts.append(MeshLib.Mesh.Vertex(Vector3D(float(parts[2]), float(parts[3]), float(parts[4]))))
		elif parts[0] == 'Face':
			vertList = [int(p) for p in parts[2:]]
			vertList = [vertMap[v] for v in vertList]
			faces.append(MeshLib.Mesh.Face(vertList))
	return (verts, faces, normals, textures)

def SaveMFile(fileName, verts, faces, normals, textures):
	'''
	Save mesh into .obj file
	'''
	output = open(fileName, 'w')
	for vi in range(0, len(verts)):
		output.write('Vertex %d %f %f %f\n' % (vi+1, verts[vi][0], verts[vi][1], verts[vi][2]))
	for fi in range(0, len(faces)):
		output.write('Face %d %d %d %d\n' % (fi+1, faces[fi][0]+1, faces[fi][1]+1, faces[fi][2]+1))
