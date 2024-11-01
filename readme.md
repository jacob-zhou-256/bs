## Import-Export OFF 基础开发

说明：使用Blender版本为4.2.3

代码如下：

```python
import bpy


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


class ImportOFF(bpy.types.Operator):
    bl_idname = "import_off.opeator"
    bl_label = "Import OFF Operator"
    # 点击"导入"按钮, 会触发执行下面execute
    def execute(self, context):
        print("import off!")
        return {'FINISHED'}


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
```

导入流程：

​	按照截图依次操作，导入写好的python文件即可

<img src="C:\Users\84077\AppData\Roaming\Typora\typora-user-images\image-20241028213203043.png" alt="image-20241028213203043" style="zoom:50%;" />

<img src="C:\Users\84077\AppData\Roaming\Typora\typora-user-images\image-20241028213327766.png" alt="image-20241028213327766" style="zoom:50%;" />



## Import OFF功能开发

