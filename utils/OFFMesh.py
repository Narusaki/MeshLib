from MeshLib.Geometry import *
import MeshLib.Mesh

def LoadOFFFile(fileName, rmReduntVerts):
	'''
	Load a .off file, return vertices, faces, normals and textures
	'''
	file = open(fileName)
	file.readline()
	meshInfo = [int(i) for i in file.readline().split()]
	verts = []; faces = []; normals = []; textures = []; lines = []
	vert2index = dict()
	realIndex = []

	# load vertices
	for i in range(0, meshInfo[0]):
		curLine = file.readline().rstrip()
		if rmReduntVerts and curLine in vert2index: 
			realIndex.append(vert2index[curLine])
			continue 
		if rmReduntVerts: 
			vert2index[curLine] = len(verts)
			realIndex.append(len(verts))

		parts = curLine.split(' ')
		parts = [p for p in parts if p != '']
		verts.append(MeshLib.Mesh.Vertex(Vector3D(float(parts[0]), float(parts[1]), float(parts[2]))))
		if len(parts) == 5:
			textures.append(Vector2D(float(parts[3]), float(parts[4])))

	# load faces
	for i in range(0, meshInfo[1]):
		vertList = file.readline().rstrip().split(' ')
		vertList = [int(p) for p in vertList if p != '']
		del vertList[0]
		if rmReduntVerts:
			vertList = [realIndex[v] for v in vertList]
		faces.append(MeshLib.Mesh.Face(vertList))
	return (verts, faces, normals, textures, lines)

def SaveOFFFile(fileName, verts, faces, normals, textures):
	'''
	Save mesh into .off file
	'''
	output = open(fileName, 'w')
	output.write('OFF\n')
	output.write('%d %d 0\n' % (len(verts), len(faces)))
	for v in verts:
		texStr = ''
		if len(textures) != 0:
			texStr = ' %f %f' % (textures[verts.index(v)][0], textures[verts.index(v)][1])
		output.write('%f %f %f%s\n' % (v[0], v[1], v[2], texStr))
	for f in faces:
		line = '%d' % len(f)
		for fi in f: line += ' ' + str(fi)
		line += '\n'
		output.write(line)
	output.close()
