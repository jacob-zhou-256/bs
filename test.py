import os
import bpy
from bpy_extras.io_utils import ImportHelper, axis_conversion


bl_info = {
    "name": "OFF format",
    "description": "",
    "author": "ZhouDaojie",
    "blender": (4, 2, 3),
    "version": (0, 0, 1),
    "location": "File > Import-Export",
    "warning": "",
    "category": "Import-Export"
}


class ImportOFF(bpy.types.Operator, ImportHelper):
    bl_idname = "import_off.opeator"
    bl_label = "Import OFF"

    # 点击"导入"按钮, 会触发执行下面execute
    def execute(self, context):
        print("import off!")

        keywords = self.as_keywords()
        # print(keywords["filepath"])

        global_matrix = axis_conversion(
            from_forward='Y',
            from_up='Z',
            to_forward='Y',
            to_up='Z'
        ).to_4x4()

        mesh = load(self, context, keywords["filepath"])
        if not mesh:
            return {'CANCELLED'}

        scene = bpy.context.scene
        obj = bpy.data.objects.new(mesh.name, mesh)
        scene.collection.objects.link(obj)

        obj.matrix_world = global_matrix

        layer = bpy.context.view_layer
        layer.update()

        return {'FINISHED'}


def load(operator, context, filepath):
    """清理旧的mesh对象"""
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':  # 仅删除Mesh对象
            bpy.data.objects.remove(obj)

    filepath = os.fsencode(filepath)    # 文件路径转编码
    # print(filepath)

    file = open(filepath, 'r')
    # print(file)
    
    """第一部分 OFF/COFF 是否使用颜色"""
    first_line = file.readline().rstrip()   # OFF->没有颜色, COFF->包含颜色, 这里是OFF
    use_colors = (first_line == 'COFF')
    # print(use_colors)
    
    """第二部分 顶点,面,边的数量"""
    line = file.readline()
    while line.isspace() or line[0]=='#':
        line = file.readline()
    
    print(line)

    (vcount, fcount, ecount) = (int(x) for x in line.split()) # 顶点数, 面数, 边数
    print("顶点数:\t%s\n面数:\t%s\n边数:\t%s\n" % (vcount, fcount, ecount))

    """遍历顶点"""
    verts = []
    facets = []
    edges = []
    i = 0
    while i < vcount:
        line = file.readline()
        if line.isspace():
            continue
        (px, py, pz) = (float(x) for x in line.split())
        verts.append((px, py, pz))
        i = i + 1
    # print(verts)

    """遍历面"""
    i = 0
    while i < fcount:
        line = file.readline()
        if line.isspace():
            continue
        splitted  = line.split()
        ids = list(map(int, splitted))
        if len(ids) > 3:
            facets.append(tuple(ids[1:]))
        elif len(ids) == 3:
            edges.append(tuple(ids[1:]))
        i = i + 1
    # print(facets)
    # print(edges)

    mesh_name = bpy.path.display_name_from_filepath(filepath)
    mesh = bpy.data.meshes.new(name=mesh_name)
    mesh.from_pydata(verts, edges, facets)

    mesh.validate()
    mesh.update()

    return mesh


class ExportOFF(bpy.types.Operator):
    bl_idname = "export_off.opeator"
    bl_label = "Export OFF Operator"
    # 点击"导出"按钮, 会触发执行下面execute
    def execute(self, context):
        print("export off!")
        return {'FINISHED'}


def menu_func_import(self, context):
    self.layout.operator(ImportOFF.bl_idname, text="OFF (.off)")


def menu_func_export(self, context):
    self.layout.operator(ExportOFF.bl_idname, text="OFF (.off)")

"""注册"""
def register():
    print("import off register!")
    bpy.utils.register_class(ImportOFF)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)

    print("export off register!")
    bpy.utils.register_class(ExportOFF)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)

"""注销"""
def unregister():
    print("import off unregister!")
    bpy.utils.unregister_class(ImportOFF)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)

    print("export off unregister!")
    bpy.utils.unregister_class(ExportOFF)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()
