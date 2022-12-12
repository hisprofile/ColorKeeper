bl_info = {
    "name" : "Curvlet",
    "description" : "Store different color combos",
    "author" : "hisanimations",
    "version" : (1, 1),
    "blender" : (3, 0, 0),
    "location" : "Render Properties > Color Management > Curvlet",
    "support" : "COMMUNITY",
    "category" : "Scene",
}

import bpy, pickle
from bpy.app.handlers import persistent
classes = []
#{'0': {'0': [0.0, 0.0], '1': [0.411111056804657, 0.24999995529651642], '2': [0.6962962746620178, 0.6547614932060242], '3': [1.0, 1.0]}, '1': {'0': [0.0, 0.0], '1': [1.0, 1.0]}, '2': {'0': [0.0, 0.0], '1': [1.0, 1.0]}, '3': {'0': [0.0, 0.0], '1': [0.25555554032325745, 0.16666662693023682], '2': [0.5074074268341064, 0.601190447807312], '3': [0.7555558681488037, 0.7440477013587952], '4': [1.0, 1.0]}}
def updateTempList(self, context):
    context.scene.CURVEDATA[context.scene.templistindex][0] = self.name
class TempList(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(
        name="",
        description="",
        default = 'untitled',
        update=updateTempList
    )

def GetCurveMapping():
    POINTS = {}
    CURVES = {}
    curvcount = 0
    counter = 0
    for i in bpy.context.scene.view_settings.curve_mapping.curves:
        for ii in i.points:
            POINTS[str(counter)] = [[ii.location[0], ii.location[1]], ii.handle_type]
            counter +=1
        counter = 0
        CURVES[str(curvcount)] = POINTS
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

class HISANIM_PT_CURVLET(bpy.types.Panel):
    bl_label = 'Curvlet'
    bl_parent_id = "RENDER_PT_color_management_curves"
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
        
        row = layout.row()
        
        
class HISANIM_OT_ADDCURVE(bpy.types.Operator):
    bl_idname = 'hisanim.addcurve'
    bl_label = 'Add Curve'
    bl_description = 'Add your current color profile to addn'
    bl_options = {'UNDO'}
    def execute(self, context):
        if context.scene.get('CURVEDATA') == None:
            bpy.types.Scene.CURVEDATA = []
        num = len(context.scene.templist)
        NEW = [f'Untitled', GetCurveMapping(), bpy.context.scene.display_settings.display_device, bpy.context.scene.view_settings.view_transform, bpy.context.scene.view_settings.look, bpy.context.scene.view_settings.exposure, bpy.context.scene.view_settings.gamma, bpy.context.scene.sequencer_colorspace_settings.name, [i for i in bpy.context.scene.view_settings.curve_mapping.black_level], [i for i in bpy.context.scene.view_settings.curve_mapping.white_level]]
        context.scene.CURVEDATA.append(NEW)
        context.scene['CURVEDATA'] = pickle.dumps(NEW)
        del NEW
        HasUntitled = lambda x: "Untitled" in x.name
        HowMany = len(list(filter(HasUntitled, context.scene.templist)))
        x = bpy.context.scene.templist.add()
        x.name = f'Untitled{HowMany+1}'
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
        context.scene['CURVEDATA'] = pickle.dumps(context.scene.CURVEDATA)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
        
class HISANIM_OT_REMOVECURVE(bpy.types.Operator):
    bl_idname = 'hisanim.removecurve'
    bl_label = ''
    bl_description = ''
    bl_options = {'UNDO'}
    def execute(self, context):
        if len(context.scene.templist) == 0:
            return {'CANCELLED'}
        LAST = False
        if context.scene.templistindex+1 == len(context.scene.templist) and len(context.scene.templist) != 1:
            LAST = True
        context.scene.CURVEDATA.pop(context.scene.templistindex)
        bpy.context.scene.templist.remove(bpy.context.scene.templistindex)
        if LAST:
            context.scene.templistindex = len(context.scene.templist)-1
        context.scene['CURVEDATA'] = pickle.dumps(context.scene.CURVEDATA)
        return {'FINISHED'}

class HISANIM_OT_APPLYCURVE(bpy.types.Operator):
    bl_idname = 'hisanim.applycurve'
    bl_label = 'Apply Curve'
    crv : bpy.props.StringProperty(default = '')
    bl_description = f'Apply Curve {"crv"} onto your scene'
    bl_options = {'UNDO'}
    def execute(self, context):
        if len(context.scene.templist) == 0:
            return {'CANCELLED'}
        #initialize curve; the curve_mapping.initialize() function does not seem to work
        counter = 0
        context.scene.display_settings.display_device = context.scene.CURVEDATA[context.scene.templistindex][2]
        context.scene.view_settings.view_transform = context.scene.CURVEDATA[context.scene.templistindex][3]
        context.scene.view_settings.look = context.scene.CURVEDATA[context.scene.templistindex][4]
        context.scene.view_settings.exposure = context.scene.CURVEDATA[context.scene.templistindex][5]
        context.scene.view_settings.gamma = context.scene.CURVEDATA[context.scene.templistindex][6]
        context.scene.sequencer_colorspace_settings.name = context.scene.CURVEDATA[context.scene.templistindex][7]
        context.scene.view_settings.curve_mapping.black_level = context.scene.CURVEDATA[context.scene.templistindex][8]
        context.scene.view_settings.curve_mapping.white_level = context.scene.CURVEDATA[context.scene.templistindex][9]
        for i in context.scene.view_settings.curve_mapping.curves:
            while True and len(i.points) != 2:
                try:
                    i.points.remove(i.points[1])
                except:
                    raise
            i.points[0].location = (0, 0)
            i.points[1].location = (1, 1)
            POINTS = [*context.scene.CURVEDATA[context.scene.templistindex][1][str(counter)].keys()]
            buh = len(POINTS)-1
            print(buh)
            POINTCOUNT = len(context.scene.CURVEDATA[context.scene.templistindex][1][str(counter)].keys())-1
            print(POINTS)
            for ii in POINTS[1:-1]:
                i.points.new(position=int(ii)/buh, value = int(ii)/buh)
                print(ii)
                print(int(ii)/buh)
            pc = 0
            for ii in POINTS:
                i.points[int(ii)].location = context.scene.CURVEDATA[context.scene.templistindex][1][str(counter)][ii][0]
                i.points[int(ii)].handle_type = context.scene.CURVEDATA[context.scene.templistindex][1][str(counter)][ii][1]
                
            counter += 1
        context.scene.view_settings.curve_mapping.update()
        context.scene.frame_current += 1
        context.scene.frame_current += -1 # to update after updating (idk lol)
        
        
        
        return {'FINISHED'}
@persistent
def OnLoad(dummy):
    if bpy.context.scene.get('CURVEDATA') == None:
        bpy.types.Scene.CURVEDATA = []
    else:
        print('LOADING')
        bpy.types.Scene.CURVEDATA = pickle.loads(bpy.context.scene.get('CURVEDATA'))

@persistent
def OnSave(dummy):
    print('SAVING')
    bpy.context.scene['CURVEDATA'] = pickle.dumps(bpy.context.scene.CURVEDATA)

bpy.app.handlers.save_pre.append(OnSave)
bpy.app.handlers.load_post.append(OnLoad)

classes.append(HISANIM_OT_UPDATECURVE)
classes.append(HISANIM_OT_APPLYCURVE)
classes.append(HISANIM_OT_ADDCURVE)
classes.append(HISANIM_PT_CURVLET)
classes.append(TempList)
classes.append(HISANIM_UL_CURVELIST)
classes.append(HISANIM_OT_REMOVECURVE)
def register():
    for i in classes:
        bpy.utils.register_class(i)
    bpy.types.Scene.templist = bpy.props.CollectionProperty(type = TempList)
    bpy.types.Scene.templistindex = bpy.props.IntProperty(name='Template Index')
    try:
        bpy.context.scene.CURVEDATA
    except:
        bpy.types.Scene.CURVEDATA = []
    bpy.app.handlers.save_pre.append(OnSave)
    bpy.app.handlers.load_post.append(OnLoad)
def unregister():
    for i in classes:
        bpy.utils.unregister_class(i)
    del bpy.types.Scene.templist
    del bpy.types.Scene.templistindex
    del bpy.types.Scene.CURVEDATA

if __name__ == '__main__':
    register()
