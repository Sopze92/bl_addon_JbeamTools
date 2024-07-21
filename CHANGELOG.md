# Blender UNOFFICIAL Jbeam-Tools Addon

### v0.2.0 (Current)

- [features] Node side handling tools (increment 'l' or 'r' and clear)
- [features] Node prefix naming tools
  - get: obtain the most used prefix on current selection into an UI field
  - set: assign the value from the UI field as prefix for current selection
- [features] Node numeral tools (recount, replace, invert, increment, decrement)
  - recount: counts from user defined value up, keeping gaps, uses selection order if available
  - replace: same as recount but doesn't keep gaps
  - invert: inverts the numeral order by selection numbers, NOT user selection order
  - increment/decrement: increments or decremens all selected node numerals by 1

Limitations:
- Due how Blender works, Shortest-Path and Loop-Select modes break user-selection order

---------------------

### v0.1.3
- [ui] Beam nodes renaming
- [ui] Changed panel distribution
- [ui] Cleaner and more functional
- [features] Added 8 ways to sort the selected elements when copying them to clipboard
- [FIXED] Nodes dissapearing while a Beam was selected
- [FIXED] Selecting with Shortest-Path or Loop-Select modes only copied a single element
- [FIXED] Changing selection mode (verts <-> edges) made Addon lose active selection

### v0.1.1b
- [FIXED] nodes/beams not copying 
- [vis] visual selection feedback for Nodes and Beams, similar to Blender's

### v0.1.1

- [ui] options for styling are now in a separate UI panel
- [beam vis] adjustable render zTest function
- [vis] real-time beam renderer with adjustable size and color
- [vis] save/load renderer active state in blend file
- [vis] opacity for all renderer elements
- [node vis] node point renderer with adjustable size and color
- [node text vis] correct rendering z-sort
- [node text vis] adjustable font size

### v0.1.0 -- Initital Release

- naming nodes
- real-time node visualization (all viewports)
- ccopy selected vertex / edges as jbeam-ready Nodes / Beams with selection order
