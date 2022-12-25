bl_info = {
    "name" : "ColorKeeper",
    "description" : "Store different color combos",
    "author" : "hisanimations",
    "version" : (1, 0),
    "blender" : (3, 0, 0),
    "location" : "Render Properties > Color Management > Curvlet",
    "support" : "COMMUNITY",
    "category" : "Scene",
}

import bpy, pickle, gzip, pathlib # pickle is used to turn all data types into one byte array which can be dumped to or loaded from at any moment.
                        # gzip to compress.
from bpy.app.handlers import persistent

#from os import Path

classes = []
#{'0': {'0': [0.0, 0.0], '1': [0.411111056804657, 0.24999995529651642], '2': [0.6962962746620178, 0.6547614932060242], '3': [1.0, 1.0]}, '1': {'0': [0.0, 0.0], '1': [1.0, 1.0]}, '2': {'0': [0.0, 0.0], '1': [1.0, 1.0]}, '3': {'0': [0.0, 0.0], '1': [0.25555554032325745, 0.16666662693023682], '2': [0.5074074268341064, 0.601190447807312], '3': [0.7555558681488037, 0.7440477013587952], '4': [1.0, 1.0]}}
def updateTempList(self, context):
    context.scene.CURVEDATA[context.scene.templistindex][0] = self.name # update the selected color preset's name. self referring to the active template list item.
    context.scene['CURVEDATA'] = pickle.dumps(context.scene.CURVEDATA) # update the scene's custom property with an up-to-date byte array of the color data in the scene.

class TempList(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="",
        description="",
        default = 'untitled',
        update=updateTempList
    )

def GetCurveMapping(): # get the current RGB curve data.
    POINTS = {}
    CURVES = {}
    curvcount = 0 # counts for the curves
    counter = 0 # counts for points
    for i in bpy.context.scene.view_settings.curve_mapping.curves: # iterates through R, G, B, and C curves
        for ii in i.points: # iterates through points.
            POINTS[str(counter)] = [[round(ii.location[0], 5), round(ii.location[1], 5)], ii.handle_type] # add a new key to `POINTS` containing the current iteration's of points location and type
            counter +=1 # count to the next point. new keys' names are a string variant of the current iteration.
        counter = 0 # reset the point counter
        CURVES[str(curvcount)] = POINTS # add a new key contating the current iteration of curves and its point data stored in POINTS
        POINTS = {}
        curvcount += 1
    return CURVES

class HISANIM_UL_CURVELIST(bpy.types.UIList):

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text='')

class HISANIM_PT_COLORKEEPER(bpy.types.Panel):
    bl_label = 'ColorKeeper'
    bl_parent_id = "RENDER_PT_color_management"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.template_list('HISANIM_UL_CURVELIST', '', context.scene, 'templist', context.scene, 'templistindex')
        row = row.column(align = True)
        row.operator('hisanim.addcurve', icon='ADD', text='')
        row.operator('hisanim.removecurve', icon='REMOVE')
        row.separator()
        row.operator('hisanim.applycurve', text='', icon='EXPORT')
        
        row = layout.row()
        
        try:
            item = context.scene.templist[context.scene.templistindex]
            row.prop(item, "name")
            row.operator('hisanim.updatecurve', text='Update Template', icon='FILE_REFRESH')
        except:
            pass
        row = layout.row()
        row.prop(context.scene, 'colorinfo', text='Color Data')
        row = layout.row(align=True)
        row.operator('hisanim.getcurve', text='Export Color Data')
        row.operator('hisanim.appendcurve', text='Import Color Data')
        row = layout.row()
        row.operator('hisanim.loadpresets')
        
        
class HISANIM_OT_ADDCURVE(bpy.types.Operator):
    bl_idname = 'hisanim.addcurve'
    bl_label = 'Add Curve'
    bl_description = 'Add your current color profile to addn'
    bl_options = {'UNDO'}
    def execute(self, context):
        if context.scene.get('CURVEDATA') == None:
            bpy.types.Scene.CURVEDATA = []
        NEW = [f'Untitled', GetCurveMapping(), bpy.context.scene.display_settings.display_device, bpy.context.scene.view_settings.view_transform, bpy.context.scene.view_settings.look, bpy.context.scene.view_settings.exposure, bpy.context.scene.view_settings.gamma, bpy.context.scene.sequencer_colorspace_settings.name, [*bpy.context.scene.view_settings.curve_mapping.black_level], [*bpy.context.scene.view_settings.curve_mapping.white_level]]
        
        # a list containing a place holder name, a list of color info, display device, view transform, look, exposure, gamma, sequencer color space, black level, and white level
        #                     0                  1                     2               3               4     5         6      7         8     9      10           11

        context.scene.CURVEDATA.append(NEW) # append the current color data to the template list.
        
        context.scene['CURVEDATA'] = pickle.dumps(context.scene.CURVEDATA) # used to be NEW | update the scene's custom property with an up-to-date byte array of the color data in the scene.
        
        del NEW
        HasUntitled = lambda x: "Untitled" in x.name #                   v
        HowMany = len(list(filter(HasUntitled, context.scene.templist))) # returns how many entries have "Untitled" in their names
        x = bpy.context.scene.templist.add() # add a new entry to the template list
        x.name = f'Untitled{max(HowMany+1,len(context.scene.templist))}'
        print(x.name) # make sure names will never overlap when creating new templates
        for i in range(0, (len(context.scene.templist)+1)):
            
            # ok so this was REALLY weird. for some reason, color data would get appended to the template list just fine, but names would not.
            # for example, say you have a color template containing "X" data with "A" name. then, you add a new color template containing "Y" data with "B" name.
            # you'd think the list would go something along the lines of [["A", "X"], ["B", "Y"]], but for some *really* stupid reason which i could not figure out,
            # if would show as [["B", "X"], ["A", "Y"]]. in super simple terms, the position of color data would stay matched to what the visible template list holds, but the names would not.
            # every time a new template is added, ColorKeeper will iterate through the visible template list, and copy & paste the name to the same iteration of the scene template list (CURVEDATA).
            
            try:
                print(f'Changing {context.scene.CURVEDATA[i][0]} to {context.scene.templist[i].name}')
                bpy.types.Scene.CURVEDATA[i][0] = context.scene.templist[i].name
            except:
                pass
        return {'FINISHED'}

class HISANIM_OT_UPDATECURVE(bpy.types.Operator):
    bl_idname = 'hisanim.updatecurve'
    bl_label = 'Update Color Settings?'
    bl_description = 'Update the selected template with the current color configuration'
    bl_options = {'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        context.scene.CURVEDATA[context.scene.templistindex] = [context.scene.CURVEDATA[context.scene.templistindex][0], GetCurveMapping(), bpy.context.scene.display_settings.display_device, bpy.context.scene.view_settings.view_transform, bpy.context.scene.view_settings.look, bpy.context.scene.view_settings.exposure, bpy.context.scene.view_settings.gamma, bpy.context.scene.sequencer_colorspace_settings.name, [i for i in bpy.context.scene.view_settings.curve_mapping.black_level], [i for i in bpy.context.scene.view_settings.curve_mapping.white_level]]
        # update the active template with current color info.
        context.scene['CURVEDATA'] = pickle.dumps(context.scene.CURVEDATA) # update the scene's custom property with an up-to-date byte array of the color data in the scene.
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event) # adds a confirmation window so you don't accidentally overwrite color data.
        
class HISANIM_OT_REMOVECURVE(bpy.types.Operator):
    bl_idname = 'hisanim.removecurve'
    bl_label = ''
    bl_description = ''
    bl_options = {'UNDO'}
    def execute(self, context):
        if len(context.scene.templist) == 0: # if there is nothing to remove, do not remove.
            return {'CANCELLED'}
        LAST = False
        if context.scene.templistindex+1 == len(context.scene.templist) and len(context.scene.templist) != 1: # v line 155
            LAST = True #                                                                                       v line 155
        context.scene.CURVEDATA.pop(context.scene.templistindex) # remove the current template
        bpy.context.scene.templist.remove(bpy.context.scene.templistindex) # 
        if LAST: # if you've removed the last template (last not meaning last remaining, but the most recent), make the active template list the one above it. this is done to avoid visual glitches.
            context.scene.templistindex = len(context.scene.templist)-1
        context.scene['CURVEDATA'] = pickle.dumps(context.scene.CURVEDATA) # update the scene's custom property with an up-to-date byte array of the color data in the scene.
        return {'FINISHED'}

class HISANIM_OT_APPLYCURVE(bpy.types.Operator):
    bl_idname = 'hisanim.applycurve'
    bl_label = 'Apply Curve'
    crv : bpy.props.StringProperty(default = '')
    bl_description = 'Apply active template onto your scene'
    bl_options = {'UNDO'}
    def execute(self, context):
        if len(context.scene.templist) == 0:
            return {'CANCELLED'}
        
        counter = 0
        context.scene.display_settings.display_device = context.scene.CURVEDATA[context.scene.templistindex][2]
        context.scene.view_settings.view_transform = context.scene.CURVEDATA[context.scene.templistindex][3]
        context.scene.view_settings.look = context.scene.CURVEDATA[context.scene.templistindex][4]
        context.scene.view_settings.exposure = context.scene.CURVEDATA[context.scene.templistindex][5]
        context.scene.view_settings.gamma = context.scene.CURVEDATA[context.scene.templistindex][6]
        context.scene.sequencer_colorspace_settings.name = context.scene.CURVEDATA[context.scene.templistindex][7]
        context.scene.view_settings.curve_mapping.black_level = context.scene.CURVEDATA[context.scene.templistindex][8]
        context.scene.view_settings.curve_mapping.white_level = context.scene.CURVEDATA[context.scene.templistindex][9]
        # initialize curve; the curve_mapping.initialize() function does not seem to work
        for i in context.scene.view_settings.curve_mapping.curves:
            while True and len(i.points) != 2:
                try:
                    # remove the 2nd point of the curve data until two points remain.
                    i.points.remove(i.points[1])
                except:
                    raise
            i.points[0].location = (0, 0) # reset the position of the curves 
            i.points[1].location = (1, 1)
            POINTS = [*context.scene.CURVEDATA[context.scene.templistindex][1][str(counter)].keys()] # get the points of the active curve of the active template
            buh = len(POINTS)-1 # useless name. this variable helps place new points in a linear line with even spacing.
            for ii in POINTS[1:-1]:
                i.points.new(position=int(ii)/buh, value = int(ii)/buh)
            for ii in POINTS: # apply the position and type of points accordingly to how they are mentioned in POINTS
                i.points[int(ii)].location = context.scene.CURVEDATA[context.scene.templistindex][1][str(counter)][ii][0] # apply location
                i.points[int(ii)].handle_type = context.scene.CURVEDATA[context.scene.templistindex][1][str(counter)][ii][1] # apply handle type
                
            counter += 1
        context.scene.view_settings.curve_mapping.update()
        context.scene.frame_current += 1
        context.scene.frame_current += -1 # to update after updating (idk lol) | that comment was written awhile before this one. it still applies lol
        
        return {'FINISHED'}

def GetCurve():
    return pickle.loads(bpy.context.scene['CURVEDATA'])[bpy.context.scene.templistindex] # get the color data of the active template.

class HISANIM_OT_GETCURVE(bpy.types.Operator):
    bl_idname = 'hisanim.getcurve'
    bl_label = 'Get Curve Data'

    def execute(self, context):
        context.scene.colorinfo = str(gzip.compress(pickle.dumps(GetCurve())))[2:-1] # dump and compress the color data and convert it into a string to be easily used anywhere else.
        return {'FINISHED'}

class HISANIM_OT_APPENDCURVE(bpy.types.Operator):
    bl_idname = 'hisanim.appendcurve'
    bl_label = 'Append Color Info'
    bl_options = {'UNDO'}
    def execute(self, context):
        cc = bytes(rf'{context.scene.colorinfo}', 'latin1').decode('unicode_escape').encode("raw_unicode_escape")
        
        # python & blender had a major issue converting the string data back into bytes, with the reason being the backslashes.
        # in python, whenever backslashes are used and it is not meant to escape from anything, you use two backslashes.
        # in this case, only one backslash is desired and it is not meant to escape from anything.
        # after trying many ways to convert the '\\' to '\', i found the best way here: https://stackoverflow.com/questions/38763771/how-do-i-remove-double-back-slash-from-a-bytes-object
        # this will decode and reencode to the desired output.
        
        context.scene.CURVEDATA.append(pickle.loads(gzip.decompress(cc))) # add the new preset color data
        x = context.scene.templist.add() # add a new entry to the visible template list
        x.name = pickle.loads(gzip.decompress(cc))[0] # rename the new entry according to the preset color data
        return {'FINISHED'}

class HISANIM_OT_LOADPRESETS(bpy.types.Operator):
    bl_idname = 'hisanim.loadpresets'
    bl_label = 'Load Presets'
    bl_options = {'UNDO'}

    def execute(self, context):
        LoadPresets()
        return {'FINISHED'}

@persistent
def OnLoad(dummy):
    if bpy.context.scene.get('CURVEDATA') == None: # if no color data exists, initialize it.
        bpy.types.Scene.CURVEDATA = []
        #LoadPresets()
    else: # if color data does exist, load from what is saved in the scene's custom property.
        print('LOADING')
        bpy.types.Scene.CURVEDATA = pickle.loads(bpy.context.scene.get('CURVEDATA'))

@persistent
def OnSave(dummy):
    print('SAVING')
    bpy.context.scene['CURVEDATA'] = pickle.dumps(bpy.context.scene.CURVEDATA) # update the scene's custom property with an up-to-date byte array of the color data in the scene.

bpy.app.handlers.save_pre.append(OnSave)
bpy.app.handlers.load_post.append(OnLoad)

classes.append(HISANIM_OT_UPDATECURVE)
classes.append(HISANIM_OT_APPLYCURVE)
classes.append(HISANIM_OT_ADDCURVE)
classes.append(HISANIM_PT_COLORKEEPER)
classes.append(TempList)
classes.append(HISANIM_UL_CURVELIST)
classes.append(HISANIM_OT_REMOVECURVE)
classes.append(HISANIM_OT_GETCURVE)
classes.append(HISANIM_OT_APPENDCURVE)
classes.append(HISANIM_OT_LOADPRESETS)

def LoadPresets(): # working on this
    path = str(pathlib.Path(__file__).parent)
    presets = open(path+'/presets.txt', 'r')

    for i in presets:
        i = i[:-1]
        print(i)
        cc = bytes(rf'{i}', 'latin1').decode('unicode_escape').encode("raw_unicode_escape")
        bpy.types.Scene.CURVEDATA.append(pickle.loads(gzip.decompress(cc))) # add the new preset color data
        x = bpy.context.scene.templist.add() # add a new entry to the visible template list
        x.name = pickle.loads(gzip.decompress(cc))[0] # rename the new entry according to the preset color data

def register():
    for i in classes:
        bpy.utils.register_class(i)
    bpy.types.Scene.templist = bpy.props.CollectionProperty(type = TempList)
    bpy.types.Scene.colorinfo = bpy.props.StringProperty(description='Exports color code in a form of a compressed byte array')
    bpy.types.Scene.templistindex = bpy.props.IntProperty(name='Template Index')
    try:
        bpy.context.scene.CURVEDATA
    except:
        bpy.types.Scene.CURVEDATA = []
    bpy.app.handlers.save_pre.append(OnSave)
    bpy.app.handlers.load_post.append(OnLoad)
    #LoadPresets()
def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)
    del bpy.types.Scene.colorinfo
    del bpy.types.Scene.templist
    del bpy.types.Scene.templistindex
    del bpy.types.Scene.CURVEDATA

if __name__ == '__main__':
    register()
