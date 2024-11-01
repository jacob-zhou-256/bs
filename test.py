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

        mesh, verts = load(keywords["filepath"])
        if not mesh:
            return {'CANCELLED'}
        
        obj = bpy.data.objects.new(mesh.name, mesh)
        bpy.context.collection.objects.link(obj)
        obj.matrix_world = global_matrix

        return {'FINISHED'}


def load(filepath):
    """清理旧的mesh对象"""
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':  # 仅删除Mesh对象
            bpy.data.objects.remove(obj)
    
    # """按行打印.off文件"""
    # output_txt_path = r"C:\Users\84077\Desktop\tmp.txt"
    # with open(filepath, 'r') as file, open(output_txt_path, 'w') as output_file:
    #     line = file.readline().strip()
    #     while line:
    #         output_file.write(line)  # 将每行内容写入 .txt 文件
    #         line = file.readline()  # 读取下一行
    # print(f"已将 {filepath} 内容写入 {output_txt_path}")

    """解析颜色,顶点,面,边"""
    verts = []
    facets = []
    edges = []
    with open(os.fsencode(filepath), 'r') as file:
        first_line = file.readline().strip()    # 读取第一行
        if "OFF" in first_line and len(first_line) > 3:
            line = first_line[3:]   # 格式1:从第4个字符起分割
        elif first_line == "OFF":
            line = file.readline().strip()  # 格式2:第一行是OFF, 下一行是顶点、面、边数量
        else:
            raise ValueError("first line is other format!")

        use_colors = True # # OFF->没有颜色, COFF->包含颜色, 这里默认是OFF
        # print(use_colors)

        (vcount, fcount, ecount) = (int(x) for x in line.split()) # 顶点数, 面数, 边数

        """遍历顶点"""
        i = 0
        while i < vcount:
            line = file.readline().strip()
            (px, py, pz) = (float(x) for x in line.split())
            verts.append((px, py, pz))
            i = i + 1
        # print(verts)

        """遍历面"""
        i = 0
        while i < fcount:
            line = file.readline().strip()
            splitted  = line.split()
            ids = list(map(int, splitted))
            if len(ids) > 3:
                facets.append(tuple(ids[1:]))
            elif len(ids) == 3:
                edges.append(tuple(ids[1:]))
            i = i + 1

        """检查数据解析"""
        if len(verts) != vcount or len(facets) != fcount or len(edges) != ecount:
            raise ValueError("data parse is error!")
        
        print("顶点数:\t%d\n面数:\t%d\n边数:\t%d\n" % (vcount, fcount, ecount))

    mesh_name = bpy.path.display_name_from_filepath(filepath)
    mesh = bpy.data.meshes.new(name=mesh_name)
    mesh.from_pydata(verts, edges, facets)

    mesh.validate()
    mesh.update()

    return mesh, verts


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
