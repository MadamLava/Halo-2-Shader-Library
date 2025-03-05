import bpy
import os
import uuid

from io_scene_halo import global_functions
from io_scene_halo.global_functions import shader_processing
#from global_functions import shader_processing

from bpy.types import (
        Panel,
        Operator,
        PropertyGroup
        )

from bpy.props import (
        IntProperty,
        BoolProperty,
        EnumProperty,
        FloatProperty,
        StringProperty,
        PointerProperty,
        FloatVectorProperty
        )

bl_info = {
    "name": "Halo 2 Shader Library Generator",
    "author": "MadamLava",
    "blender": "4, 0, 0",
    "category": "Import-Export"
}    

class H2SL_AddonPrefs(bpy.types.AddonPreferences):
    bl_idname = __name__
    halo_2_asset_library_path: StringProperty(
        name = "Halo 2 Asset Library Path",
        description = "Path to the Asset Library directory",
        subtype = "FILE_PATH",
    )
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        row = col.row()
        row.label(text='Halo 2 Asset Library Path:')
        row.prop(self, "halo_2_asset_library_path", text='')

class Halo_H2AssetPropertiesGroup(PropertyGroup):
    clear_scene: BoolProperty(
        name = "Clear Entire Scene",
        description = "DO NOT USE IF YOU DO NOT KNOW WHAT YOU ARE DOING.\n\nWill completely obliterate all objects, materials and bitmaps associated with the scene when running generation. You shouldn't need to use this",
        default = False,
    )
    
    regen_existing: BoolProperty(
        name = "Regenerate Existing Materials",
        description = "Only enable if you want to refresh already-generated materials, which you shouldn't need to, because it'll take longer/might mess up edits you've made",
        default = False,
    )
    
    use_shader_collections: BoolProperty(
        name = "Use Shader Collections",
        description = "Attempt to assign a shader collection prefix to imported shaders to avoid duplicates and speed up generation. Highly recommended to leave enabled",
        default = True,
    )

# Borrowed from General's toolkit, global_functions.py because it doesnt count as imported and Im lazy, sorry
def string_empty_check(string):
    is_empty = False
    
    if not string == None and (len(string) == 0 or string.isspace()):
        is_empty = True
    
    return is_empty

def generate_sc_dict():
    # Parse the shader collections file into a more readable python dict, thank god its whitespace formatted
    # This mostly reuses the parsing method General uses
    
    sc_dict = {} # key = collection prefix, value = folder path
    sc_path = os.path.join(bpy.context.preferences.addons["io_scene_halo"].preferences.halo_2_tag_path, r"scenarios\shaders\shader_collections.shader_collections")
    
    if os.path.isfile(sc_path):
        print("Caching shader collections...")
        
        sc_file = open(sc_path, "r")
        for line in sc_file.readlines():
            if not string_empty_check(line) and not line.startswith(";"):
                split_result = line.split()
                if len(split_result) == 2:
                    prefix = split_result[0]
                    path = split_result[1]
                    
                    # normally this would be prefix as key and path as value, but reversing it is convenient for getting the prefix from the path instead
                    sc_dict[path] = prefix
                    
        # print a pretty dictionary for the log <3
        #print("\n".join("{0} {1}".format(k, v)  for k,v in sc_dict.items()))
        
    else:
        print("!!! WARNING: SHADER COLLECTIONS FILE NOT FOUND !!!")
    
    return sc_dict

def assign_shader_collection(shader, shaderpath, sc_dict):
    # Take the shader name so it can be returned, the shaderpath must start in scenarios\shaders, and is used to crossreference.
    # This would be cleaner if shader collection file depth matched the actual directory depth, but sucks to suck! dirty loops win again
    
    # Make sure it exists - if not hit the bricks
    if not sc_dict:
        print("!!! Shader Collection Dict didn't generate!")
        return shader
    
    prefix = ""
    
    # Check every collection in order to see if its a good match with substrings, ugly but the shadercollections are sequential anyways so this still will find the "best" match
    for collection in sc_dict:
        if collection in shaderpath:
            prefix = sc_dict[collection]
    
    # Assign sc prefix afterwards
    if prefix != "":
        print("Collection found for " + shader)
        
        shader = prefix + " " + shader
    else:
        print(shader + " was not sorted into a collection!")
    
    return shader

def generate_shader_batch(c_path):
    
        # Iterate over the tags folder to find .shader tags
        tag_path = bpy.context.preferences.addons["io_scene_halo"].preferences.halo_2_tag_path.lower()
        
        # Generate the shader collections dict from file
        sc_dict = generate_sc_dict()
        
        shader_count = 0
        skipped_count = 0
        
        row_shift = 0
        row_shift_counter = 0
        
        for root, dirs, files in os.walk(c_path):
            for file in files:
                if file.endswith(".shader"):
                    
                    # Die, extension, you dont belong in this world
                    shadername = file.removesuffix('.shader')
                    
                    # Check to see if it belongs to a collection and if so add the prefix
                    shadername = assign_shader_collection(shadername, root.removeprefix(tag_path), sc_dict)
                    
                    # THIS '--' IS LOAD-BEARING: OTHERWISE SHADER COLLECTION PREFIXES WILL GET IN THE WAY LATER </3
                    shadername_full = shadername + '--' + (root.removeprefix(tag_path)).removeprefix("scenarios\\shaders\\")
                    
                    # Check if the material already exists
                    if shadername in bpy.data.materials:
                        
                        if bpy.context.scene.h2sl_props.regen_existing:
                            print("Regenerating", file, shader_count)
                            bpy.data.materials.remove(bpy.data.materials[shadername])
                            bpy.data.objects.remove(bpy.data.objects[shadername_full], do_unlink = True)
                            
                            # Run Shader Generation
                            mat = bpy.data.materials.get(shadername)
                            halo_shader = shader_processing.find_h2_shader_tag(file, shadername)
                            shader_processing.generate_h2_shader(mat, halo_shader, print)
                            
                            shader_count += 1
                        else:
                            print("Skipping", file)
                            skipped_count += 1
                    
                    # If not:
                    else:
                        obj = bpy.ops.mesh.primitive_plane_add(size=1)
                        mat = bpy.data.materials.new(name=shadername)
                        bpy.context.active_object.name = shadername_full
                        
                        obj = bpy.context.object
                        obj.data.materials.append(mat)
                        
                        obj.location.x += (shader_count % 10)
                        obj.location.y += row_shift
                        shader_count += 1
                        
                        row_shift_counter += 1
                        if row_shift_counter == 20:
                            row_shift_counter = 0
                            row_shift += 1
                        
                        #debugging
                        print(file, shader_count)
                        
                        # Run Shader Generation
                        halo_shader = shader_processing.find_h2_shader_tag(file, shadername)
                        shader_processing.generate_h2_shader(mat, halo_shader, print)
        
        print(shader_count, ".shader tags found")
        print(skipped_count, "shaders skipped")
        
        return

def create_catalog(catalog_names, catalog_path, mat):
    # (Largely) not my own, sourced from:
    # https://blender.stackexchange.com/questions/294734/how-to-create-a-new-catalog-in-the-asset-browser-using-python
    # Because asset catalogs have minimal/poor direct API still so I had to just find the brute force method online :/
    
    #catalog_names = catalog_names[:-1]  # Exclude the last item assuming it is an asset
    catalog_file_path = catalog_path
    with open(catalog_file_path, "a+", encoding="utf-8") as file:
        file.seek(0)
        existing_catalogs = file.read()

        # Process each subset of the catalog_names for directory depth
        for i in range(1, len(catalog_names) + 1):
            # print(catalog_names)
            full_catalog_name = "/".join(catalog_names[:i])
            simple_catalog_name = "-".join(catalog_names[:i])
            catalog_entry = f"{full_catalog_name}:{simple_catalog_name}"

            # Check if the full catalog name is already listed to avoid duplicates
            if catalog_entry not in existing_catalogs:
                new_uuid = str(uuid.uuid4())
                file.write(f"{new_uuid}:{full_catalog_name}:{simple_catalog_name}\n")
                mat.asset_data.catalog_id = new_uuid
            else:
                # Get existing UUID
                
                # Find known substring of full path to get a position to work back from
                index = existing_catalogs.find(full_catalog_name)
                existing_uuid = existing_catalogs[index-37 : index-1] # work backwards
                # print(existing_uuid)
                
                mat.asset_data.catalog_id = existing_uuid
            
    
    return

def create_collection_list(list, obj):
    # Sets up Blender collections to match the folder structure. Largely superfluous but it took AGES to get working so :shrug:
    
    b_collections = bpy.data.collections
    scene_collection = bpy.context.scene.collection
    
    prev_col = None
    i = 0
    for name in list:
        if bpy.data.collections.get(name):
            new_collection = bpy.data.collections[name]
        else:
            new_collection = bpy.data.collections.new(name)
            
        # add object to collection if bottom reached
        if i == len(list) - 1:
            print("moving to " + name)
            try:
                scene_collection.objects.unlink(obj)
            except:
                print("already non-child of scene collection")
            try:
                new_collection.objects.link(obj)
            except:
                print("already child of collection")
            
        if prev_col != None:
            
            try:
                prev_col.children.link(new_collection)
            except:
                print("already child of collection")
        else:
            try:
                scene_collection.children.link(new_collection)
            except:
                print("already child of scene collection")
        
        prev_col = new_collection
        i += 1
    
    return

def categorize_scene_assets():
    
    # Mark Assets
    for m in bpy.data.materials:
        m.asset_mark()
    
    # Fix material preview renders
    for m in bpy.data.materials:
        m.preview_render_type = 'FLAT'
        m.asset_generate_preview()
    
    # Organize - this is the fucked bit
    for o in bpy.data.objects:
        #split into [shadername] and [path], dir's root is the shaders folder
        list = o.name.split('--')
        shadername = list[0]
        path = list[1]
        
        #split the path into a list to iterate into collections
        splitpath = path.split('\\')
        
        print(path)
        create_collection_list(splitpath, o)
        
        fp = bpy.data.filepath
        dir = os.path.dirname(fp)
        
        print(splitpath)
        mat = bpy.data.materials.get(shadername)
        
        if mat is not None:
            create_catalog(splitpath, os.path.join(dir, "blender_assets.cats.txt"), mat)
        else:
            print("!!! Shader " + shadername + " did not generate into a material at cataloguing stage!")
        
    return

class Halo_GenerateAssetsVanilla(Operator):
    """Generate Halo 2 Shaders into an asset library"""
    bl_idname = 'halo_mattools.generate_asset_library'
    bl_label = 'Generate H2 Asset Library'
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        print("Processing main directory shaders...")
        
        #data_path = bpy.context.preferences.addons["io_scene_halo"].preferences.halo_2_data_path.lower()
        tag_path = bpy.context.preferences.addons["io_scene_halo"].preferences.halo_2_tag_path.lower()
        
        if string_empty_check(tag_path):
            self.report({'INFO'}, "Halo 2 Tag Path is not set in addon preferences")
            return {'FINISHED'}
        
        shaders_path = tag_path + "scenarios\\shaders"
        
        # Clear scene entirely if desired
        if context.scene.h2sl_props.clear_scene:
            for o in bpy.data.objects:
                bpy.data.objects.remove(o)    
            
            for m in bpy.data.materials:
                bpy.data.materials.remove(m)
                
            for i in bpy.data.images:
                bpy.data.images.remove(i)
        
        # Invoke generation
        generate_shader_batch(shaders_path)
        
        # Process Materials into Assets
        categorize_scene_assets()
        
        # All done!
        print("==========================")
        print("SHADER GENERATION COMPLETE")
        print("==========================")
        
        return {'FINISHED'}

class Halo_GenerateAssetsFromDirectory(Operator):
    """Select a folder of Halo 2 shaders to convert into assets"""
    bl_idname = 'halo_mattools.generate_external_assets'
    bl_label = 'Append External Shaders'
    bl_options = {"REGISTER", "UNDO"}
    
    directory: StringProperty(
        name="Shader Directory Path",
        description="Directory containing Halo 2 shaders",
        subtype="DIR_PATH",
        default="",
    )
    
    filter_folder: BoolProperty(
        default=True,
        options={"HIDDEN"}
    )
    
    # need this to get a directory filesystem prompt
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        print("Selected directory:", self.directory)
        
        if string_empty_check(self.directory):
            self.report({'INFO'}, "Directory not found")
            return {'FINISHED'}
        
        print("Processing selected directory shaders...")
        
        shaders_path = self.directory
        
        # Invoke generation
        generate_shader_batch(shaders_path)
        
        # Process into assets
        categorize_scene_assets()
        
        # All done!
        print("==========================")
        print("SHADER GENERATION COMPLETE")
        print("==========================")
        
        return{'FINISHED'}

class Halo_ReplaceLocalMaterials(Operator):
    """Replace local materials with Asset equivalents"""
    bl_idname = 'halo_mattools.replace_local_materials'
    bl_label = 'Replace Local Materials'
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        # https://blenderartists.org/t/how-do-i-link-asset-library-materials-and-replace-local-materials/1458657
        print("Attempting to link material assets...")
        
        tag_path = bpy.context.preferences.addons["io_scene_halo"].preferences.halo_2_tag_path.lower() # this is a directory
        asset_file = bpy.context.preferences.addons["h2sl"].preferences.halo_2_asset_library_path # this is a file
        
        # Collect all local material slots
        localSlots = []
        nameList = []
        
        for obj in bpy.data.objects:
            for slot in obj.material_slots:
                localSlots.append(slot)
                if slot.material.name not in nameList:
                    nameList.append(slot.material.name)
        print(len(nameList), "local materials found")
                
        # Link the asset file mats
        count = 0
        with bpy.data.libraries.load(asset_file, assets_only = True, link = True) as (data_from, data_to):
            for mat in data_from.materials:
                if mat in nameList:
                    print(mat)
                    data_to.materials.append(mat)
                    count += 1
        
        # Replace materials
        if localSlots:
            for slot in localSlots:
                for mat in bpy.data.materials:
                    if (slot.material.name_full + ' [' + os.path.basename(asset_file) + ']') == mat.name_full:
                        print("Replacing...")
                        slot.material = mat
        
        print("Finished linking material assets")
        return {'FINISHED'}

class Halo_RegenerateAssetPreviews(Operator):
    """Refresh asset preview thumbnails if they didnt all generate"""
    bl_idname = 'halo_mattools.refresh_asset_previews'
    bl_label = 'Refresh Asset Previews'
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self, context):
        print("Refreshing asset previews...")
        
        for m in bpy.data.materials:
            if not m.preview:    
                m.preview_render_type = 'FLAT'
                m.asset_generate_preview()
        
        return {'FINISHED'}

class Halo_H2AssetLibrary(Panel):
    bl_label = "Create H2 Asset Library"
    bl_idname = "HALO_PT_H2AssetLibrary"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "HALO_PT_AutoTools"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = scene.h2sl_props
        
        # Disable everything if you havent set up your paths, you nonce
        # Or if you're not in the right spot
        tag_path = bpy.context.preferences.addons["io_scene_halo"].preferences.halo_2_tag_path
        data_path = bpy.context.preferences.addons["io_scene_halo"].preferences.halo_2_data_path
        asset_path = bpy.context.preferences.addons["h2sl"].preferences.halo_2_asset_library_path
        if string_empty_check(tag_path) or string_empty_check(data_path) or string_empty_check(asset_path) or bpy.path.abspath(bpy.context.blend_data.filepath) != asset_path:
            layout.enabled = False
        
        col = layout.column(align=True)
        
        row = col.row()
        row.label(text="Only use in Asset Library file", icon="ERROR")
        row = col.row()
        row.label(text='Clear Entire Scene')
        row.prop(settings, "clear_scene", text='')
        row = col.row()
        row.label(text='Regenerate Existing Materials')
        row.prop(settings, "regen_existing", text='')
        row = col.row()
        row.label(text='Use Shader Collections')
        row.prop(settings, "use_shader_collections", text='')
        
        row = col.row()
        row.operator("halo_mattools.generate_asset_library", text="Generate H2 Asset Library")
        
        row = col.row()
        row.operator("halo_mattools.refresh_asset_previews", text="Refresh Asset Previews")
        
        # Presently disabled due to needing messy refactors on the main processing function which makes a lot of assumptions involved with shaders being from the default path.
        #row = col.row()
        #row.operator("halo_mattools.generate_external_assets", text="Append External Shaders")

class Halo_H2AssetUtilities(Panel):
    bl_label = "H2 Asset Utilities"
    bl_idname = "HALO_PT_H2AssetUtils"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "HALO_PT_AutoTools"
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        settings = scene.h2sl_props
        
        # Disable everything if you havent set up your paths, you nonce
        # Or if you're not in the right spot
        tag_path = bpy.context.preferences.addons["io_scene_halo"].preferences.halo_2_tag_path
        data_path = bpy.context.preferences.addons["io_scene_halo"].preferences.halo_2_data_path
        asset_path = bpy.context.preferences.addons["h2sl"].preferences.halo_2_asset_library_path
        if string_empty_check(tag_path) or string_empty_check(data_path) or string_empty_check(asset_path):
            layout.enabled = False
        
        col = layout.column(align=True)
        
        row = col.row()
        row.operator("halo_mattools.replace_local_materials", text="Replace Local Materials")

def register():
    bpy.utils.register_class(Halo_H2AssetLibrary)
    bpy.utils.register_class(Halo_H2AssetUtilities)
    bpy.utils.register_class(H2SL_AddonPrefs)
    bpy.utils.register_class(Halo_GenerateAssetsVanilla)
    bpy.utils.register_class(Halo_GenerateAssetsFromDirectory)
    bpy.utils.register_class(Halo_ReplaceLocalMaterials)
    bpy.utils.register_class(Halo_RegenerateAssetPreviews)
    bpy.utils.register_class(Halo_H2AssetPropertiesGroup)
    
    bpy.types.Scene.h2sl_props = PointerProperty(type=Halo_H2AssetPropertiesGroup)

def unregister():
    bpy.utils.unregister_class(Halo_H2AssetLibrary)
    bpy.utils.unregister_class(Halo_H2AssetUtilities)
    bpy.utils.unregister_class(H2SL_AddonPrefs)
    bpy.utils.unregister_class(Halo_GenerateAssetsVanilla)
    bpy.utils.unregister_class(Halo_GenerateAssetsFromDirectory)
    bpy.utils.unregister_class(Halo_ReplaceLocalMaterials)
    bpy.utils.unregister_class(Halo_RegenerateAssetPreviews)
    bpy.utils.unregister_class(Halo_H2AssetPropertiesGroup)

if __name__ == "__main__":
    register()
