# Halo-2-Shader-Library
Extension add-on for the Halo Asset Blender Development Toolset that enables creation of a visual library of Halo 2 environment shaders. Requires Blender 4.0 or later. All credit to General_101 and co. for their work on the original toolset this addon depends on, and to Crisp and other members of the Halo modding spheres for input/assistance on the coding side of things.

## How to Set Up

### Install the Toolset
Download the latest release of the [Halo Asset Blender Development Toolset](https://github.com/General-101/Halo-Asset-Blender-Development-Toolset).<br>
**Be sure to set up your Halo 2 Data Path and Tag Path in the Toolset, and set Shader Generation to "Full".**

### Install H2SL
Download the latest release of this add-on from the Releases tab, and install h2sl.zip as an add-on.


### Setting up your Asset Library

Blender Asset Libraries are technically just folders that contain normal .blend files, themselves containing objects, materials, etc. marked as Assets. This is no different.

Firstly, create a new folder specifically to be used as your Halo 2 Shaders Library. I recommend making a new folder in the root of your H2EK with a distinctive name like "blender_shader_library".

Next, mark it as an Asset Library with Blender's built-in tools. Open Blender's Preferences menu and navigate to File Paths.

From there, create a new Asset Library (the name doesn't matter but you should probably name it something to the effect of "Halo 2 Shaders"), and set its folder to be the same as the one created in the previous step.

Create a new Blender file, and **save it inside of the folder used as your Asset Library.** The name also technically doesn't matter but should obviously indicate that the file holds all of your Halo 2 shader data. Delete any default objects inside it and leave it completely empty, but **stay in the Layout Tab in the default 3D view.**

Navigate back to your Blender Preferences, but this time to the Add-ons section. Find the Halo 2 Shader Library Generator add-on, and set the **Halo 2 Asset Library Path** field to **the .blend file you created inside of your Asset Library.**


### Generating Shader Assets

If you did all of the above correctly, you should now have a completely empty blend file inside a folder that Blender considers its own Asset Library. I recommmend changing the bottom window to the **Asset Browser** view, which should show an empty library with the name of the Asset Library you created earlier.

If your Halo 2 Tag and Halo 2 Data paths, in addition to your Halo 2 Asset Library path are all filled out correctly, the **"Create H2 Asset Library** tab at the bottom of the Halo Tools panel should no longer be greyed out. There are several options, but you don't need to use these at all. Just leave **"Use Shader Collections"** enabled as it speeds up the next process enormously.

This process of shader name importing and conversion into Blender assets takes quite a while, I estimate up to ten minutes on average hardware. To view the script's progress, look to Blender's topbar, select **Window**, then **Toggle System Console.** Drag this window out somewhere where you can see it, it will display the script's progress even though Blender will be frozen while it runs.

At this point, you are ready to let the magic begin. Click the button labeled **"Generate Halo 2 Asset Library".** Blender will become unresponsive, with the exception of the System Console window, which will display various debug information about what the script is doing. This process does not consume all of your system's resources unless it is particularly weak, so do something else for a little while whilst it runs. When it is done, the console should display a line saying **"SHADER GENERATION COMPLETE"**, and your Blender file will be filled with about 1530 objects and materials, if your Halo 2 shaders folder is vanilla.

If you now check the contents of your library in the Asset Browser, you should now see hundreds of materials, all of which sorted into catalog folders based on their actual location in the H2EK shader directory. Initially, they will lack material preview thumbnails, which take awhile to generate since they are done on a background thread, so they will eventually fill in. Again, take some time to let this process complete, as it may not run in the background still if you switch to a different blender file. If for whatever reason after a long time not every thumbnail has yet been created, click the **"Refresh Asset Previews"** button, which will force Blender to try again, though this will still take some time.


### Using the Asset Library

Blender Assets are used via the **Asset Browser** view. You can drag and drop materials onto objects, or more usefully in the case of this tool, directly onto **Object Material Slots.**

### Replacing Local Materials

With General's toolset, when you import a map's .ass file, it will automatically create Blender shaders for it, local to the .blend file you imported the map into. However, this is of course potentially inconvenient when attempting to work with this Asset Library based tool. To remedy this somewhat, using the **"Replace Local Materials"** button will find any local materials in the file that match the name of a material in your Halo 2 Asset Library and replace them with their Asset equivalents. Note that Halo materials in Blender can use their names to assign extra material parameters such as lightmap density or brightness, or even collision. Materials with these additional properties will not be converted to Asset equivalents.

Nonetheless, this tool shines best for the purposes of adding new Halo materials to a scene rather than working with ones already present.
