# MeshLib
A simple 3d geometry and mesh library implemented by python

Currently, only 2-manifold triangular meshes (orientable/non-orientable) can be handled.

Supported format:
* .obj
* .off
* .m (Hugues Hoppe's format)
* .ply

## A Mesh-Viewer toolkit
A Mesh-Viewer toolkit (GLutils/GLWindowShader.py) is presented to show the loaded mesh. It's implemented by PyOpenGL using GLSL thus owning high display efficiency.

<div align="center">
<img src="figures/dragon.png" width="400" align="center"/>
<br>
<caption align="bottom">Figure 1. A 6 million faces dragon loaded by the toolkit. Still has interactive responses.</caption>
</div>

Operations:
* Left mouse + drag: Roate.
* Middle mouse + drag: Translate.
* Right mouse + drag: Zoom.
* 's' key: smooth/flat mode siwthc.
* 'd' key: wireframe on/of.
* 't' key: texture on/of (if texture exists).
