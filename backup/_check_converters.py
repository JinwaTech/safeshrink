"""检查 MarkItDown 的格式路由逻辑"""
import inspect
import markitdown._markitdown as mdm

# 读取 MarkItDown.convert 方法的源码，看扩展名路由
src = inspect.getsource(mdm.MarkItDown.convert)
lines = src.split('\n')
for i, line in enumerate(lines):
    print(f'{i+1:3d}: {line}')
