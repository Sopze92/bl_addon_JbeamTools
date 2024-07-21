# Blender UNOFFICIAL Jbeam-Tools Addon

for BeamNG Modding

I was pretty unhappy with the official **Jbeam editor for Blender** so I'm making a simpler one with the tools i really need, unlike the official, this one supports **Ctrl-Z** as it works along with a standard blender mesh

any mesh can be non-destructively turned into a Jbeam-data-holder, it stores te JBeam data as vertex/edge attributes, currently the features are:

- Change selected nodes side (+left, +right, clear)
- Change selected nodes numbers (recount, replace, invert, increment, decrement), (use selection order when available)
- Change selected nodes prefix
- Assign node name directly on mesh vertices
- Copy selected vertex / edges as Nodes / Beams respectively in a Jbeam-ready text format so you can paste them there directly, (+ respecting selection order!)
- Ability to sort the selection before copying it to clipboard in 8 different modes: (node names must follow **BeamNG** node naming convention for automatic sorting to work)
    ```
    L>R-Asc: Ascending numeral, blocks from Left to Right
    L>R-Desc: Descending numeral, blocks from Left to Right
    R>L-Asc: Ascending numeral, blocks from Right to Left
    R>L-Desc: Descending numeral, blocks from Right to Left

    Asc-L>R: Blocks from ascending numeral, Left to Right
    Desc-L>R: Blocks from descending numeral, Left to Right
    Asc-L>R: Blocks from ascending numeral, Right to Left
    Desc-L>R: Blocks from descending numeral, Right to Left
    ```
- 3 real-time visualization modes for nodes in all 3D views: **Normal**, **Names**, **Normal+Names**
- 1 real-time visualization mode for beams in all 3D views
- Customizable real-time visualization settings such as colors, sizes and xray

#### someday (maybe):
- duplicate node name / beam warning
- load existent .jbeam files

#### NOT planned:
- collision tris