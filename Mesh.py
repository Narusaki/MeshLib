from MeshLib.Geometry import *

def LoadMesh(fileName, rmReduntVerts = False):
	'''
	Load a .obj file, return vertices, faces and normals
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
			v0 = int(parts[1].split('/')[0])-1
			v1 = int(parts[2].split('/')[0])-1
			v2 = int(parts[3].split('/')[0])-1
			if rmReduntVerts:
				v0 = realIndex[v0]; v1 = realIndex[v1]; v2 = realIndex[v2]
			faces.append([v0, v1, v2])
		# select normals
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

def SaveMesh(fileName, verts, faces, normals = [], textures = []):
	nVert = len(verts)
	nNorm = len(normals)
	nTex = len(textures)
	if nVert != nNorm: print('Warnning: nVert != nNorm')
	if nVert != nTex: print('Warnning: nVert != nTex')
	if nNorm != nTex: print('Warnning: nNorm != nTex')
	output = open(fileName, 'w')
	for i in range(0, nVert):
		output.write('v %f %f %f\n' % (verts[i][0], verts[i][1], verts[i][2]))
	for i in range(0, nNorm):
		output.write('vn %f %f %f\n' % (normals[i][0], normals[i][1], normals[i][2]))
	for i in range(0, nTex):
		output.write('vt %f %f\n' % (textures[i][0], textures[i][1]))
	for f in faces:
		if nNorm == 0 and nTex == 0:
			output.write('f %d %d %d\n' % (f[0]+1, f[1]+1, f[2]+1))
		elif nNorm != 0 and nTex == 0 or nNorm == 0 and nTex != 0:
			output.write('f %d/%d %d/%d %d/%d\n' % (f[0]+1, f[0]+1, f[1]+1, f[1]+1, f[2]+1, f[2]+1))
		else:
			output.write('f %d/%d/%d %d/%d/%d %d/%d/%d\n' % (f[0]+1, f[0]+1, f[0]+1, f[1]+1, f[1]+1, f[1]+1, f[2]+1, f[2]+1, f[2]+1))
	output.close()

if __name__ == '__main__':
	(verts, faces, normals, textures) = LoadMesh('bunny.unify.obj')
	print(len(verts), len(faces), len(normals), len(textures))
	SaveMesh('bunny.unify.out.obj', verts, faces, normals, textures)


