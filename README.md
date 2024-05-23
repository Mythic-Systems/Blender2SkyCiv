# Blender2SkyCiv
A little script that turns an object into a SkyCiv project with wind and live loads. Dreaming of a larger system, maybe with a little help from my friends.

Open the .blend, go to Scripting tab, alt-P to run script

Edit shape in Edit Mode

Any node at elevation 0 gets an anchor

Any face gets a wind load or a live load


## Todos 
Visualization
 - show loads and anchors before sending to SkyCiv (probably as objects you can toggle on off and adjust)
 - show results from SkyCiv
Engineering
 - node type editing in Blender
 - export all to pdf from Blender (minimal style to be added to your own titleblock)
 - get asce-7 loads from SkyCiv
 - section viewer/editor/library
Algorithmic
 - convert IFC to stick model

 ## Why??
 Because I love Blender. 
 Because I didn't want to write my own 3d statics solver. 
 Because a web interface for building structures will probably never be good enough. 
 Because it only took a day.
 Because it's free(ish).
 Why not?