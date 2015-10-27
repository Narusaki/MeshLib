from MeshLib.Geometry import *

def LoadOBJFile(fileName, rmReduntVerts):
	'''
	Load a .obj file, return vertices, faces, normals and textures
	'''
	verts = []; faces = [];	normals = []; textures = []
	reduntLabels = []
	vert2index = dict()
	realIndex = []
	for curLine in open(fileName):
		curLine = curLine.rstrip()
		if curLine[:2] == 'v ':
			if rmReduntVerts and curLine in vert2index: 
				realIndex.append(vert2index[curLine])
				reduntLabels.append(True)
				continue 
			if rmReduntVerts: 
				vert2index[curLine] = len(verts)
				realIndex.append(len(verts))
				reduntLabels.append(False)

			parts = curLine.split(' ')
			parts = [p for p in parts if p != '']
			verts.append(Vector3D(float(parts[1]), float(parts[2]), float(parts[3])))
		elif curLine[:3] == 'vn ':
			parts = curLine.split(' ')
			parts = [p for p in parts if p != '']
			normals.append(Vector3D(float(parts[1]), float(parts[2]), float(parts[3])))
		elif curLine[:3] == 'vt ':
			parts = curLine.split(' ')
			parts = [p for p in parts if p != '']
			textures.append(Vector2D(float(parts[1]), float(parts[2])))
		elif curLine[:2] == 'f ':
			parts = curLine.split(' ')
			parts = [p for p in parts if p != '']
			del parts[0]
			vertList = [int(p.split('/')[0])-1 for p in parts]
			if rmReduntVerts:
				vertList = [realIndex[v] for v in vertList]
			faces.append(vertList)
	# select normals and textures -- here assume that the normals and textures have exact the same size as vertices
	normals_ = []; textures_ = []
	if rmReduntVerts:
		for i in range(0, len(normals)):
			if not reduntLabels[i]: 
				normals_.append(normals[realIndex[i]])
				textures_.append(textures[realIndex[i]])
	else:
		normals_ = normals
		textures_ = textures
	return (verts, faces, normals_, textures_)

def SaveOBJFile(fileName, verts, faces, normals, textures):
	'''
	Save mesh into .obj file
	'''
	nNorm = len(normals); nTex = len(textures)
	output = open(fileName, 'w')
	for v in verts:
		output.write('v %f %f %f\n' % (v[0], v[1], v[2]))
	for vn in normals:
		output.write('vn %f %f %f\n' % (vn[0], vn[1], vn[2]))
	for vt in textures:
		output.write('vt %f %f\n' % (vt[0], vt[1]))
	for f in faces:
		faceLine = 'f'
		if nNorm == 0 and nTex == 0:
			for fi in f: faceLine += ' ' + str(fi+1)
		elif nNorm != 0 and nTex == 0 or nNorm == 0 and nTex != 0:
			for fi in f: faceLine += ' ' + str(fi+1) + '/' + str(fi+1)
		else:
			for fi in f: faceLine += ' ' + (str(fi+1) + '/')*2 + str(fi+1)
		output.write(faceLine + '\n')
	output.close()
	pass

def LoadOFFFile(fileName, rmReduntVerts):
	'''
	Load a .off file, return vertices, faces, normals and textures
	'''
	file = open(fileName)
	file.readline()
	meshInfo = [int(i) for i in file.readline().split()]
	verts = []; faces = []; normals = []; textures = []
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
		verts.append(Vector3D(float(parts[0]), float(parts[1]), float(parts[2])))

	# load faces
	for i in range(0, meshInfo[1]):
		vertList = file.readline().rstrip().split(' ')
		vertList = [int(p) for p in vertList if p != '']
		del vertList[0]
		if rmReduntVerts:
			vertList = [realIndex[v] for v in vertList]
		faces.append(vertList)
	return (verts, faces, normals, textures)

def SaveOFFFile(fileName, verts, faces, normals, textures):
	'''
	Save mesh into .off file
	'''
	output = open(fileName, 'w')
	output.write('OFF\n')
	output.write('%d %d 0\n' % (len(verts), len(faces)))
	for v in verts:
		output.write('%f %f %f\n' % (v[0], v[1], v[2]))
	for f in faces:
		line = '%d' % len(f)
		for fi in f: line += ' ' + str(fi)
		line += '\n'
		output.write(line)
	output.close()

def LoadPLYFile(fileName, rmReduntVerts):
	# TODO: load .ply file
	pass

def SavePLYFile(fileName, verts, faces, normals, textures):
	# TODO: save .ply file
	pass

def LoadMesh(fileName, rmReduntVerts = False):
	'''
	Load mesh
	'''
	suffix = fileName[fileName.rfind('.'):].lower()
	if suffix == '.obj': return LoadOBJFile(fileName, rmReduntVerts)
	elif suffix == '.off': return LoadOFFFile(fileName, rmReduntVerts)
	elif suffix == '.ply': return LoadPLYFile(fileName, rmReduntVerts)


def SaveMesh(fileName, verts, faces, normals = [], textures = []):
	'''
	Save mesh
	'''
	nVert = len(verts)
	nNorm = len(normals)
	nTex = len(textures)
	if nVert != nNorm: print('Warnning: nVert != nNorm')
	if nVert != nTex: print('Warnning: nVert != nTex')
	if nNorm != nTex: print('Warnning: nNorm != nTex')

	suffix = fileName[fileName.rfind('.'):].lower()
	if suffix == '.obj': SaveOBJFile(fileName, verts, faces, normals, textures)
	elif suffix == '.off': SaveOFFFile(fileName, verts, faces, normals, textures)
	elif suffix == '.ply': SavePLYFile(fileName, verts, faces, normals, textures)

# test code
if __name__ == '__main__':
	# load .obj
	(verts, faces, normals, textures) = LoadMesh('bunny.unify.obj')
	print(len(verts), len(faces), len(normals), len(textures))
	SaveMesh('bunny.unify.out.obj', verts, faces, normals, textures)
	# load .off
	(verts, faces, normals, textures) = LoadMesh('test.off')
	print(len(verts), len(faces), len(normals), len(textures))
	SaveMesh('test.out.off', verts, faces, normals, textures)


