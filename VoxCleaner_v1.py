'''
VoxCleaner © 2021 by Farhan Shaikh is licensed under CC BY 4.0. 

License: CC-BY
Users are free to copy, adapt, remix, and redistribute the content - even commercially. User must give appropriate credit to the creator.
Read more about the license: https://creativecommons.org/licenses/by/4.0/

Thanks so much for your purchase and please feel free to tag me @TheStrokeForge on Instagram/Twitter and I’d love to see your work! Cheers!

'''

bl_info = {
    "name": "Vox Cleaner",
    "author": "Farhan Shaikh",
    "version": (1, 0),
    "blender": (2, 93, 0),
    "location": "View3D > Sidebar/N-Panel > Item > Vox Cleaner",
    "description": "Cleans voxel models in a single click!",
    "warning": "",
    "doc_url": "https://www.thestrokeforge.xyz/vox-cleaner",
    "category": "Clean Mesh",
    }
    
import bpy

class MyData:
    MainObj = None
    MainObjName = None
    DupeObj = None
    
    ButtonHeight = 1.5
    CleanModePaneHeight = 1
    RowSpacing = 1
    
class MyProperties(bpy.types.PropertyGroup):
    
    my_string : bpy.props.StringProperty(name= "Enter Text")
    
    ResX : bpy.props.IntProperty(name= "X", soft_min = 0, soft_max = 16384,default = 1024, description="""● X Resolution of the image to be generated""")
    ResY : bpy.props.IntProperty(name= "Y", soft_min = 0, soft_max = 16384,default = 1024, description="""● Y Resolution of the image to be generated""")
       
    BaseColor : bpy.props.FloatVectorProperty(name='Base Colour',subtype='COLOR_GAMMA',size=4, min=0.0, max=1.0,default = (0.05,0.4,0.3,1.0), description="""● Base color of the image to be generated
● This color won't be visible on the final cleaned model, is just for easier visibility""")
    
    AlphaBool: bpy.props.BoolProperty(name="Alpha", description="● Should the image to be generated have alpha?")
    
    CleanMode : bpy.props.EnumProperty(
        items = [("ez", "Lazy Clean", "", 1),("hard", "3-Step Clean", "", 2),],
        description="""● Mode of Cleaning.
● Use lazy clean for fast, one-click cleaning. Ideal for small voxel objects.
● Use 3-step clean for more control over each of the involved steps like custom UVs. 
● Mode of cleaning you're hovering on""")
        
    
def VColorMaterial(context):
    if bpy.data.materials.get("VColorMaterial") is None :
        #mat = bpy.data.materials.get("rustymetal")
        VMaterial = bpy.data.materials.new(name = "VColorMaterial")

        #edit the material
        VMaterial.use_nodes = True
        nodes = VMaterial.node_tree.nodes

        PrincipledBSDF = nodes.get('Principled BSDF')
        VertexColorNode = nodes.new(type = 'ShaderNodeVertexColor')
        VertexColorNode.location = (-280,80)

        Links = VMaterial.node_tree.links
        NewLink = Links.new(VertexColorNode.outputs[0], PrincipledBSDF.inputs[0])
    else:
        VMaterial = bpy.data.materials.get("VColorMaterial")
    
    #remove then add a new material to everyone
    for x in bpy.context.selected_objects:
        if x.type == 'MESH':
            x.data.materials.clear()
            x.data.materials.append(VMaterial)
    
    
def CleanModel(context):
    
    #set main object and its name
    MyData.MainObj = bpy.context.active_object
    MyData.MainObjName = bpy.context.active_object.name

    #Merge all vertices
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles()
    bpy.ops.object.editmode_toggle()
    
    #Fix Shading
    bpy.context.object.data.use_auto_smooth = False
    bpy.ops.object.shade_flat()
    
    #duplicate the main obj, set and name dupe 
    bpy.ops.object.duplicate()
    MyData.DupeObj = bpy.context.active_object
    MyData.DupeObj.name = MyData.MainObjName + "Cleaned"
    
    


    #Hide main obj
    MyData.MainObj.hide_set(True)                           
                           
    #Add and apply modifiers
    MyData.DupeObj.modifiers.new("MrCleaner",'DECIMATE')
    MyData.DupeObj.modifiers["MrCleaner"].decimate_type = 'DISSOLVE'
    MyData.DupeObj.modifiers["MrCleaner"].delimit = {'SHARP'}
    bpy.ops.object.modifier_apply(modifier="MrCleaner", report=True)


def EditMaterials(context):
    
    #remove then add a new material
    MyData.DupeObj.data.materials.clear()

    ImageMaterial = bpy.data.materials.new(name = MyData.DupeObj.name + "Material")
    MyData.DupeObj.data.materials.append(ImageMaterial)

    #edit the material
    ImageMaterial.use_nodes = True

    nodes = ImageMaterial.node_tree.nodes

    PrincipledBSDF = nodes.get('Principled BSDF')
    ImageTextureNode = nodes.new(type = 'ShaderNodeTexImage')
    ImageTextureNode.location = (-280,80)

    Links = ImageMaterial.node_tree.links
    NewLink = Links.new(ImageTextureNode.outputs[0], PrincipledBSDF.inputs[0])

    #Add new black 4k image texture 
    scene = context.scene
    mytool = scene.my_tool
    
    #bpy.ops.image.new(name=MyData.DupeObj.name + "Tex", width=mytool.ResX, height=mytool.ResY, color=(1.0, 1.0, 1.0, 1.0), alpha=mytool.AlphaBool, generated_type='BLANK', float=False, use_stereo_3d=False, tiled=False)
    
    GeneratedTex = bpy.data.images.new(MyData.DupeObj.name + "Tex", mytool.ResX, mytool.ResY, alpha = mytool.AlphaBool)
    bpy.data.images[MyData.DupeObj.name + "Tex"].generated_color = (mytool.BaseColor[0],mytool.BaseColor[1],mytool.BaseColor[2],mytool.BaseColor[3])
    ImageTextureNode.image = GeneratedTex

    #Set that image in the uv editor, if uv editor is available
    for area in bpy.context.screen.areas :
        if area.type == 'IMAGE_EDITOR' :
            area.spaces.active.image = GeneratedTex
            
    
            
    
def SmartUVProject(context):
    bpy.ops.object.editmode_toggle()    
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=0.523599, island_margin=0.0003, correct_aspect=True, scale_to_bounds=False)
    bpy.ops.object.editmode_toggle()
    
            
    

def Bake(context):
    MyData.MainObj.hide_set(False) 

    #Select objects in order
    MyData.MainObj.select_set(True)
    MyData.DupeObj.select_set(True)
    bpy.context.view_layer.objects.active = MyData.DupeObj

    #set bake settings
    bpy.context.scene.render.engine = 'CYCLES'
    bpy.context.scene.cycles.device = 'GPU'

    #set device type to cuda cus optix doesnt support baking
    bpy.context.preferences.addons["cycles"].preferences.compute_device_type = "CUDA" # or "OPENCL"

    # get_devices() to let Blender detects GPU device
    bpy.context.preferences.addons["cycles"].preferences.get_devices()
    print(bpy.context.preferences.addons["cycles"].preferences.compute_device_type)
    for d in bpy.context.preferences.addons["cycles"].preferences.devices:
        d["use"] = 1 # Using all devices, include GPU and CPU
        print(d["name"], d["use"])


    bpy.context.scene.cycles.bake_type = 'DIFFUSE'
    bpy.context.scene.render.bake.use_pass_direct = False
    bpy.context.scene.render.bake.use_pass_indirect = False
    bpy.context.scene.render.bake.use_clear = False
    bpy.context.scene.render.bake.use_selected_to_active = True
    bpy.context.scene.render.bake.cage_extrusion = 0.01
    bpy.context.scene.render.bake.max_ray_distance = 0.1

    bpy.ops.object.bake(type='DIFFUSE')

    MyData.MainObj.hide_set(True) 

class ApplyVColors(bpy.types.Operator):
    """● Applies a principled BSDF material with the mesh's vertex color as the base color.
● Used specifically for .ply meshes, as they have vertex color data present.
● Using .ply meshes is recommended for best results"""
    bl_idname = "voxcleaner.applyvertexcolors"
    bl_label = "Apply vertex colors"
    bl_options = {'UNDO'}

    def execute(self, context):
        
        VColorMaterial(context)
        
        self.report({'INFO'}, "Vertex color material applied to selected objects")
        
        return {'FINISHED'}


class EZClean(bpy.types.Operator):
    """● Click to lazy clean the selected model.
● Time taken depends on the complexity of the model and the resolution of the generated texture.
● Data specified in the image properties panel is used to generate the image"""
    bl_idname = "voxcleaner.oneclickclean"
    bl_label = "Clean Model"
    bl_options = {'UNDO'}

    def execute(self, context):
        
        
        CleanModel(context)
        EditMaterials(context)
        
        self.report({'INFO'}, "Geometry optimised and Material Set")
        
        
        SmartUVProject(context)
        
        self.report({'INFO'}, "UVs projected, Bake started")
        
        
        #self.report({'INFO'}, "Geometry optimised, bake started")
        Bake(context)
        
        self.report({'INFO'}, "Model cleaned!")
        
        
        return {'FINISHED'}


class PrepareForUV(bpy.types.Operator):
    """● Cleans the model geometry, sets up a new material and generates a new image texture. 
● Data specified in the image properties panel is used to generate the image. 
● Any remaining geometry cleaning can be done now"""
    
    bl_idname = "voxcleaner.prepareforuv"
    bl_label = "Prepare For UV"
    bl_options = {'UNDO'}

    def execute(self, context):
        CleanModel(context)
        EditMaterials(context)
        self.report({'INFO'}, "Geometry optimised and Material Set")
        return {'FINISHED'}
    
class AutoUV(bpy.types.Operator):
    """● Smart UV project with tweaked settings. 
● You can skip this step and do your own UVs for more precision as well"""
    bl_idname = "voxcleaner.autouv"
    bl_label = "Auto UV"
    bl_options = {'UNDO'}

    def execute(self, context):
        SmartUVProject(context)
        self.report({'INFO'}, "UVs projected")
        return {'FINISHED'}


class PostUVBake(bpy.types.Operator):
    """● Make sure that the UVs are done before this step.
● Auto bakes the texture from the original model to the cleaned model.
● Might take some time depending on the image resoultion"""
    bl_idname = "voxcleaner.postuvbake"
    bl_label = "Bake Texture"
    bl_options = {'UNDO'}

    def execute(self, context):
        Bake(context)
        self.report({'INFO'}, "Model cleaned!")
        return {'FINISHED'}


class UILayout(bpy.types.Panel):
    bl_label = "Vox Cleaner"
    bl_idname = "VoxCleaner_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Item"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        
        
        #Image Properties
        box = layout.box()
        box.label(text="Base Image Properties", icon="IMAGE_DATA")
        split = box.split()
        col = split.column()
        col.label(text="Resolution (px):")
        col.prop(mytool, "ResX")
        col.prop(mytool, "ResY")
        col = split.column()
        col.prop(mytool, "BaseColor")
        col.prop(mytool, "AlphaBool")
        
       

        #Mode Toggle
        box = layout.box()
        box.label(text="Procedures", icon="GREASEPENCIL")
        
        if bpy.context.mode == 'OBJECT':
            if len(bpy.context.selected_objects) == 1:
                if bpy.context.active_object == bpy.context.selected_objects[0]:
                    
                    if bpy.context.active_object.type == 'MESH':
                        row = box.row()
                        row.scale_y = MyData.CleanModePaneHeight
                        row.operator("voxcleaner.applyvertexcolors", icon = 'MATERIAL')

                        row = box.row()
                        row.scale_y = MyData.CleanModePaneHeight
                        row.prop(mytool, "CleanMode", expand=True)
                
                        if mytool.CleanMode == 'ez':
                            row = box.row()
                            row.scale_y = MyData.ButtonHeight
                            row.operator("voxcleaner.oneclickclean",icon = 'SOLO_ON')
                        
                        
                        if mytool.CleanMode == 'hard':
                            
                            col = box.column()
                            col.scale_y = MyData.ButtonHeight
                            
                            col.operator("voxcleaner.prepareforuv", icon = 'TOOL_SETTINGS')
                            
                            row = col.row()
                            row.scale_y = MyData.RowSpacing
                            
                            col.operator("voxcleaner.autouv", icon = 'UV')
                            
                            row = col.row()
                            row.scale_y = MyData.RowSpacing
                            
                            col.operator("voxcleaner.postuvbake",icon = 'RENDER_STILL')

                        

                    else:
                        row = layout.row()
                        box.label(icon="ERROR", text = "Selected object is not a mesh")
                    
                else:
                    row = box.row()
                    row.scale_y = MyData.CleanModePaneHeight
                    row.operator("voxcleaner.applyvertexcolors", icon = 'MATERIAL')
                    row = layout.row()
                    box.label(icon="LIGHT", text = "Select it properly to clean")
                    
            elif len(bpy.context.selected_objects) >= 1:
                MeshPresent = False
                for y in bpy.context.selected_objects:
                    if y.type == 'MESH':
                        MeshPresent = True

                if MeshPresent:
                    row = box.row()
                    row.scale_y = MyData.CleanModePaneHeight
                    row.operator("voxcleaner.applyvertexcolors", icon = 'MATERIAL')
                
                box.label(icon="ERROR", text = "Please select a single mesh to clean")
            else:
                box.label(icon="ERROR", text = "Please select a mesh")
        else:
            box.label(icon="ERROR", text = "Enter object mode to clean")

        
        
        
        
        
        
        


 
def register():
    bpy.utils.register_class(ApplyVColors)
    bpy.utils.register_class(MyProperties) 
    bpy.utils.register_class(EZClean)
    bpy.utils.register_class(PrepareForUV)
    bpy.utils.register_class(AutoUV)
    bpy.utils.register_class(PostUVBake)
    bpy.utils.register_class(UILayout)
        
    bpy.types.Scene.my_tool = bpy.props.PointerProperty(type= MyProperties)
 
def unregister():
    bpy.utils.unregister_class(ApplyVColors)
    bpy.utils.unregister_class(MyProperties)
    bpy.utils.unregister_class(EZClean)
    bpy.utils.unregister_class(PrepareForUV)
    bpy.utils.unregister_class(AutoUV)
    bpy.utils.unregister_class(PostUVBake)
    bpy.utils.unregister_class(UILayout)
    
    del bpy.types.Scene.my_tool
 
 
 
if __name__ == "__main__":
    register()