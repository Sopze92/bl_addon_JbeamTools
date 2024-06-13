# Blender UNOFFICIAL Jbeam-Tools Addon

for BeamNG Modding

I was pretty unhappy with the official **Jbeam editor for Blender** so I'm making a simpler one with the tools i really need, unlike the official, this one supports **Ctrl-Z** as it works along with a standard blender mesh

any mesh can be non-destructively turned into a Jbeam-data-holder, it stores te JBeam data as vertex/edge attributes, currently the features are:

- assign node name directly on mesh vertices
- copy selected vertex / edges as Nodes / Beams respectively in a Jbeam-ready text format so you can paste them there directly, (+ respecting selection order!)
- 3 real-time visualization modes for nodes in all 3D views: **Normal**, **Names**, **Normal+Names**
- 1 real-time visualization mode for beams in all 3D views
- customizable real-time visualization settings such as colors, sizes and xray

#### coming up:

- toggle `l`, `ll`, `r`, `rr` on all selected node names
- automatic name numeration on selected nodes (by selection order)
- change node name but no numeration nor side
- duplicate node name / beam warning

#### NOT planned:
- collision tris