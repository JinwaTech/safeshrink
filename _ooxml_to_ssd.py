"""
_ooxml_to_ssd.py
纯 Python zipfile 实现 OOXML → SSD 转换（不依赖 markitdown/docx/pptx/openpyxl）
用于 PyInstaller 打包的 EXE 环境
"""
import zipfile
import re
import os
from pathlib import Path

def _ooxml_to_ssd(filepath, embed_images=False):
    """
    纯 zipfile 解析 .docx/.xlsx/.pptx，返回 Markdown 文本。
    不依赖 markitdown / python-docx / openpyxl / pptx。
    """
    ext = Path(filepath).suffix.lower()
    if ext == '.docx':
        return _docx_to_ssd(filepath)
    elif ext == '.xlsx':
        return _xlsx_to_ssd(filepath)
    elif ext == '.pptx':
        return _pptx_to_ssd(filepath)
    else:
        raise ValueError(f"不支持的格式: {ext}")


def _docx_to_ssd(filepath):
    """用 zipfile 解析 .docx（Word），提取纯文字"""
    paragraphs = []
    with zipfile.ZipFile(filepath, 'r') as z:
        xml_content = z.read('word/document.xml').decode('utf-8', errors='ignore')
    # 提取 <w:t> 标签内的文字
    texts = re.findall(r'<w:t[^>]*>([^<]*)</w:t>', xml_content)
    for t in texts:
        t = t.strip()
        if t:
            paragraphs.append(t)
    # 提取标题（<w:pStyle w:val="HeadingX"/> 附近的文字）
    return '\n\n'.join(paragraphs)


def _xlsx_to_ssd(filepath):
    """用 zipfile 解析 .xlsx（Excel），提取所有单元格文字"""
    rows_data = []
    with zipfile.ZipFile(filepath, 'r') as z:
        # 读取 shared strings（字符型单元格）
        shared_strings = []
        if 'xl/sharedStrings.xml' in z.namelist():
            ss_xml = z.read('xl/sharedStrings.xml').decode('utf-8', errors='ignore')
            shared_strings = re.findall(r'<t[^>]*>([^<]*)</t>', ss_xml)
        # 遍历所有 sheet
        sheet_files = sorted([n for n in z.namelist() if n.startswith('xl/worksheets/sheet') and n.endswith('.xml')])
        for sfile in sheet_files:
            sheet_xml = z.read(sfile).decode('utf-8', errors='ignore')
            # 提取单元格引用和值
            cells = re.findall(r'<c r="([A-Z]+[0-9]+)"[^>]*>([^<]*(?:<[^/][^>]*>[^<]*</[^>]+>)*)</c>', sheet_xml)
            # 简化：直接提取所有 <v> 标签值
            cell_values = re.findall(r'<c r="([A-Z]+[0-9]+)"[^>]*><v>([^<]*)</v></c>', sheet_xml)
            for ref, val in cell_values:
                col = re.match(r'([A-Z]+)', ref).group(1)
                row = ref[len(col):]
                try:
                    idx = int(val)
                    text = shared_strings[idx] if idx < len(shared_strings) else val
                except:
                    text = val
                if text:
                    rows_data.append(f"{ref}: {text}")
    return '\n'.join(rows_data) if rows_data else "(空表格)"


def _pptx_to_ssd(filepath):
    """用 zipfile 解析 .pptx（PowerPoint），提取所有文本框文字"""
    slides_text = []
    with zipfile.ZipFile(filepath, 'r') as z:
        slide_files = sorted([n for n in z.namelist() if n.startswith('ppt/slides/slide') and n.endswith('.xml')])
        for sfile in slide_files:
            slide_xml = z.read(sfile).decode('utf-8', errors='ignore')
            # 提取 <a:t> 标签文字
            texts = re.findall(r'<a:t[^>]*>([^<]*)</a:t>', slide_xml)
            line = ' '.join(t.strip() for t in texts if t.strip())
            if line:
                slides_text.append(line)
    return '\n\n'.join(slides_text)


def test():
    """简单测试"""
    import sys
    test_file = sys.argv[1] if len(sys.argv) > 1 else None
    if test_file and os.path.exists(test_file):
        result = _ooxml_to_ssd(test_file)
        print(f"=== SSD 输出 ({len(result)} 字符) ===")
        print(result[:500])
    else:
        print("用法: python _ooxml_to_ssd.py <文件路径>")


if __name__ == '__main__':
    test()
