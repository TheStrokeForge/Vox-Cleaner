# Vox-Cleaner
Single-Click voxel model cleaner add-on for Blender!

How does it work:
The script is essentially made to work with Blender, and it cleans planar surfaces with the help of Blender's decimate modifier. 
Here's how it goes :

1. Duplicate the original model, add a decimate modifier with Planar mode on the duplicate.
2. Add a new material to the Duplicate model with a generated image texture having specified properties
3. Smart UV project the duplicate model to generate a UV layer
4. Bake colors from the Original model to the duplicate model with predefined settings, as most of the voxel models dont have much different bake settings.
5. That's how your model is Much more optimized!


Have a look at it in action here - 
https://youtu.be/Lqd8AA5sILo

More info on my website -
https://www.thestrokeforge.xyz



