from MeshLib.Geometry import *
from MeshLib.OBJMesh import *
from MeshLib.OFFMesh import *
from MeshLib.PLYMesh import *

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


