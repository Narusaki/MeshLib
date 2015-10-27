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
