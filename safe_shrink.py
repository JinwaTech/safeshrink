# -*- coding: utf-8 -*-

import sys as _sys

try:

    _sys.stdout.reconfigure(encoding='utf-8')

    _sys.stderr.reconfigure(encoding='utf-8')

except Exception:

    pass



"""

SafeShrink 增强版 v2.0

=====================

支持格式:

  - 纯文本: .txt, .md, .json, .csv, .xml, .html, .log

  - Word: .docx (需要 python-docx)

  - Excel: .xlsx (需要 openpyxl, 已有), .xls (需要 xlrd)

  - PPT: .pptx (需要 python-pptx, 已有)

  - PDF: .pdf (需要 pdfplumber 或 PyMuPDF)



用法:

  python safe_shrink.py slim input.docx -o output.txt

  python safe_shrink.py sanitize input.pdf -o output.pdf

  python safe_shrink.py slim input.xlsx --sheet 0

  python safe_shrink.py sanitize input.docx -o sanitized.docx --format docx

"""



import argparse

import json

import sys

from datetime import datetime

import os

import re

import zipfile

import csv

from pathlib import Path



# ========== 依赖检测 ==========

DEPS = {}

try:

    import docx

    DEPS['docx'] = True

except ImportError:

    DEPS['docx'] = False



try:

    import openpyxl

    DEPS['openpyxl'] = True

except ImportError:

    DEPS['openpyxl'] = False



try:

    import pptx

    DEPS['pptx'] = True

except ImportError:

    DEPS['pptx'] = False



try:

    import pdfplumber

    DEPS['pdfplumber'] = True

except ImportError:

    DEPS['pdfplumber'] = False



try:

    from pypdf import PdfReader, PdfWriter

    DEPS['pypdf'] = True

except ImportError:

    DEPS['pypdf'] = False



try:

    import xlrd

    DEPS['xlrd'] = True

except ImportError:

    DEPS['xlrd'] = False



try:

    from PIL import Image

    DEPS['pillow'] = True

except ImportError:

    DEPS['pillow'] = False





def check_dep(name, pkg_name=None):

    """检查依赖,打印警告"""

    if DEPS.get(name):

        return True

    pkg = pkg_name or name

    safe_stderr(msg("err_missing_dep", pkg=pkg))

    return False





# ========== 文件读取模块 ==========



def read_txt(filepath):

    """读取纯文本文件"""

    for enc in ['utf-8', 'gbk', 'gb2312', 'utf-16']:

        try:

            with open(filepath, 'r', encoding=enc) as f:

                return f.read()

        except:

            continue

    raise ValueError(f"无法读取文件: {filepath}")





def read_json(filepath):

    """读取JSON文件,返回原始文本"""

    with open(filepath, 'r', encoding='utf-8') as f:

        obj = json.load(f)

    return json.dumps(obj, ensure_ascii=False, indent=2)





def read_csv(filepath):

    """读取CSV文件"""

    lines = []

    with open(filepath, 'r', encoding='utf-8-sig', newline='') as f:

        reader = csv.reader(f)

        for row in reader:

            lines.append(','.join(row))

    return '\n'.join(lines)





def read_docx(filepath):
    """读取Word .docx文件 - 使用markitdown"""
    import markitdown
    mr = markitdown.MarkItDown()
    result = mr.convert(filepath)
    return result.text_content

def read_xlsx(filepath, sheet_index=0):

    """读取Excel .xlsx文件"""

    if not check_dep('openpyxl'):

        raise ImportError("openpyxl 未安装")

    import openpyxl

    wb = openpyxl.load_workbook(filepath, data_only=True)

    sheets = wb.sheetnames

    result_parts = []

    for idx in (sheet_index if isinstance(sheet_index, list) else [sheet_index]):

        if idx < len(sheets):

            ws = wb[sheets[idx]]

            result_parts.append(f"[Sheet: {sheets[idx]}]")

            for row in ws.iter_rows(values_only=True):

                cells = []
                for c in row:
                    if c is None:
                        cells.append('')
                    elif isinstance(c, float) and (c != c):  # NaN check
                        cells.append('')
                    else:
                        cells.append(str(c))

                if any(cells):

                    result_parts.append('\t'.join(cells))

    return '\n'.join(result_parts)





def read_xls(filepath, sheet_index=0):

    """读取Excel .xls文件(老格式)"""

    if not check_dep('xlrd', 'xlrd'):

        raise ImportError("xlrd 未安装 (需要支持.xls)")

        # 退而求其次: 尝试openpyxl

        if check_dep('openpyxl'):

            try:

                import openpyxl

                wb = openpyxl.load_workbook(filepath)

                ws = wb.active

                lines = []

                for row in ws.iter_rows(values_only=True):

                    cells = [str(c) if c else '' for c in row]

                    if any(cells):

                        lines.append('\t'.join(cells))

                return '\n'.join(lines)

            except:

                pass

        raise ImportError("xlrd 未安装,无法读取.xls文件")

    import xlrd

    wb = xlrd.open_workbook(filepath)

    sheets = wb.sheet_names()

    parts = []

    idx = sheet_index if isinstance(sheet_index, list) else sheet_index

    if idx < len(sheets):

        ws = wb.sheet_by_index(idx)

        parts.append(f"[Sheet: {sheets[idx]}]")

        for r in range(ws.nrows):

            row_data = [str(ws.cell_value(r, c)) for c in range(ws.ncols)]

            if any(c.strip() for c in row_data):

                parts.append('\t'.join(row_data))

    return '\n'.join(parts)





def read_pptx(filepath):

    """读取PowerPoint .pptx文件"""

    if not check_dep('pptx', 'python-pptx'):

        raise ImportError("python-pptx 未安装")

    import pptx

    prs = pptx.Presentation(filepath)

    slides_text = []

    for i, slide in enumerate(prs.slides, 1):

        slide_texts = []

        for shape in slide.shapes:

            if hasattr(shape, 'text') and shape.text.strip():

                slide_texts.append(shape.text.strip())

        if slide_texts:

            slides_text.append(f"[幻灯片 {i}]\n" + '\n'.join(slide_texts))

    return '\n\n'.join(slides_text)





def read_pdf_pdfplumber(filepath):

    """用pdfplumber读取PDF"""

    if not check_dep('pdfplumber', 'pdfplumber'):

        raise ImportError("pdfplumber 未安装")

    import pdfplumber

    pages_text = []

    with pdfplumber.open(filepath) as pdf:

        for i, page in enumerate(pdf.pages, 1):

            text = page.extract_text()

            if text and text.strip():

                pages_text.append(f"[页 {i}]\n{text}")

    return '\n\n'.join(pages_text)





def read_pdf_pypdf(filepath):

    """用pypdf读取PDF"""

    if not check_dep('pypdf', 'pypdf'):

        raise ImportError("pypdf 未安装")

    from pypdf import PdfReader

    reader = PdfReader(filepath)

    pages_text = []

    for i, page in enumerate(reader.pages, 1):

        text = page.extract_text()

        if text and text.strip():

            pages_text.append(f"[页 {i}]\n{text}")

    return '\n\n'.join(pages_text)





def read_pdf(filepath):

    """读取PDF,尝试多种方式"""

    errors = []

    # 优先 pdfplumber(表格支持好)

    if DEPS.get('pdfplumber'):

        try:

            return read_pdf_pdfplumber(filepath)

        except Exception as e:

            errors.append(f"pdfplumber: {e}")

    # 备选 pypdf

    if DEPS.get('pypdf'):

        try:

            return read_pdf_pypdf(filepath)

        except Exception as e:

            errors.append(f"pypdf: {e}")

    raise ImportError(f"无法读取PDF。尝试了: {', '.join(errors)}")





# ========== 文件写入模块 ==========



def write_txt(filepath, content):

    with open(filepath, 'w', encoding='utf-8') as f:

        f.write(content)





def write_json(filepath, content):

    obj = json.loads(content)

    with open(filepath, 'w', encoding='utf-8') as f:

        json.dump(obj, f, ensure_ascii=False, indent=2)





def write_docx(filepath, content):

    """写入Word .docx"""

    if not check_dep('docx', 'python-docx'):

        raise ImportError("python-docx 未安装")

    import docx

    doc = docx.Document()

    for para in content.split('\n'):

        if para.strip():

            doc.add_paragraph(para)

    doc.save(filepath)





def write_xlsx(filepath, content):

    """写入Excel .xlsx"""

    if not check_dep('openpyxl'):

        raise ImportError("openpyxl 未安装")

    import openpyxl

    wb = openpyxl.Workbook()

    ws = wb.active

    for i, line in enumerate(content.split('\n'), 1):

        if '\t' in line:

            for j, cell in enumerate(line.split('\t')):

                ws.cell(row=i, column=j+1, value=cell)

        elif line.strip():

            ws.cell(row=i, column=1, value=line)

    wb.save(filepath)






def write_xls(filepath, content):
    """写入Excel .xls (OLE2格式)"""
    try:
        import xlwt
    except ImportError:
        raise ImportError("xlwt 未安装")
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Sheet1')
    for i, line in enumerate(content.split('\n')):
        if '\t' in line:
            for j, cell in enumerate(line.split('\t')):
                ws.write(i, j, cell)
        elif line.strip():
            ws.write(i, 0, line)
    wb.save(filepath)

def write_pptx(filepath, content):

    """写入PowerPoint .pptx"""

    if not check_dep('pptx', 'python-pptx'):

        raise ImportError("python-pptx 未安装")

    import pptx

    prs = pptx.Presentation()

    for block in content.split('[幻灯片 '):

        if not block.strip():

            continue

        slide = prs.slides.add_slide(prs.slide_layouts[5])  # 空白布局

        lines = block.split('\n')

        title = lines[0].rstrip(']') if lines else f"内容 {len(prs.slides)}"

        body = '\n'.join(lines[1:]) if len(lines) > 1 else block

        if hasattr(slide.shapes, 'title') and slide.shapes.title:

            slide.shapes.title.text = title

        tf = slide.shapes.placeholders[0].text_frame if slide.shapes.placeholders else None

        if tf:

            tf.text = body

        else:

            from pptx.util import Inches, Pt

            txBox = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(8), Inches(6))

            tf2 = txBox.text_frame

            tf2.text = body

    prs.save(filepath)






def slim_native_docx(filepath, compression_rate=0.3, remove_ai=False):
    import docx
    from docx.shared import Pt
    doc = docx.Document(filepath)
    total = 0
    for para in doc.paragraphs:
        for run in para.runs:
            if run.text.strip() and run.font.size:
                try:
                    run.font.size = Pt(max(6, int(run.font.size.pt * (1 - compression_rate))))
                    total += len(run.text)
                except:
                    pass
    try:
        nsmap = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        comments = doc.element.body.find('.//w:comments', nsmap)
        if comments is not None and comments.getparent() is not None:
            comments.getparent().remove(comments)
    except:
        pass
    if remove_ai:
        try:
            cp = doc.core_properties
            cp.subject = ''
            cp.keywords = ''
        except:
            pass
    doc.save(filepath)
    return {'result': '[docx done]', 'stats': {'chars_removed': total}}

def slim_native_xlsx(filepath, compression_rate=0.3, remove_ai=False):
    import openpyxl
    from openpyxl.styles import Font
    wb = openpyxl.load_workbook(filepath, data_only=False)
    total = 0
    for sn in wb.sheetnames:
        ws = wb[sn]
        for row in ws.iter_rows():
            for cell in row:
                if cell.font and cell.font.size and compression_rate > 0:
                    try:
                        new_sz = max(6, int(cell.font.size * (1 - compression_rate)))
                        cell.font = Font(
                            name=cell.font.name, size=new_sz,
                            bold=cell.font.bold, italic=cell.font.italic,
                            color=cell.font.color
                        )
                        if cell.value and isinstance(cell.value, str):
                            total += len(cell.value)
                    except:
                        pass
                if remove_ai and cell.comment:
                    cell.comment = None
    wb.save(filepath)
    return {'success': True, 'stats': {'chars_removed': total}}

def slim_native_pptx(filepath, compression_rate=0.3, remove_ai=False):
    import pptx
    from pptx.util import Pt
    prs = pptx.Presentation(filepath)
    total = 0
    for slide in prs.slides:
        for shape in slide.shapes:
            if not hasattr(shape, 'text_frame'):
                continue
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    if run.text.strip() and run.font.size and compression_rate > 0:
                        try:
                            run.font.size = Pt(max(6, int(run.font.size.pt * (1 - compression_rate))))
                            total += len(run.text)
                        except:
                            pass
    if remove_ai:
        try:
            cp = prs.core_properties
            cp.subject = ''
            cp.keywords = ''
        except:
            pass
    prs.save(filepath)
    return {'success': True, 'stats': {'chars_removed': total}}

def write_pdf_pdfplumber(filepath, content):

    """用pdfplumber写入PDF(实际上是文本到PDF)"""

    try:

        from reportlab.pdfgen import canvas

        from reportlab.lib.pagesizes import A4

        from reportlab.pdfbase import pdfmetrics

        from reportlab.pdfbase.ttfonts import TTFont

        from reportlab.lib.styles import getSampleStyleSheet

        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

    except ImportError:

        # 没有reportlab,用备选方案:保存为同名txt

        alt = str(Path(filepath).with_suffix('.txt'))

        with open(alt, 'w', encoding='utf-8') as f:

            f.write(content)

        raise RuntimeError(f"PDF写入需要reportlab,已保存为: {alt}")

    import pdfplumber

    pdf = pdfplumber.open(filepath)

    # 实际pdfplumber不支持创建PDF,这里只是保留接口

    raise RuntimeError("pdfplumber不支持创建PDF,请使用文本输出")





# ========== 文件读取入口 ==========



READERS = {

    '.txt': read_txt,

    '.md': read_txt,

    '.ssd': read_txt,

    '.json': read_json,

    '.csv': read_csv,

    '.xml': read_txt,

    '.html': read_txt,

    '.htm': read_txt,

    '.log': read_txt,

    '.ini': read_txt,

    '.cfg': read_txt,

    '.yaml': read_txt,

    '.yml': read_txt,

    '.docx': read_docx,

    '.xlsx': read_xlsx,

    '.xls': read_xls,

    '.pptx': read_pptx,

    '.pdf': read_pdf,


    '.c': None,  # code file - skip
    '.cpp': None,  # code file - skip
    '.h': None,  # code file - skip
    '.java': None,  # code file - skip
    '.js': None,  # code file - skip
    '.ts': None,  # code file - skip
    '.sh': None,  # code file - skip
    '.bat': None,  # code file - skip
    '.css': None,  # code file - skip
    '.sql': None,  # code file - skip
    '.go': None,  # code file - skip
    '.rs': None,  # code file - skip
    '.py': None,  # code file - skip
}


# 结构化格式（slim 跳过，sanitize 用 StructSanitizer）
STRUCTURED_EXTENSIONS = {'.json', '.xml', '.html', '.htm', '.yaml', '.yml', '.csv', '.xls'}


# ============================================================
# i18n: Language detection + Message dictionary
# ============================================================
import locale as _locale

def get_lang():
    """Detect system language. zh -> 'zh', everything else -> 'en'"""
    # Check env vars first (most reliable, no deprecation)
    for var in ('LANG', 'LC_ALL', 'LANGUAGE'):
        val = os.environ.get(var, '')
        if val.startswith('zh'):
            return 'zh'
    # Fallback: try getlocale()
    try:
        lang = _locale.getlocale()[0] or ''
        if lang.startswith('zh'):
            return 'zh'
    except Exception:
        pass
    return 'en'

_LANG = get_lang()

MSG = {
    'zh': {
        # CLI main
        'reading': '[读入] {file} ({chars} 字符)',
        'code_skip': '[跳过] 代码文件不支持处理: {file}',
        'struct_skip': '[跳过] 结构化格式不支持压缩: {file}',
        'ssd_done': '[SSD 转换] 完成, {chars} 字符',
        'deep_clean': '[深度清理] 压缩率: {rate}%',
        'deep_clean_chars': '           减少字符: {chars}',
        'aggressive': '[激进压缩] 压缩率: {rate}%',
        'aggressive_chars': '           减少字符: {chars}',
        'standard': '[标准压缩] 压缩率: {rate}%',
        'standard_chars': '           减少字符: {chars}',
        'sanitize_done': '[脱敏] 共脱敏 {total} 项: {detail}',
        'sanitize_none': '[脱敏] 共脱敏 0 项: 无',
        'saved': '[保存] -> {path}',
        'saved_fallback': '[保存] -> {path} (格式降级)',
        'truncated': '\n... (共 {chars} 字符,已截断)',
        'perm_tip': '[提示] 权限不足时,可尝试指定其他输出目录:--out-dir D:\\输出',
        # Errors
        'err_convert': '[错误] 转换失败: {msg}',
        'err_read': '[错误] 读取失败: {msg}',
        'err_save': '[错误] 保存失败: {msg}',
        'err_no_input': '[错误] 请提供文本或输入文件 (-i)',
        'err_input_not_dir': '[错误] 输入路径不是目录: {path}',
        'err_no_files': '[批量转换] 未找到可转换的文件（支持: {exts}）',
        'err_no_images': '[批量压缩] 未找到图片文件（支持: {exts}）',
        'err_target_fmt': "[错误] 目标格式 '{fmt}' 暂不支持，仅支持: ssd | txt | md",
        'err_compress': '[错误] 压缩失败: {msg}',
        'err_unknown': '未知错误',
        'err_missing_dep': '[警告] 缺少 {pkg},相关功能不可用。安装: pip install {pkg}',
        'err_alt_format': '[注意] 此格式不支持直接写入,已保存为: {path}',
        'err_output_dir': "[提示] 无法创建输出目录 '{dir}',将输出到控制台",
        # Batch
        'batch_action': '[批量{action}] 文件夹: {folder}',
        'batch_output': '[输出] {dir}',
        'batch_error': '\n错误: {msg}',
        'batch_done': '  完成!耗时 {sec}秒',
        'batch_stats': '  成功: {ok}  失败: {fail}  跳过: {skip}',
        'batch_size': '  原始: {orig} → 处理后: {new}',
        'batch_saved': '  节省: {saved} ({rate:.1f}%)',
        'batch_report': '  报告: {dir}\\处理报告.txt',
        # Batch convert
        'batch_convert': '[批量转换] 文件夹: {folder}',
        'batch_format': '[目标格式] {fmt}',
        'batch_convert_ok': '  [OK] {file} -> {out} ({chars} 字符)',
        'batch_convert_done': '  完成！成功: {ok}  失败: {fail}  总计: {total}',
        # Batch compress
        'batch_compress': '[批量压缩] 文件夹: {folder}',
        'batch_quality': '[质量] {q}  [线程] {w}',
        'batch_compress_ok': '  [OK] {file} -> {out} (节省 {saved})',
        'batch_compress_done': '  完成！成功: {ok}  失败: {fail}  总计: {total}',
        # Config
        'config_output': '\n[配置] output_dir: {dir}',
        'dep_check': '=== 依赖检查 ===',
        'image_compress': '[图片压缩] {file} -> {out} ({saved})',
        'image_compress_err': '[错误] 压缩失败: {file}: {msg}',
        # version
        'version': 'SafeShrink v{ver} — 文档压缩/脱敏工具',
    },
    'en': {
        # CLI main
        'reading': '[Read] {file} ({chars} chars)',
        'code_skip': '[Skipped] Code files not supported: {file}',
        'struct_skip': '[Skipped] Structured format: {file}',
        'ssd_done': '[SSD Conversion] Done, {chars} chars',
        'deep_clean': '[Deep Clean] Compression ratio: {rate}%',
        'deep_clean_chars': '           Chars reduced: {chars}',
        'aggressive': '[Aggressive Compression] Ratio: {rate}%',
        'aggressive_chars': '           Chars reduced: {chars}',
        'standard': '[Standard Compression] Ratio: {rate}%',
        'standard_chars': '           Chars reduced: {chars}',
        'sanitize_done': '[Sanitized] Total {total} items: {detail}',
        'sanitize_none': '[Sanitized] Total 0 items: none',
        'saved': '[Saved] -> {path}',
        'saved_fallback': '[Saved] -> {path} (format downgrade)',
        'truncated': '\n... ({chars} chars total, truncated)',
        'perm_tip': '[Tip] If access denied, try: --out-dir D:\\output',
        # Errors
        'err_convert': '[Error] Conversion failed: {msg}',
        'err_read': '[Error] Read failed: {msg}',
        'err_save': '[Error] Save failed: {msg}',
        'err_no_input': '[Error] Provide text or input file (-i)',
        'err_input_not_dir': '[Error] Input path is not a directory: {path}',
        'err_no_files': '[Batch Convert] No convertible files found (supported: {exts})',
        'err_no_images': '[Batch Compress] No image files found (supported: {exts})',
        'err_target_fmt': "[Error] Target format '{fmt}' not supported. Use: ssd | txt | md",
        'err_compress': '[Error] Compression failed: {msg}',
        'err_unknown': 'Unknown error',
        'err_missing_dep': '[Warning] Missing {pkg}, feature unavailable. Install: pip install {pkg}',
        'err_alt_format': '[Note] Format not directly writable, saved as: {path}',
        'err_output_dir': "[Tip] Cannot create output dir '{dir}', outputting to console",
        # Batch
        'batch_action': '[Batch {action}] Folder: {folder}',
        'batch_output': '[Output] {dir}',
        'batch_error': '\nError: {msg}',
        'batch_done': '  Done! Elapsed {sec}s',
        'batch_stats': '  Success: {ok}  Failed: {fail}  Skipped: {skip}',
        'batch_size': '  Original: {orig} -> Processed: {new}',
        'batch_saved': '  Saved: {saved} ({rate:.1f}%)',
        'batch_report': '  Report: {dir}\\report.txt',
        # Batch convert
        'batch_convert': '[Batch Convert] Folder: {folder}',
        'batch_format': '[Target Format] {fmt}',
        'batch_convert_ok': '  [OK] {file} -> {out} ({chars} chars)',
        'batch_convert_done': '  Done! Success: {ok}  Failed: {fail}  Total: {total}',
        # Batch compress
        'batch_compress': '[Batch Compress] Folder: {folder}',
        'batch_quality': '[Quality] {q}  [Threads] {w}',
        'batch_compress_ok': '  [OK] {file} -> {out} (saved {saved})',
        'batch_compress_done': '  Done! Success: {ok}  Failed: {fail}  Total: {total}',
        # Config
        'config_output': '\n[Config] output_dir: {dir}',
        'dep_check': '=== Dependency Check ===',
        'image_compress': '[Image Compress] {file} -> {out} ({saved})',
        'image_compress_err': '[Error] Compress failed: {file}: {msg}',
        # version
        'version': 'SafeShrink v{ver} — Document compression & sanitization tool',
    },
}

def msg(key, **kwargs):
    """Get localized message by key"""
    template = MSG.get(_LANG, MSG['en']).get(key, MSG['en'].get(key, key))
    try:
        return template.format(**kwargs)
    except (KeyError, IndexError):
        return template


def safe_stderr(msg):
    """安全写入 stderr（GUI 环境下 stderr 可能已关闭）"""
    try:
        print(msg, file=sys.stderr)
    except OSError:
        pass





def read_file(filepath, options=None):

    """统一读取接口"""

    opts = options or {}

    ext = Path(filepath).suffix.lower()



    if ext == '.xlsx' and 'sheet' in opts:

        return read_xlsx(filepath, sheet_index=opts['sheet'])

    if ext == '.xls' and 'sheet' in opts:

        return read_xls(filepath, sheet_index=opts['sheet'])



    if ext in READERS and READERS[ext] is None:
        return None  # code file - skip

    if ext not in READERS:
        raise ValueError(f"不支持的格式: {ext}。支持: {', '.join(READERS.keys())}")



    return READERS[ext](filepath)





def write_file(filepath, content, fmt=None):

    """统一写入接口"""

    ext = Path(filepath).suffix.lower() if fmt is None else f'.{fmt}'



    writers = {

        '.txt': write_txt,

        '.md': write_txt,

        '.ssd': write_txt,

        '.json': write_json,

        '.csv': write_txt,

        '.docx': write_docx,

        '.xlsx': write_xlsx,

        '.xls': write_xls,

        '.pptx': write_pptx,

    }



    if ext not in writers:

        # 默认写txt

        ext = '.txt'

        alt_path = str(Path(filepath).with_suffix('.txt'))

        safe_stderr(msg("err_alt_format", path=alt_path))

        filepath = alt_path



    writers[ext](filepath, content)





# ========== Token 估算 ==========



import re as _re



def estimate_tokens(text):

    """

    估算文本的 Token 消耗(基于 GPT-4o / Claude 等主流大模型)



    参数:

        text (str): 输入文本(纯文本或 Markdown)



    返回:

        dict: {

            'total': int,       # 总 token 数

            'chinese': int,     # 中文 token

            'english': int,     # 英文 token

            'numbers': int,     # 数字 token

            'punctuation': int, # 标点 token

            'whitespace': int,  # 空白 token

            'tables': int,      # 表格 token

            'code_blocks': int, # 代码块 token

            'links': int,       # 链接 token

            'images': int,      # 图片 token(仅 Markdown 图片标记)

            'lists': int,       # 列表 token

            'headings': int,    # 标题 token

            'emphasis': int,    # 加粗/斜体 token

            'quotes': int,      # 引用块 token

            'hr': int,          # 水平线 token

            'footnotes': int,   # 脚注 token

            'math': int,        # 数学公式 token

            'html': int,        # HTML 标签 token

            'strikethrough': int,  # 删除线 token

            'checkboxes': int,  # Checkbox token

            'toc': int,         # 目录 token

        }

    """

    if not text:

        return _empty_token_result()



    stats = _empty_token_result()



    # --- 先统计 Markdown 结构元素(这些不参与基础字符统计)---



    # 1. 图片: Base64 data URI 精确计算 + 非 base64 图片按 170 估算
    _b64_pat = r'data:image/[a-zA-Z]+;base64,[A-Za-z0-9+/=]+'
    _b64_matches = _re.findall(_b64_pat, text)
    if _b64_matches:
        _b64_chars = sum(len(m.split(',', 1)[1]) for m in _b64_matches)
        stats['images'] = _b64_chars // 4
    else:
        stats['images'] = 0
    # 非 base64 图片(URL 引用),按 170 token 估算
    for m in _re.finditer(r'!\[[^\]]*\]\((?!data:image)[^)]+\)', text):
        stats['images'] += 170

# 2. 超链接: [text](url) - 非图片

    link_matches = _re.findall(r'(?<!!)\[([^\]]+)\]\(([^)]+)\)', text)

    stats['links'] = len(link_matches) * 15



    # 3. 代码块: ```...```

    code_blocks = _re.findall(r'```[^\n]*\n(.*?)```', text, _re.DOTALL)

    for block in code_blocks:

        stats['code_blocks'] += 20  # 开销

        stats['code_blocks'] += block.count('\n') * 3  # 每行

    # 行内代码: `code`

    inline_codes = _re.findall(r'`([^`]+)`', text)

    stats['code_blocks'] += len(inline_codes) * 2



    # 4. 表格: 含 | 的连续行

    table_lines = _re.findall(r'^\s*\|.+\|\s*$', text, _re.MULTILINE)

    if table_lines:

        stats['tables'] += len(table_lines) * 15  # 每行

        # 分隔行额外 +5

        for line in table_lines:

            if _re.match(r'^\s*\|[\s\-:|]+\|\s*$', line):

                stats['tables'] += 5



    # 5. 标题: # ~ ######

    headings = _re.findall(r'^#{1,6}\s+.+$', text, _re.MULTILINE)

    stats['headings'] = len(headings) * 3



    # 6. 列表项: - * + 开头,或 1. 2. 编号

    list_items = _re.findall(r'^(\s*)([-*+]|\d+\.)\s+', text, _re.MULTILINE)

    stats['lists'] = len(list_items) * 4



    # 7. 引用块: > 开头

    quotes = _re.findall(r'^>\s?.+$', text, _re.MULTILINE)

    stats['quotes'] = len(quotes) * 5



    # 8. 水平线: --- 或 *** 或 ___

    hrs = _re.findall(r'^(\s*)(---+|\*\*\*+|___+)(\s*)$', text, _re.MULTILINE)

    stats['hr'] = len(hrs) * 3



    # 9. 加粗: **text** 或 __text__

    bolds = _re.findall(r'\*\*[^*]+\*\*|__[^_]+__', text)

    stats['emphasis'] += len(bolds) * 3



    # 10. 斜体: *text* 或 _text_(排除已匹配的加粗)

    italics = _re.findall(r'(?<!\*)\*(?!\*)([^*]+?)(?<!\*)\*(?!\*)|(?<!_)_(?!_)([^_]+?)(?<!_)_(?!_)', text)

    stats['emphasis'] += len(italics) * 2



    # 11. 删除线: ~~text~~

    strikethroughs = _re.findall(r'~~[^~]+~~', text)

    stats['strikethrough'] = len(strikethroughs) * 3



    # 12. 脚注: [^n]

    footnotes = _re.findall(r'\[\^[^\]]+\]', text)

    stats['footnotes'] = len(footnotes) * 10



    # 13. 数学公式(块级): $$...$$

    math_blocks = _re.findall(r'\$\$(.*?)\$\$', text, _re.DOTALL)

    for block in math_blocks:

        stats['math'] += 20 + block.count('\n') * 5



    # 14. 数学公式(行内): $...$(排除已匹配的块级)

    inline_math = _re.findall(r'(?<!\$)\$(?!\$)([^$]+?)(?<!\$)\$(?!\$)', text)

    stats['math'] += len(inline_math) * 10



    # 15. HTML 标签

    html_tags = _re.findall(r'<([a-zA-Z][a-zA-Z0-9]*)[^>]*>', text)

    stats['html'] = len(html_tags) * 5



    # 16. Checkbox: - [ ] 或 - [x]

    checkboxes = _re.findall(r'-\s*\[[ xX]\]', text)

    stats['checkboxes'] = len(checkboxes) * 5



    # 17. 目录标记: [[toc]] 或 [TOC]

    tocs = _re.findall(r'\[\[toc\]\]|\[TOC\]', text, _re.IGNORECASE)

    stats['toc'] = len(tocs) * 8



    # --- 从原文本中移除 Markdown 标记,得到纯文本用于基础字符统计 ---

    clean = text

    # 移除代码块

    clean = _re.sub(r'```[^\n]*\n.*?```', '', clean, flags=_re.DOTALL)

    # 移除图片标记(保留 alt 文本作为纯文本,已在图片 token 中计费)

    clean = _re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', clean)

    # 移除链接(保留文本)

    clean = _re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean)

    # 移除表格分隔行

    clean = _re.sub(r'^\s*\|[\s\-:|]+\|\s*$', '', clean, flags=_re.MULTILINE)

    # 移除表格管道符

    clean = _re.sub(r'\|', ' ', clean)

    # 移除标题标记

    clean = _re.sub(r'^#{1,6}\s+', '', clean, flags=_re.MULTILINE)

    # 移除列表标记

    clean = _re.sub(r'^(\s*)([-*+]|\d+\.)\s+', r'\1', clean, flags=_re.MULTILINE)

    # 移除引用标记

    clean = _re.sub(r'^>\s?', '', clean, flags=_re.MULTILINE)

    # 移除水平线

    clean = _re.sub(r'^(\s*)(---+|\*\*\*+|___+)(\s*)$', '', clean, flags=_re.MULTILINE)

    # 移除格式标记(加粗/斜体/删除线)

    clean = _re.sub(r'\*\*([^*]+)\*\*', r'\1', clean)

    clean = _re.sub(r'__([^_]+)__', r'\1', clean)

    clean = _re.sub(r'\*([^*]+)\*', r'\1', clean)

    clean = _re.sub(r'_([^_]+)_', r'\1', clean)

    clean = _re.sub(r'~~([^~]+)~~', r'\1', clean)

    # 移除行内代码

    clean = _re.sub(r'`([^`]+)`', r'\1', clean)

    # 移除脚注

    clean = _re.sub(r'\[\^[^\]]+\]', '', clean)

    # 移除数学公式

    clean = _re.sub(r'\$\$(.*?)\$\$', '', clean, flags=_re.DOTALL)

    clean = _re.sub(r'(?<!\$)\$(?!\$)([^$]+?)(?<!\$)\$(?!\$)', '', clean)

    # 移除 HTML 标签

    clean = _re.sub(r'<[^>]+>', '', clean)

    # 移除 checkbox 标记

    clean = _re.sub(r'-\s*\[[ xX]\]', '-', clean)

    # 移除目录标记

    clean = _re.sub(r'\[\[toc\]\]|\[TOC\]', '', clean, flags=_re.IGNORECASE)



    # --- 基础字符统计 ---

    # 中文

    chinese_chars = _re.findall(r'[\u4e00-\u9fff\u3400-\u4dbf\U00020000-\U0002a6df]', clean)

    stats['chinese'] = len(chinese_chars) * 1.5



    # 英文单词

    english_words = _re.findall(r'[a-zA-Z]+(?:\'[a-zA-Z]+)?', clean)

    stats['english'] = len(english_words) * 1.0



    # 数字串

    number_groups = _re.findall(r'\d[\d,._]*\d|\d', clean)

    stats['numbers'] = len(number_groups) * 0.5



    # 标点

    punct = _re.findall(r'[,。!?、;:\u201c\u201d\u2018\u2019()【】《》...-·\u3000\uff01\uff0c\uff0e\uff1f\uff1b\uff1a\uff08\uff09\u300a\u300b\u2026\u2014\u00b7,.\-!?;:\'"()\[\]{}]', clean)

    stats['punctuation'] = len(punct) * 0.5



    # 空白

    whitespace = _re.findall(r'\s', clean)

    stats['whitespace'] = len(whitespace) * 0.3



    # 汇总

    stats['total'] = sum(v for k, v in stats.items() if k != 'total')

    # 四舍五入到整数

    for k in stats:

        stats[k] = int(round(stats[k]))



    return stats





def _empty_token_result():

    return {

        'total': 0, 'chinese': 0, 'english': 0, 'numbers': 0,

        'punctuation': 0, 'whitespace': 0, 'tables': 0, 'code_blocks': 0,

        'links': 0, 'images': 0, 'lists': 0, 'headings': 0,

        'emphasis': 0, 'quotes': 0, 'hr': 0, 'footnotes': 0,

        'math': 0, 'html': 0, 'strikethrough': 0,

        'checkboxes': 0, 'toc': 0,

    }





def format_token_summary(stats, label=""):

    """格式化 token 估算结果为可读字符串"""

    if not stats or stats['total'] == 0:

        return "0 tokens"



    prefix = f"[{label}] " if label else ""

    lines = [

        f"{prefix}预估 Token 消耗: ~{stats['total']:,}",

    ]



    # Top 分类

    cats = []

    for name, key, unit in [

        ('中文', 'chinese', ''), ('英文', 'english', '词'),

        ('代码块', 'code_blocks', ''), ('表格', 'tables', ''),

        ('图片', 'images', ''), ('链接', 'links', ''),

        ('数学公式', 'math', ''), ('HTML标签', 'html', ''),

    ]:

        v = stats.get(key, 0)

        if v > 0:

            cats.append(f"{name}: {v:,}{unit}")



    if cats:

        lines.append("  " + " | ".join(cats[:4]))

        if len(cats) > 4:

            lines.append("  " + " | ".join(cats[4:]))



    return '\n'.join(lines)





# ========== 文档减肥器 ==========



class DocSlimmer:

    """文档减肥器 - 精简文本,去除冗余"""



    # 压缩词汇映射(先处理,避免与AI痕迹冲突)

    REDUNDANT_PATTERNS = [

        (r'\n{3,}', '\n\n'),

        (r' {2,}', ' '),

        (r'\t+', ' '),

        # 程度副词冗余

        (r'非常+', '很'),

        (r'特别+', '很'),

        (r'极其+', '很'),

        (r'十分+', '很'),

        (r'相当+', '很'),

        # 重复表达

        (r'真的', ''),

        (r'实际上', ''),

        (r'其实', ''),

        # 连接词冗余

        (r'也就是说', '即'),

        (r'并且', '且'),

        (r'同时', '且'),

        (r'但是', '但'),

        (r'然而', '但'),

        # 标点冗余

        (r'[。]{2,}', '。'),

        (r'[,]{2,}', ','),

        (r'[!]{2,}', '!'),

        (r'[?]{2,}', '?'),

        # 清理连续标点+空格

        (r'[。!?,;]\s*', lambda m: m.group()[:-1] + ' ' if m.group().endswith(',') or m.group().endswith('。') else m.group()),

    ]



    # AI写作痕迹(后处理)

    AI_PATTERNS = [

        (r'首先、?其次、?再次、?最后', '第一、第二、第三'),

        (r'综上所述', '总之'),

        (r'值得注意的是', '但'),

        (r'可以说是不胜枚举', '不胜枚举'),

        (r'可以说', ''),

        (r'毋庸置疑', ''),

        (r'显而易见', ''),

        (r'不言而喻', ''),

        (r'众所周知', ''),

        (r'从某种意义上', ''),

        (r'总的来说', '总体'),

        (r'坦白地说', ''),

        (r'客观地说', ''),

        (r'想必', ''),

        (r'不由得', ''),

        (r'不禁', ''),

        (r'想必大家', ''),

        (r'那么我们', ''),

        (r'首先、其次、最后', '第一、第二'),

    ]



    def slim(self, text, compression_rate=0.3, remove_ai=False):

        if not text or not text.strip():

            return {"result": "", "stats": {}}



        original_length = len(text)

        result = text



        # 根据压缩强度决定应用的规则数量

        # compression_rate: 0.0-1.0,表示目标压缩比例

        # 0.0 = 不压缩,1.0 = 最大压缩



        # 基础清理(总是应用)

        for pattern, replacement in self.REDUNDANT_PATTERNS:

            if callable(replacement):

                result = re.sub(pattern, replacement, result)

            else:

                result = re.sub(pattern, replacement, result)



        # 根据压缩强度应用额外的压缩

        if compression_rate > 0.1:

            # 去除重复字符

            result = re.sub(r'(\w)\1{2,}', r'\1', result)



        if compression_rate > 0.3:

            # 移除多余的空格和制表符

            result = re.sub(r' {2,}', ' ', result)

            result = re.sub(r'\t+', ' ', result)



        if compression_rate > 0.7:

            # 移除某些冗余词汇

            result = re.sub(r'([^)]*)', '', result)  # 移除括号内容

            result = re.sub(r'\([^)]*\)', '', result)   # 移除英文括号内容



        if compression_rate > 0.7:

            # 激进压缩:移除更多内容

            result = re.sub(r'【[^】]*】', '', result)  # 移除方括号

            result = re.sub(r'\[[^\]]*\]', '', result)



        # 去AI味

        if remove_ai:

            for pattern, replacement in self.AI_PATTERNS:

                result = re.sub(pattern, replacement, result)



        # 清理残留的连续标点和空格

        result = re.sub(r'[,。;!?\s]+', lambda m: ' ' if ' ' in m.group() and len(m.group()) > 1 else m.group(), result)

        result = result.strip()



        result = result.strip()

        new_length = len(result)

        actual_rate = (original_length - new_length) / original_length if original_length > 0 else 0



        return {

            "result": result,

            "stats": {

                "original_length": original_length,

                "new_length": new_length,

                "compression_rate": round(actual_rate * 100, 1),

                "reduced_chars": original_length - new_length

            }

        }





# ========== 文档脱敏器 ==========



class DocSanitizer:

    """文档脱敏器 - 去除个人信息,可选择性脱敏"""



    # 敏感信息正则(按分类)

    PATTERNS = {

        # ===== 个人敏感信息 =====

        '手机号': r'(?<!\d)1[3-9]\d[\s\-]?\d{4}[\s\-]?\d{4}(?!\d)',

        '邮箱': r'\b[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,}\b',

        '身份证': r'(?<!\d)\d{17}[\dXx](?!\d)',

        '银行卡': r'(?<!\d)\d{16,19}(?!\d)',

        'IP地址': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',

        # ===== 商业敏感信息 =====

        '社会信用代码': r'(?<!\d)91\d{16}(?!\d)',        # 统一社会信用代码18位

        '营业执照号': r'(?<!\d)\d{15}(?!\d)',            # 15位工商注册号

        '开户许可证号': r'(?<!\d)[A-Z0-9]{14,16}(?!\d)',  # 14-16位开户许可

        '投标/成交价': r'[¥¥]?\d{1,12}(?:\.\d{2})?(?![元])',  # 金额(需配合上下文判断)

        '合同编号': r'(?<![a-zA-Z])[A-Z]{2,4}[-#]?\d{2,4}[-]?\d{2,8}(?![a-zA-Z])',  # HT/HT-2026-XXXX类

        '采购/订单编号': r'(?<![a-zA-Z])(?:CG|PO|DD|HT|FC)[-_]?\d{4,12}(?![a-zA-Z])',  # CG/PO/FC开头编号

        '固定电话': r'(?<!\d)0\d{2,3}[-]?\d{7,8}(?!\d)',  # 021-12345678

        '传真号': r'(?<!\d)(?:传真|Fax)[-:]?\s*0\d{2,3}[-]?\d{7,8}(?!\d)',

        '工号/学号': r'(?<![a-zA-Z])(?:工号|学号|员工号|编号)[-:]?\s*[A-Z0-9]{4,12}(?![a-zA-Z])',

        '项目代号': r'(?<![a-zA-Z])(?:项目[编号码]|PRJ|PROJ)[-_]?\d{2,8}(?![a-zA-Z])',

        '邮编': r'(?<!\d)\d{6}(?!\d)',

        # ===== 证件/设备标识 =====

        '护照号': r'(?<![A-Za-z])[EeGgPpDdSsHhLl][A-Za-z]?\d{7,9}(?!\d)',  # 中国护照

        'Mac地址': r'(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}',  # MAC地址

        'IMEI': r'(?<!\d)\d{15}(?!\d)',  # IMEI号15位

        # ===== 车辆/社保 =====

        '车牌号': r'[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领警][A-Z][·]?[A-HJ-NP-Z0-9]{4,5}[A-HJ-NP-Z0-9挂学港澳]?',

        '社保卡号': r'(?<!\d)\d{14,18}(?!\d)',  # 社保卡号14-18位

        '医保卡号': r'(?<!\d)\d{10,18}(?!\d)',  # 医保卡号10-18位

        # ===== 医疗/公文 =====

        '病历号': r'(?:(?:BL|MR|EMR|MZ|ZY|门诊号?|住院号?|病历号?|病案号?)[::\-]?\d{4,}|[A-Z]{2,3}[-]?\d{6,12})',

        '公文份号': r'(?:(?:No|NO|Nr|No)[-:\s]*\d{4,}|份号[::\s]+\d+|\d{4,}[-]\d{4}[-]\d{4,}|第\d{2,4}[-]\d{4,}号|文件编号[::\s]*[A-Z]{2,3}[-_]\d{2,4}[-_]\d{3,})',

        '公文密级': r'(?:【[绝密机密秘密内部]+】|绝密\s*[★☆]?\s*\d*\s*年?|[机密秘密内部]+(?:文件|资料|通知|信息))',

        '公文文号': r'[\u4e00-\u9fa5]+发〔\d{4}〕\s*(?:第\s*)?\d+(?:号)?|[\u4e00-\u9fa5]*(?:政办发|发)〔\d{4}〕\s*(?:第\s*)?\d+号?|〔\d{4}〕(?:第?\s*\d+号?)',  # 公文文号

    }



    # 名称映射

    ITEM_LABELS = {

        '手机号': '手机号',

        '邮箱': '邮箱',

        '身份证': '身份证',

        '银行卡': '银行卡',

        'IP地址': 'IP地址',

    }



    # 英文敏感信息正则 (宽松匹配, 宁误勿漏)
    EN_PATTERNS = {
        # 1. Phone (US + UK combined)
        'Phone': r'(?:(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})|(?:(?:\+?44[-.\s]?)?\d{2,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4})',
        # 2. Email
        'Email': r'\b[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,}\b',
        # 3. SSN (US): 123-45-6789
        'SSN': r'\b\d{3}-\d{2}-\d{4}\b',
        # 4. Credit Card: 1234-5678-9012-3456 or 16 consecutive digits
        'Credit Card': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        # 5. IP Address
        'IP Address': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
        # 6. Tax ID / EIN: 12-3456789
        'Tax ID': r'\b\d{2}-\d{7}\b',
        # 7. Business License: BL-12345678
        'Business License': r'\b(?:BL|LIC|REG|BN)[-_\s]?\d{6,15}\b',
        # 8. Bank Routing (ABA): 021000021 (9 digits starting with 0/1/2/3/6/7/8)
        'Bank Routing': r'\b[0123678]\d{8}\b',
        # 9. Currency Amount: $1,234.56 / £999 / €1.00
        'Currency Amount': r'(?:\$|£|€|USD|GBP|EUR)\s?\d[\d,]*\.?\d*',
        # 10. Contract Number: Contract#ABC123
        'Contract Number': r'\b(?:Contract|Agreement|CA)[-_\s#]*[A-Z0-9]{4,20}\b',
        # 11. PO Number: PO#12345678
        'PO Number': r'\b(?:PO|Purchase Order|Order)[-_\s#]*\d{4,16}\b',
        # 12. Fax Number: Fax: (555) 123-4567
        'Fax Number': r'\b(?:Fax|FAX|fax)[-_\s:]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        # 13. Employee ID: EMP-123456
        'Employee ID': r'\b(?:ID|Emp|Employee|Staff)[-_\s#]*[A-Z0-9]{4,12}\b',
        # 14. Student ID: SID-20240001
        'Student ID': r'\b(?:Student|SID|Stu)[-_\s#]*[A-Z0-9]{4,12}\b',
        # 15. Project Code: PRJ-2024-001
        'Project Code': r'\b(?:Project|PRJ|PRG)[-_\s#]*[A-Z0-9]{3,12}\b',
        # 16. ZIP Code (US): 90210 or 90210-1234
        'ZIP Code': r'\b\d{5}(?:-\d{4})?\b',
        # 17. Passport (US): C12345678 (letter + 8 digits)
        'Passport': r'\b[A-Z][0-9]{8}\b',
        # 18. MAC Address (universal)
        'MAC Address': r'(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}',
        # 19. IMEI (universal): 15 digits
        'IMEI': r'\b\d{15}\b',
        # 20. License Plate: ABC-1234 / AB12 CDE
        'License Plate': r'\b[A-Z]{2,3}[-\s]?\d{1,4}[-\s]?[A-Z]{0,3}\b',
        # 21. NINO (UK National Insurance): AB123456C
        'NINO': r'\b(?!BG|GB|NK|KN|NT|TN|ZZ)[A-CEGHJ-PR-TW-Z]{2}\s?\d{2}\s?\d{2}\s?\d{2}\s?[A-D]\b',
        # 22. NHS Number (UK): 123 456 7890
        'NHS Number': r'\b\d{3}[- ]?\d{3}[- ]?\d{4}\b',
        # 23. Medical Record: MRN-12345678
        'Medical Record': r'\b(?:MRN|MR|Medical Record)[-_\s#]*\d{6,12}\b',
        # 24. Document Serial: DOC-2024-00001
        'Document Serial': r'\b(?:Serial|Doc)[-_\s#]*[A-Z]{2,4}[-_]?\d{4}[-_]?\d{4,8}\b',
        # 25. Classification Level: SECRET / TOP SECRET / CONFIDENTIAL
        'Classification Level': r'\b(?:TOP SECRET|SECRET|CONFIDENTIAL|UNCLASSIFIED|RESTRICTED)\b',
        # 26. Document Reference: No.2024-001
        'Document Reference': r'\b(?:No\.?|Ref\.?)[-_\s#]*\d{4}[-/]\d{1,6}\b',
    }

    @staticmethod




    def available_items():

        return list(DocSanitizer.PATTERNS.keys()) + list(DocSanitizer.EN_PATTERNS.keys())



    def _mask_phone(self, m):

        p = m.group()

        return f"{p[:3]}****{p[7:]}"



    def _mask_email(self, m):

        e = m.group()

        parts = e.split('@')

        if len(parts) == 2:

            name, domain = parts

            n = len(name)

            if n >= 3:

                return f"{name[:2]}***@{domain}"

            elif n == 2:

                return f"{name[0]}***@{domain}"

            else:

                return f"***@{domain}"

        return e



    def _mask_id(self, m):

        i = m.group()

        return f"{i[:6]}**********{i[-1] if len(i)==18 else ''}"



    def _mask_bank(self, m):

        b = m.group()

        return f"{b[:4]}****{b[-4:]}"



    def _mask_ip(self, m):

        return 'xxx.xxx.xxx.xxx'



    def _mask_passport(self, m):

        p = m.group()

        if len(p) >= 5:

            return p[0] + '*' * (len(p) - 2) + p[-1]

        return '*' * len(p)



    def _mask_mac(self, m):

        mac = m.group()

        parts = mac.replace('-', ':').split(':')

        if len(parts) == 6:

            return ':'.join([parts[0]] + ['****'] + [parts[-1]])

        return '**:**:**:**:**:**'



    def _mask_imei(self, m):

        e = m.group()

        if len(e) >= 8:

            return e[:6] + '******' + e[-6:]

        return '*' * len(e)



    def _mask_plate(self, m):

        p = m.group()

        return p[:2] + '*' * (len(p) - 2)



    def _mask_social_card(self, m):

        c = m.group()

        return c[:4] + '*' * (len(c) - 8) + c[-4:]



    def _mask_medical_record(self, m):

        c = m.group()

        digits = re.sub(r'\D', '', c)

        prefix = re.sub(r'\d', '', c)

        return prefix + '*' * len(digits)



    def _mask_docnum(self, m):

        c = m.group()

        digits = re.sub(r'\D', '', c)

        prefix = re.sub(r'\d', '', c)

        return prefix + '*' * len(digits)



    def _mask_doclevel(self, m):

        c = m.group()

        if c.startswith('【') and c.endswith('】'):

            return '【' + '*' * (len(c) - 4) + '】'

        if '文件' in c:

            return '*' * len(c)

        return re.sub(r'[*☆★\d]+', '*', c)



    def _mask_docref(self, m):

        c = m.group()

        return re.sub(r'\d+(?=号)', lambda x: '*' * len(x.group()), c)



    def sanitize(self, text, custom_words=None, items=None):

        if not text:

            return {"result": "", "stats": {"total": 0}}



        stats = {}

        result = text



        if items is None:

            items = list(self.PATTERNS.keys()) + list(self.EN_PATTERNS.keys())



        def mask_code(m):

            c = m.group()

            if len(c) <= 4:

                return '*' * len(c)

            half = len(c) // 2

            return f"{c[:half]}***{c[-half:]}"



        def mask_phone_last(m):

            p = m.group()

            digits = re.sub(r'\D', '', p)

            if len(digits) >= 8:

                return f"{digits[:3]}****{digits[-4:]}"

            return '****'



        def mask_social_credit(m):

            c = m.group()

            if len(c) == 18:

                return f"{c[:4]}**********{c[-4:]}"

            return mask_code(m)



        def mask_landline(m):

            p = m.group()

            digits = re.sub(r'\D', '', p)

            if len(digits) >= 8:

                return f"{digits[:3]}****{digits[-4:]}"

            return '****'



        def mask_fax(m):

            return '***-********'



        def mask_amount(m):

            return m.group()[:1] + '***'



        # ===== 个人敏感信息 =====

        if '手机号' in items:

            found = re.findall(self.PATTERNS['手机号'], result)

            stats['手机号'] = len(found)

            result = re.sub(self.PATTERNS['手机号'], self._mask_phone, result)



        if '邮箱' in items:

            found = re.findall(self.PATTERNS['邮箱'], result)

            stats['邮箱'] = len(found)

            result = re.sub(self.PATTERNS['邮箱'], self._mask_email, result)



        if '身份证' in items:

            found = re.findall(self.PATTERNS['身份证'], result)

            stats['身份证'] = len(found)

            result = re.sub(self.PATTERNS['身份证'], self._mask_id, result)



        if '银行卡' in items:

            found = re.findall(self.PATTERNS['银行卡'], result)

            stats['银行卡'] = len(found)

            result = re.sub(self.PATTERNS['银行卡'], self._mask_bank, result)



        if 'IP地址' in items:

            found = re.findall(self.PATTERNS['IP地址'], result)

            stats['IP地址'] = len(found)

            result = re.sub(self.PATTERNS['IP地址'], self._mask_ip, result)



        # ===== 商业敏感信息 =====

        if '社会信用代码' in items:

            found = re.findall(r'(?<![A-Z0-9])[0-9A-Z]{18}(?![A-Z0-9])', result)

            stats['社会信用代码'] = len(found)

            result = re.sub(r'(?<![A-Z0-9])[0-9A-Z]{18}(?![A-Z0-9])', mask_social_credit, result)



        if '营业执照号' in items:

            found = re.findall(r'(?<!\d)\d{15}(?!\d)', result)

            stats['营业执照号'] = len(found)

            result = re.sub(r'(?<!\d)\d{15}(?!\d)', lambda m: f"{m.group()[:5]}****{m.group()[-3:]}", result)



        if '开户许可证号' in items:

            found = re.findall(r'(?<![A-Z0-9])[A-Z0-9]{14,16}(?![A-Z0-9])', result)

            stats['开户许可证号'] = len(found)

            result = re.sub(r'(?<![A-Z0-9])[A-Z0-9]{14,16}(?![A-Z0-9])', mask_code, result)



        if '投标/成交价' in items:

            price_count = 0

            # 1. 带货币符号的金额

            found_sym = re.findall(r'[¥¥$]\s*[\d,]+(?:\.\d+)?', result)

            price_count += len(found_sym)

            for m in found_sym:

                digits = re.sub(r'[^\d]', '', m)

                prefix = m[:len(m) - len(digits)]

                result = result.replace(m, prefix + '*' * min(len(digits), 8), 1)

            # 2. USD格式

            found_usd = re.findall(r'USD\s*[\d,]+(?:\.\d+)?', result)

            price_count += len(found_usd)

            for m in found_usd:

                digits = re.sub(r'[^\d]', '', m)

                result = result.replace(m, 'USD ' + '*' * min(len(digits), 6), 1)

            # 3. 纯数字+单位

            found_unit = re.findall(r'[\d,]+(?:\.\d+)?\s*(?:万|亿|美元|欧元|英镑|元)', result)

            price_count += len(found_unit)

            for m in found_unit:

                digits = re.sub(r'[^\d]', '', m)

                unit = re.sub(r'[\d,\s]', '', m)

                result = result.replace(m, '*' * min(len(digits), 8) + unit, 1)

            # 4. 人民币中文大写金额

            found_cn = re.findall(r'人民币[零壹贰叁肆伍陆柒捌玖拾佰仟萬万〇\d\u6574\u5146\u4ebf\u4e07]+(?:元\u6574|元)?', result)

            price_count += len(found_cn)

            for m in found_cn:

                result = result.replace(m, '人民币*元整', 1)

            # 5. 上下文关键词附近的数字

            price_kw = r'(?:价格|报价|投标|成交|中标|预算|金额|总价|单价|限价|底价|费率|折扣|优惠|费用|成本|售价|买价|卖价|估值|挂牌|起拍|报价单|价格表|清单|项目价|合同价|总报价|参考价)'

            ctx_pattern = re.compile(price_kw + r'[^\d]{0,8}[\d,]+(?:\.\d+)?')

            found_ctx = list(ctx_pattern.finditer(result))

            # 从后往前替换避免位移

            replaced_nums = set()

            for cm in reversed(found_ctx):

                num_match = re.search(r'[\d,]+(?:\.\d+)?', cm.group())

                if num_match:

                    num_str = num_match.group()

                    digits = re.sub(r'[^\d]', '', num_str)

                    if len(digits) >= 2 and num_str not in replaced_nums:

                        result = result[:cm.start() + num_match.start()] + '*' * min(len(digits), 8) + result[cm.start() + num_match.end():]

                        replaced_nums.add(num_str)

            price_count += len(replaced_nums)

            stats['投标/成交价'] = price_count

        if '合同编号' in items:

            found = re.findall(r'[A-Z]{2,8}[-_/](?:[A-Z0-9]+[-_/])*[A-Z0-9]*\d{4,}[A-Z0-9]*(?:[-_/][A-Z0-9]+)*', result)

            stats['合同编号'] = len(found)

            result = re.sub(r'[A-Z]{2,8}[-_/](?:[A-Z0-9]+[-_/])*[A-Z0-9]*\d{4,}[A-Z0-9]*(?:[-_/][A-Z0-9]+)*', mask_code, result)



        if '采购/订单编号' in items:

            found = re.findall(r'(?<![A-Z])(?:CG|PO|DD|FC)[-_]?\d{4,12}(?![A-Z0-9])', result, re.IGNORECASE)

            stats['采购/订单编号'] = len(found)

            result = re.sub(r'(?<![A-Z])(?:CG|PO|DD|FC)[-_]?\d{4,12}(?![A-Z0-9])', mask_code, result, flags=re.IGNORECASE)



        if '固定电话' in items:

            found = re.findall(self.PATTERNS['固定电话'], result)

            stats['固定电话'] = len(found)

            result = re.sub(self.PATTERNS['固定电话'], mask_landline, result)



        if '传真号' in items:

            found = re.findall(self.PATTERNS['传真号'], result)

            stats['传真号'] = len(found)

            result = re.sub(self.PATTERNS['传真号'], mask_fax, result)



        if '工号/学号' in items:

            found = re.findall(self.PATTERNS['工号/学号'], result)

            stats['工号/学号'] = len(found)

            result = re.sub(self.PATTERNS['工号/学号'], mask_code, result)



        if '项目代号' in items:

            found = re.findall(r'(?<![a-zA-Z])(?:项目[编号码]|PRJ|PROJ)[-_]?\d{2,8}(?![a-zA-Z0-9])', result, re.IGNORECASE)

            stats['项目代号'] = len(found)

            result = re.sub(r'(?<![a-zA-Z])(?:项目[编号码]|PRJ|PROJ)[-_]?\d{2,8}(?![a-zA-Z0-9])', mask_code, result, flags=re.IGNORECASE)



        if '邮编' in items:

            found = re.findall(r'(?<!\d)\d{6}(?!\d)', result)

            stats['邮编'] = len(found)


        # ===== 英文敏感信息 =====
        _en_items = {k: v for k, v in self.EN_PATTERNS.items()
                     if items is None or k in items}

        _en_masks = {
            'Phone': lambda m: re.sub(r'\d', '*', m.group()[:-4]) + m.group()[-4:],
            'SSN': lambda m: '***-**-' + m.group()[-4:],
            'Credit Card': lambda m: '****-****-****-' + re.sub(r'\D', '', m.group())[-4:],
            'Email': self._mask_email,
            'IP Address': self._mask_ip,
            'Tax ID': lambda m: '**-' + m.group()[-4:],
            'Business License': lambda m: m.group()[:3] + '*' * (len(m.group()) - 3),
            'Bank Routing': lambda m: '****' + m.group()[-4:],
            'Currency Amount': lambda m: m.group()[0] + '***',
            'Contract Number': lambda m: m.group()[:8] + '****',
            'PO Number': lambda m: m.group()[:3] + '****',
            'Fax Number': lambda m: re.sub(r'\d', '*', m.group()[:-4]) + m.group()[-4:],
            'Employee ID': lambda m: m.group()[:3] + '****',
            'Student ID': lambda m: m.group()[:3] + '****',
            'Project Code': lambda m: m.group()[:4] + '****',
            'ZIP Code': lambda m: m.group()[:2] + '***',
            'Passport': lambda m: m.group()[0] + '*' * (len(m.group()) - 1),
            'MAC Address': lambda m: m.group()[:8] + ':**:**:**',
            'IMEI': lambda m: m.group()[:6] + '******' + m.group()[-6:],
            'License Plate': lambda m: m.group()[:2] + '*' * (len(m.group()) - 2),
            'NINO': lambda m: m.group()[:2] + '****' + m.group()[-1],
            'NHS Number': lambda m: '***-***-' + m.group()[-4:],
            'Medical Record': lambda m: m.group()[:4] + '****',
            'Document Serial': lambda m: m.group()[:4] + '****',
            'Classification Level': lambda m: '*' * len(m.group()),
            'Document Reference': lambda m: m.group()[:3] + '****',
        }

        # ===== 新增类型（统一使用 self.PATTERNS）=====

        if '护照号' in items:
            found = re.findall(self.PATTERNS['护照号'], result)
            stats['护照号'] = len(found)
            result = re.sub(self.PATTERNS['护照号'], lambda m: m.group()[0] + '*' * (len(m.group()) - 2) + m.group()[-1], result)

        if 'Mac地址' in items:
            found = re.findall(self.PATTERNS['Mac地址'], result)
            stats['Mac地址'] = len(found)
            def _mask_mac(m):
                c = m.group()
                sep = ':' if ':' in c else '-'
                parts = c.split(sep)
                return sep.join([parts[0]] + ['****'] + [parts[-1]])
            result = re.sub(self.PATTERNS['Mac地址'], _mask_mac, result)

        if 'IMEI' in items:
            found = re.findall(self.PATTERNS['IMEI'], result)
            stats['IMEI'] = len(found)
            result = re.sub(self.PATTERNS['IMEI'], lambda m: m.group()[:6] + '******' + m.group()[-6:], result)

        if '车牌号' in items:
            found = re.findall(self.PATTERNS['车牌号'], result)
            stats['车牌号'] = len(found)
            result = re.sub(self.PATTERNS['车牌号'], lambda m: m.group()[:2] + '*' * (len(m.group()) - 2), result)

        if '社保卡号' in items:
            found = re.findall(self.PATTERNS['社保卡号'], result)
            stats['社保卡号'] = len(found)
            result = re.sub(self.PATTERNS['社保卡号'], lambda m: m.group()[:4] + '*' * (len(m.group()) - 8) + m.group()[-4:], result)

        if '医保卡号' in items:
            found = re.findall(self.PATTERNS['医保卡号'], result)
            stats['医保卡号'] = len(found)
            result = re.sub(self.PATTERNS['医保卡号'], lambda m: m.group()[:4] + '*' * (len(m.group()) - 6) + m.group()[-4:], result)

        if '病历号' in items:
            found = re.findall(self.PATTERNS['病历号'], result)
            stats['病历号'] = len(found)
            def _mask_medical(m):
                digits = re.sub(r'\D', '', m.group())
                prefix = re.sub(r'\d', '', m.group())
                return prefix + '*' * len(digits)
            result = re.sub(self.PATTERNS['病历号'], _mask_medical, result)

        if '公文份号' in items:
            found = re.findall(self.PATTERNS['公文份号'], result)
            stats['公文份号'] = len(found)
            def _mask_doc_no(m):
                digits = re.sub(r'\D', '', m.group())
                prefix = re.sub(r'\d', '', m.group())
                return prefix + '*' * len(digits)
            result = re.sub(self.PATTERNS['公文份号'], _mask_doc_no, result)

        if '公文密级' in items:
            found = re.findall(self.PATTERNS['公文密级'], result)
            stats['公文密级'] = len(found)
            def _mask_doc_sec(m):
                t = m.group()
                if t.startswith('【') and t.endswith('】'):
                    return '【' + '*' * (len(t) - 4) + '】'
                return '*' * len(t)
            result = re.sub(self.PATTERNS['公文密级'], _mask_doc_sec, result)

        if '公文文号' in items:
            found = re.findall(self.PATTERNS['公文文号'], result)
            stats['公文文号'] = len(found)
            result = re.sub(self.PATTERNS['公文文号'], lambda m: re.sub(r'\d+(?=号)', lambda x: '*' * len(x.group()), m.group()), result)





        for en_name, en_pattern in _en_items.items():
            if en_name in ('Email', 'IP Address'):
                continue  # Already handled above
            mask_fn = _en_masks.get(en_name, lambda m: '***')
            found = re.findall(en_pattern, result)
            if found:
                stats[en_name] = len(found)
                result = re.sub(en_pattern, mask_fn, result)


        # 自定义敏感词(始终处理)

        custom_count = 0

        if custom_words:

            for word in custom_words:

                if word.strip() and len(word) >= 2:

                    count = result.count(word)

                    if count > 0:

                        masked = word[0] + '*' * (len(word) - 2) + word[-1] if len(word) > 2 else '**'

                        result = result.replace(word, masked)

                        custom_count += count

        if custom_count > 0:

            stats['自定义'] = custom_count



        stats['总计'] = sum(stats.values())



        return {

            "result": result.strip(),

            "stats": stats

        }





# ========== 批量处理入口 ==========



def cmd_batch(args):

    """批量处理命令"""

    from batch_processor import batch_process

    import shutil



    # 确定输出目录

    if args.out_dir:

        out_dir = args.out_dir

    else:

        cfg = load_config()

        default_out = cfg.get('output_dir', 'output')

        if default_out == 'output':

            # 默认输出到源目录的父目录

            src_parent = str(Path(args.folder).resolve().parent)

            ts = datetime.now().strftime('%Y%m%d_%H%M%S')

            out_dir = os.path.join(src_parent, f"{Path(args.folder).name}_处理结果_{ts}")

        else:

            out_dir = default_out



    # 选项

    options = {}

    if args.command == 'batch-slim':

        options['compression'] = args.compression

        options['remove_ai'] = args.ai

        action = 'slim'

    else:

        options['custom_words'] = args.words or []

        options['sanitize_items'] = args.items or None

        action = 'sanitize'



    print(msg("batch_action", action=action, folder=args.folder))

    print(msg("batch_output", dir=out_dir))

    print()



    result = batch_process(

        folder_path=args.folder,

        action=action,

        options=options,

        recursive=not args.no_recursive,

        workers=args.workers or 4,

        out_base=out_dir

    )



    if 'error' in result and result.get('total', 0) == 0:

        print(msg("batch_error", msg=result['error']))

        return



    s = result['summary']

    print()

    print(f"{'='*50}")

    print(msg("batch_done", sec=s['elapsed_seconds']))

    print(msg("batch_stats", ok=s['success'], fail=s['error'], skip=s['skip']))

    if s['total_input_size'] > 0:

        rate = s['size_reduced'] / s['total_input_size'] * 100

        print(msg("batch_size", orig=format_size(s['total_input_size']), new=format_size(s['total_output_size'])))

        print(msg("batch_saved", saved=format_size(s['size_reduced']), rate=rate))

    print(msg("batch_output", dir=result['output_dir']))

    print(msg("batch_report", dir=result['output_dir']))

    print(f"{'='*50}")



    # 打印报告

    print("\n" + result['report'])





# ========== 主程序 ==========



def load_config():

    """加载配置"""

    config_path = Path(__file__).parent / 'config.json'

    if config_path.exists():

        try:

            with open(config_path, 'r', encoding='utf-8') as f:

                return json.load(f)

        except Exception:

            pass

    return {}





def resolve_output_path(input_path, action, user_output, out_dir, fmt):

    """解析输出路径,支持:手动指定 / 默认output目录 / 同目录"""

    Path_like = type(Path())



    # 如果用户直接指定了完整路径

    if user_output:

        return Path(user_output)



    # 确定输出目录

    if out_dir:

        out = Path(out_dir)

    else:

        cfg = load_config()

        default_out = cfg.get('output_dir')

        if default_out:

            out = Path(__file__).parent / default_out

        else:

            # 默认:源文件同目录

            out = Path(input_path).parent



    # 创建输出目录(如果不存在)

    if not out.exists():

        try:

            out.mkdir(parents=True, exist_ok=True)

        except PermissionError:

            safe_stderr(msg("err_output_dir", dir=out))

            out = None

        except Exception:

            out = None



    # 生成文件名

    src = Path(input_path)

    action_tag = '减肥' if action == 'slim' else '脱敏'



    if src.suffix.lower() in ['.docx', '.xlsx', '.xls', '.pptx', '.pdf']:

        # 格式文件:根据 fmt 决定输出格式
        stem = src.stem
        if fmt and fmt in ['ssd', 'txt']:
            out_name = f"{stem}_{action_tag}.{fmt}"
        elif fmt == 'original':
            out_name = f"{stem}_{action_tag}{src.suffix}"
        else:
            out_name = f"{stem}_{action_tag}.ssd"

    else:

        # 文本文件

        stem = src.stem

        if fmt and fmt in ['ssd', 'txt']:
            # SSD/深度清理:纯格式转换,不加 _减肥 后缀
            out_name = f"{stem}.{fmt}"
        else:
            # 标准/激进压缩:保持原扩展名,加 _减肥 后缀
            out_name = f"{stem}_{action_tag}{src.suffix}"



    return out / out_name





def main():

    # 加载配置

    cfg = load_config()



    parser = argparse.ArgumentParser(

        description='SafeShrink v2.0 - 文档减肥 & 脱敏(支持Office/PDF)',

        formatter_class=argparse.RawDescriptionHelpFormatter,

        epilog='''

支持格式:

  文本: .txt .md .json .csv .xml .html .log

  Word: .docx  Excel: .xlsx .xls  PPT: .pptx  PDF: .pdf



保存策略:

  - 不覆盖源文件,自动另存

  - 默认保存到 output/ 子目录(可在 config.json 中修改)

  - 也可用 --out-dir 指定输出目录



示例:

  # 文档减肥(自动保存到 output/)

  safeshrink slim input.pdf

  safeshrink slim input.docx -o custom.txt

  safeshrink slim "要精简的文本" -o custom.txt



  # 文档脱敏(自动保存到 output/)

  safeshrink sanitize input.xlsx --out-dir D:\\输出

  safeshrink sanitize "文本..." --words 张三



  # 查看依赖

  safeshrink --check

        '''

    )



    parser.add_argument('--check', action='store_true', help='检查依赖状态')

    parser.add_argument('--version', action='version', version='SafeShrink v1.2.3')



    subparsers = parser.add_subparsers(dest='command', help='子命令')



    # 全局 JSON 输出标志(顶级参数,对 slim/sanitize 生效)

    parser.add_argument('--json', dest='json_output', action='store_true',

                        help='以 JSON 格式输出结果(供程序调用)')



    # slim

    sp = subparsers.add_parser('slim', help='文档减肥')

    sp.add_argument('text', nargs='?', help='要处理的文本')

    sp.add_argument('-i', '--input', help='输入文件')

    sp.add_argument('-o', '--output', help='输出文件路径(完整路径)')

    sp.add_argument('-d', '--out-dir', help='输出目录(默认使用 config.json 中的 output_dir)')

    sp.add_argument('-m', '--mode', choices=['standard', 'aggressive', 'deep-clean', 'ssd'],
                    default='standard', help='处理模式:standard(标准压缩) | aggressive(激进压缩) | deep-clean(深度清理) | ssd(转换为SSD)')

    sp.add_argument('-c', '--compression', type=float, default=0.3, help='压缩率 (0.0-1.0,仅 standard/aggressive 模式生效)')

    sp.add_argument('--ai', action='store_true', help='去除AI写作痕迹')

    sp.add_argument('--sheet', type=int, default=0, help='Excel sheet索引')

    # SSD 模式子选项
    sp.add_argument('--embed-images', action='store_true', help='SSD 模式:将图片转为 Base64 嵌入')

    sp.add_argument('--ocr-images', action='store_true', help='SSD 模式:OCR 识别文档内图片文字')

    sp.add_argument('--ocr-pdf', action='store_true', help='SSD 模式:对 PDF 扫描件进行 OCR(需要 Tesseract)')

    sp.add_argument('--json', dest='json_output', action='store_true',

                    help='以 JSON 格式输出结果(供程序调用)')



    # sanitize

    ep = subparsers.add_parser('sanitize', help='文档脱敏')

    ep.add_argument('text', nargs='?', help='要处理的文本')

    ep.add_argument('-i', '--input', help='输入文件')

    ep.add_argument('-o', '--output', help='输出文件路径(完整路径)')

    ep.add_argument('-d', '--out-dir', help='输出目录')

    ep.add_argument('--words', nargs='*', help='自定义敏感词')

    ep.add_argument('--items', nargs='*',

        help='指定要处理的脱敏项,可用值: 手机号,邮箱,身份证,银行卡,IP地址')

    ep.add_argument('--sheet', type=int, default=0, help='Excel sheet索引')

    ep.add_argument('--format', help='指定输出格式')

    ep.add_argument('--json', dest='json_output', action='store_true',

                    help='以 JSON 格式输出结果(供程序调用)')



    # batch-slim

    bp = subparsers.add_parser('batch-slim', help='批量文档减肥(文件夹)')

    bp.add_argument('folder', help='输入文件夹路径')

    bp.add_argument('-o', '--out-dir', help='输出目录')

    bp.add_argument('-m', '--mode', choices=['standard', 'aggressive', 'deep-clean', 'ssd'],
                    default='standard', help='处理模式:standard(标准压缩) | aggressive(激进压缩) | deep-clean(深度清理) | ssd(转换为SSD)')

    bp.add_argument('-c', '--compression', type=float, default=0.3, help='压缩率(仅 standard/aggressive 模式生效)')

    bp.add_argument('--ai', action='store_true', help='去除AI味')

    # SSD 模式子选项
    bp.add_argument('--embed-images', action='store_true', help='SSD 模式:将图片转为 Base64 嵌入')

    bp.add_argument('--ocr-images', action='store_true', help='SSD 模式:OCR 识别图片文件文字')

    bp.add_argument('--ocr-pdf', action='store_true', help='SSD 模式:对 PDF 扫描件进行 OCR(需要 Tesseract)')

    bp.add_argument('-w', '--workers', type=int, help='并行线程数(默认4)')

    bp.add_argument('--no-recursive', action='store_true', help='不递归子文件夹')



    # batch-sanitize

    bx = subparsers.add_parser('batch-sanitize', help='批量文档脱敏(文件夹)')

    bx.add_argument('folder', help='输入文件夹路径')

    bx.add_argument('-o', '--out-dir', help='输出目录')

    bx.add_argument('--words', nargs='*', help='自定义敏感词')

    bx.add_argument('--items', nargs='*', help='指定脱敏项')

    bx.add_argument('-w', '--workers', type=int, help='并行线程数(默认4)')

    bx.add_argument('--no-recursive', action='store_true', help='不递归子文件夹')


    # convert
    cv = subparsers.add_parser('convert', help='文件格式转换')

    cv.add_argument('-i', '--input', required=True, help='输入文件路径')

    cv.add_argument('-o', '--output', help='输出文件路径（完整路径）')

    cv.add_argument('-d', '--out-dir', help='输出目录')

    cv.add_argument('-f', '--format', choices=['ssd', 'txt', 'md', 'pdf', 'docx', 'xlsx', 'pptx'],
                    required=True, help='目标格式：ssd | txt | md | pdf | docx | xlsx | pptx')

    cv.add_argument('--ocr-pdf', action='store_true', help='对 PDF 扫描件进行 OCR（需要 Tesseract）')

    cv.add_argument('--embed-images', action='store_true', help='SSD 模式：将图片转为 Base64 嵌入')

    cv.add_argument('--ocr-images', action='store_true', help='SSD 模式：OCR 识别文档内图片文字')

    cv.add_argument('--json', dest='json_output', action='store_true',

                    help='以 JSON 格式输出结果（供程序调用）')


    # compress-image
    ci = subparsers.add_parser('compress-image', help='图片压缩')

    ci.add_argument('-i', '--input', required=True, help='输入图片路径')

    ci.add_argument('-o', '--output', help='输出图片路径（完整路径）')

    ci.add_argument('-q', '--quality', type=int, default=60, help='压缩质量 (1-100，默认60)')

    ci.add_argument('--max-width', type=int, help='最大宽度（像素）')

    ci.add_argument('--max-height', type=int, help='最大高度（像素）')

    ci.add_argument('--json', dest='json_output', action='store_true',

                    help='以 JSON 格式输出结果（供程序调用）')


    # batch-convert
    bc = subparsers.add_parser('batch-convert', help='批量格式转换（文件夹）')

    bc.add_argument('folder', help='输入文件夹路径')

    bc.add_argument('-o', '--out-dir', required=True, help='输出目录')

    bc.add_argument('-f', '--format', choices=['ssd', 'txt', 'md'],
                    required=True, help='目标格式：ssd | txt | md')

    bc.add_argument('--ocr-pdf', action='store_true', help='对 PDF 扫描件进行 OCR（需要 Tesseract）')

    bc.add_argument('--embed-images', action='store_true', help='SSD 模式：将图片转为 Base64 嵌入')

    bc.add_argument('--ocr-images', action='store_true', help='SSD 模式：OCR 识别文档内图片文字')

    bc.add_argument('-w', '--workers', type=int, help='并行线程数（默认4）')

    bc.add_argument('--no-recursive', action='store_true', help='不递归子文件夹')

    bc.add_argument('--json', dest='json_output', action='store_true',

                    help='以 JSON 格式输出结果（供程序调用）')


    # batch-compress-image
    bci = subparsers.add_parser('batch-compress-image', help='批量图片压缩（文件夹）')

    bci.add_argument('folder', help='输入文件夹路径')

    bci.add_argument('-o', '--out-dir', required=True, help='输出目录')

    bci.add_argument('-q', '--quality', type=int, default=60, help='压缩质量 (1-100，默认60)')

    bci.add_argument('--max-width', type=int, help='最大宽度（像素）')

    bci.add_argument('--max-height', type=int, help='最大高度（像素）')

    bci.add_argument('-w', '--workers', type=int, help='并行线程数（默认4）')

    bci.add_argument('--no-recursive', action='store_true', help='不递归子文件夹')

    bci.add_argument('--json', dest='json_output', action='store_true',

                    help='以 JSON 格式输出结果（供程序调用）')


    args = parser.parse_args()



    # 检查依赖

    if args.check:

        print(msg("dep_check"))

        deps_list = [

            ('docx', 'python-docx', 'Word .docx'),

            ('openpyxl', 'openpyxl', 'Excel .xlsx'),

            ('pptx', 'python-pptx', 'PPT .pptx'),

            ('pdfplumber', 'pdfplumber', 'PDF (表格)'),

            ('pymupdf', 'PyMuPDF', 'PDF (通用)'),

            ('xlrd', 'xlrd', 'Excel .xls'),

        ]

        for key, pkg, desc in deps_list:

            status = "[OK]" if DEPS.get(key) else "[MISSING]"

            print(f"  {status} {desc:12} ({pkg})")

        print(msg("config_output", dir=cfg.get('output_dir', 'N/A')))

        return



    if not args.command:

        parser.print_help()

        return



    # ===== 单文件格式转换 =====

    if args.command == 'convert':

        json_mode = getattr(args, 'json_output', False)

        from format_to_ssd import convert_to_ssd_v2, is_ssd_convertible

        input_file = args.input

        target_fmt = args.format

        # 确定输出路径

        if args.output:

            output_path = Path(args.output)

        elif args.out_dir:

            output_path = Path(args.out_dir) / f"{Path(input_file).stem}.{target_fmt}"

        else:

            output_path = Path(input_file).parent / f"{Path(input_file).stem}_{target_fmt}.{target_fmt}"

        # SSD 模式

        if target_fmt == 'ssd':

            try:

                ssd_text = convert_to_ssd_v2(

                    input_file,

                    optimize=True,

                    embed_images=args.embed_images,

                    ocr_images=args.ocr_images,

                    ocr_pdf=args.ocr_pdf,

                )

                # 写入输出文件

                output_path = Path(str(output_path).replace('.ssd', '.ssd') if str(output_path).endswith('.ssd') else f"{output_path}.ssd")

                output_path.write_text(ssd_text, encoding='utf-8')

                if not json_mode:

                    print(msg("batch_convert_ok", file=input_file, out=output_path, chars=len(ssd_text)))

                result_json = {

                    'success': True,

                    'action': 'convert',

                    'output_path': str(output_path),

                    'format': 'ssd',

                    'chars': len(ssd_text),

                }

            except ValueError as e:

                error_msg = str(e)

                if json_mode:

                    result_json = {'success': False, 'error': error_msg}

                    print(json.dumps(result_json, ensure_ascii=False))

                else:

                    safe_stderr(msg("err_convert", msg=error_msg))

                sys.exit(1)

            except Exception as e:

                error_msg = f"SSD 转换失败: {e}"

                if json_mode:

                    result_json = {'success': False, 'error': error_msg}

                    print(json.dumps(result_json, ensure_ascii=False))

                else:

                    safe_stderr(msg("err_convert", msg=error_msg))

                sys.exit(1)

        # TXT/MD 模式（纯文本提取）

        elif target_fmt in ('txt', 'md'):

            try:

                text = read_file(input_file, {})

                output_path = Path(str(output_path).replace('.ssd', f'.{target_fmt}'))

                output_path.write_text(text, encoding='utf-8')

                if not json_mode:

                    print(msg("batch_convert_ok", file=input_file, out=output_path, chars=len(text)))

                result_json = {

                    'success': True,

                    'action': 'convert',

                    'output_path': str(output_path),

                    'format': target_fmt,

                    'chars': len(text),

                }

            except Exception as e:

                if json_mode:

                    result_json = {'success': False, 'error': str(e)}

                    print(json.dumps(result_json, ensure_ascii=False))

                else:

                    safe_stderr(f"[错误] 转换失败: {e}")

                sys.exit(1)

        # 其他格式（pdf/docx/xlsx/pptx）- 需要额外依赖

        else:

            safe_stderr(msg("err_target_fmt", fmt=target_fmt))

            sys.exit(1)

        # JSON 输出

        if json_mode:

            print(json.dumps(result_json, ensure_ascii=False))

        return


    # ===== 单张图片压缩 =====

    if args.command == 'compress-image':

        json_mode = getattr(args, 'json_output', False)

        input_file = args.input

        quality = args.quality

        max_size = None

        if args.max_width or args.max_height:

            max_size = (args.max_width or 999999, args.max_height or 999999)

        # 确定输出路径

        if args.output:

            output_path = args.output

        else:

            stem = Path(input_file).stem

            suffix = Path(input_file).suffix

            output_path = str(Path(input_file).parent / f"{stem}_减肥{suffix}")

        result = compress_image(input_file, output_path, quality=quality, max_size=max_size)

        if json_mode:

            print(json.dumps(result, ensure_ascii=False))
        else:

            if result.get('success'):

                print(msg("image_compress", file=input_file, out=result['output_path'], saved=""))

                print(f"        {format_size(result['original_size'])} -> {format_size(result['new_size'])}")

                print(f"        {format_size(result['saved'])} ({result['saved_percent']}%)")

            else:

                safe_stderr(msg("err_compress", msg=result.get('error', msg('err_unknown'))))

                sys.exit(1)

        return


    # ===== 批量格式转换 =====

    if args.command == 'batch-convert':

        json_mode = getattr(args, 'json_output', False)

        import shutil

        from format_to_ssd import convert_to_ssd_v2

        IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff', '.tif'}

        SUPPORTED_EXT = {'.txt', '.md', '.json', '.csv', '.xml', '.html', '.log',
                         '.docx', '.xlsx', '.xls', '.pptx', '.pdf'}

        src_folder = Path(args.folder)

        if not src_folder.is_dir():

            safe_stderr(msg("err_input_not_dir", path=src_folder))

            sys.exit(1)

        out_dir = Path(args.out_dir)

        out_dir.mkdir(parents=True, exist_ok=True)

        # 收集文件

        files_to_convert = []

        if args.no_recursive:

            for f in src_folder.iterdir():

                if f.is_file() and f.suffix.lower() in SUPPORTED_EXT:

                    files_to_convert.append(f)

        else:

            for f in src_folder.rglob('*'):

                if f.is_file() and f.suffix.lower() in SUPPORTED_EXT:

                    files_to_convert.append(f)

        if not files_to_convert:

            print(msg("err_no_files", exts=', '.join(SUPPORTED_EXT)))

            if json_mode:

                print(json.dumps({'success': True, 'total': 0, 'converted': 0, 'errors': 0, 'files': []}, ensure_ascii=False))

            return

        print(msg("batch_convert", folder=src_folder))

        print(msg("batch_format", fmt=args.format))

        print(msg("batch_output", dir=out_dir))

        results = []

        success_count = 0

        error_count = 0

        for file_path in files_to_convert:

            rel_path = file_path.relative_to(src_folder)

            target_name = f"{file_path.stem}.{args.format}"

            target_path = out_dir / rel_path.parent / target_name

            target_path.parent.mkdir(parents=True, exist_ok=True)

            try:

                if args.format == 'ssd':

                    ssd_text = convert_to_ssd_v2(

                        str(file_path),

                        optimize=True,

                        embed_images=args.embed_images,

                        ocr_images=args.ocr_images,

                        ocr_pdf=args.ocr_pdf,

                    )

                    target_path.write_text(ssd_text, encoding='utf-8')

                    success_count += 1

                    results.append({

                        'source': str(file_path),

                        'output': str(target_path),

                        'status': 'success',

                        'chars': len(ssd_text),

                    })

                    if not json_mode:

                        print(msg("batch_convert_ok", file=rel_path, out=target_path.name, chars=len(ssd_text)))

                else:

                    text = read_file(str(file_path), {})

                    target_path.write_text(text, encoding='utf-8')

                    success_count += 1

                    results.append({

                        'source': str(file_path),

                        'output': str(target_path),

                        'status': 'success',

                        'chars': len(text),

                    })

                    if not json_mode:

                        print(msg("batch_convert_ok", file=rel_path, out=target_path.name, chars=len(text)))

            except Exception as e:

                error_count += 1

                results.append({

                    'source': str(file_path),

                    'output': '',

                    'status': 'error',

                    'error': str(e),

                })

                if not json_mode:

                    print(f"  [ERROR] {rel_path}: {e}")

        if not json_mode:

            print(f"\n{'='*50}")

            print(msg("batch_convert_done", ok=success_count, fail=error_count, total=len(files_to_convert)))

            print(msg("batch_output", dir=out_dir))

            print(f"{'='*50}")

        if json_mode:

            print(json.dumps({

                'success': True,

                'action': 'batch-convert',

                'total': len(files_to_convert),

                'converted': success_count,

                'errors': error_count,

                'output_dir': str(out_dir),

                'files': results,

            }, ensure_ascii=False))

        return


    # ===== 批量图片压缩 =====

    if args.command == 'batch-compress-image':

        json_mode = getattr(args, 'json_output', False)

        from concurrent.futures import ThreadPoolExecutor, as_completed

        IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.tiff', '.tif'}

        src_folder = Path(args.folder)

        if not src_folder.is_dir():

            safe_stderr(f"[错误] 输入路径不是目录: {src_folder}")

            sys.exit(1)

        out_dir = Path(args.out_dir)

        out_dir.mkdir(parents=True, exist_ok=True)

        # 收集图片文件

        image_files = []

        if args.no_recursive:

            for f in src_folder.iterdir():

                if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS:

                    image_files.append(f)

        else:

            for f in src_folder.rglob('*'):

                if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS:

                    image_files.append(f)

        if not image_files:

            print(msg("err_no_images", exts=', '.join(IMAGE_EXTENSIONS)))

            if json_mode:

                print(json.dumps({'success': True, 'total': 0, 'compressed': 0, 'errors': 0, 'files': []}, ensure_ascii=False))

            return

        workers = args.workers or 4

        max_size = None

        if args.max_width or args.max_height:

            max_size = (args.max_width or 999999, args.max_height or 999999)

        print(msg("batch_compress", folder=src_folder))

        print(msg("batch_quality", q=args.quality, w=workers))

        print(msg("batch_output", dir=out_dir))

        results = []

        def _compress_one(file_path):

            rel_path = file_path.relative_to(src_folder)

            target_path = out_dir / rel_path.parent / f"{file_path.stem}_减肥{file_path.suffix}"

            target_path.parent.mkdir(parents=True, exist_ok=True)

            try:

                result = compress_image(str(file_path), str(target_path),

                                        quality=args.quality, max_size=max_size)

                if result.get('success'):

                    return {

                        'source': str(file_path),

                        'output': str(target_path),

                        'status': 'success',

                        'original_size': result['original_size'],

                        'new_size': result['new_size'],

                        'saved_percent': result['saved_percent'],

                    }

                else:

                    return {

                        'source': str(file_path),

                        'output': '',

                        'status': 'error',

                        'error': result.get('error', '未知错误'),

                    }

            except Exception as e:

                return {

                    'source': str(file_path),

                    'output': '',

                    'status': 'error',

                    'error': str(e),

                }

        with ThreadPoolExecutor(max_workers=workers) as executor:

            futures = {executor.submit(_compress_one, f): f for f in image_files}

            for future in as_completed(futures):

                result = future.result()

                results.append(result)

                if not json_mode:

                    if result['status'] == 'success':

                        print(f"  [OK] {Path(result['source']).relative_to(src_folder)} -> "

                              f"{Path(result['output']).name} "

                              f"({format_size(result['original_size'])} -> {format_size(result['new_size'])}, "

                              f"节省 {result['saved_percent']}%)")

                    else:

                        print(f"  [ERROR] {Path(result['source']).relative_to(src_folder)}: {result['error']}")

        success_count = sum(1 for r in results if r['status'] == 'success')

        error_count = sum(1 for r in results if r['status'] == 'error')

        if not json_mode:

            print(f"\n{'='*50}")

            print(msg("batch_compress_done", ok=success_count, fail=error_count, total=len(image_files)))

            print(msg("batch_output", dir=out_dir))

            print(f"{'='*50}")

        if json_mode:

            print(json.dumps({

                'success': True,

                'action': 'batch-compress-image',

                'total': len(image_files),

                'compressed': success_count,

                'errors': error_count,

                'output_dir': str(out_dir),

                'files': results,

            }, ensure_ascii=False))

        return


    # 批量处理

    if args.command in ('batch-slim', 'batch-sanitize'):

        import shutil

        from batch_processor import batch_process



        if args.out_dir:

            out_dir = args.out_dir

        else:

            src_parent = str(Path(args.folder).resolve().parent)

            ts = datetime.now().strftime('%Y%m%d_%H%M%S')

            out_dir = os.path.join(src_parent, f"{Path(args.folder).name}_处理结果_{ts}")



        options = {}

        if args.command == 'batch-slim':

            options['compression'] = args.compression

            options['remove_ai'] = args.ai

            # 模式映射
            mode_map = {
                'standard': {'compression': 0.3, 'deep_clean': False, 'convert_to_ssd': False},
                'aggressive': {'compression': 0.7, 'deep_clean': False, 'convert_to_ssd': False},
                'deep-clean': {'compression': 0.3, 'deep_clean': True, 'convert_to_ssd': False},
                'ssd': {'compression': 0.3, 'deep_clean': False, 'convert_to_ssd': True},
            }
            mode_opts = mode_map.get(args.mode, mode_map['standard'])
            options['compression'] = mode_opts['compression']
            options['deep_clean'] = mode_opts['deep_clean']
            options['convert_to_ssd'] = mode_opts['convert_to_ssd']

            # SSD 子选项
            options['embed_images'] = args.embed_images
            options['ocr_images'] = args.ocr_images
            options['ocr_images_files'] = args.ocr_images
            options['ocr_pdf'] = args.ocr_pdf

            # 根据模式调整 output_ext
            if args.mode == 'ssd':
                options['output_ext'] = '.ssd'
            elif args.mode == 'deep-clean':
                options['output_ext'] = '.txt'
            else:
                pass  # standard/aggressive: keep original format

            action = 'slim'

        else:

            options['custom_words'] = args.words or []

            options['sanitize_items'] = args.items or None

            options['output_ext'] = '.ssd'

            action = 'sanitize'



        print(msg("batch_action", action=action, folder=args.folder))

        print(msg("batch_output", dir=out_dir))



        result = batch_process(

            folder_path=args.folder,

            action=action,

            options=options,

            recursive=not args.no_recursive,

            workers=args.workers or 4,

            out_base=out_dir

        )



        if 'error' in result and result.get('total', 0) == 0:

            print(msg("batch_error", msg=result['error']))

            return



        s = result['summary']

        print(f"\n{'='*50}")

        print(msg("batch_done", sec=s['elapsed_seconds']))

        print(msg("batch_stats", ok=s['success'], fail=s['error'], skip=s['skip']))

        if s['total_input_size'] > 0:

            rate = s['size_reduced'] / s['total_input_size'] * 100

            print(msg("batch_size", orig=format_size(s['total_input_size']), new=format_size(s['total_output_size'])))

            print(msg("batch_saved", saved=format_size(s['size_reduced']), rate=rate))

        print(msg("batch_output", dir=result['output_dir']))

        print(msg("batch_report", dir=result['output_dir']))

        print(f"{'='*50}\n{result['report']}")

        return



    # 获取输入文本

    text = None

    input_file = None

    if args.input:

        input_file = args.input

        opts = {'sheet': args.sheet}

        try:

            text = read_file(args.input, opts)

            if text is None:
                print(msg("code_skip", file=args.input))
                sys.exit(0)

            print(msg("reading", file=args.input, chars=len(text)))

        except ImportError as e:

            safe_stderr(f"[错误] {e}")

            sys.exit(1)

        except Exception as e:

            safe_stderr(msg("err_read", msg=e))

            sys.exit(1)

    elif args.text:

        text = args.text

    else:

        safe_stderr(msg("err_no_input"))

        sys.exit(1)



    # 处理

    json_mode = getattr(args, 'json_output', False)

    stats = {}

    # 检测是否为结构化格式
    _input_ext = Path(input_file).suffix.lower() if input_file else None
    _is_structured = _input_ext in STRUCTURED_EXTENSIONS if _input_ext else False



    if args.command == 'slim':

        # 结构化格式（JSON/XML/YAML/CSV/HTML）slim 模式跳过
        if _is_structured:
            print(msg("struct_skip", file=input_file))
            sys.exit(0)

        # 根据模式选择处理路径
        if args.mode == 'ssd':
            # SSD 模式:调用 convert_to_ssd_v2
            from format_to_ssd import convert_to_ssd_v2

            ssd_input = args.input or input_file
            if not ssd_input:
                import tempfile
                tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
                tmp.write(args.text)
                tmp.close()
                ssd_input = tmp.name

            ssd_result = convert_to_ssd_v2(
                ssd_input,
                optimize=True,
                embed_images=args.embed_images,
                ocr_images=args.ocr_images,
                ocr_pdf=args.ocr_pdf,
            )

            # convert_to_ssd_v2 returns a string (SSD text)
            result = {'result': ssd_result, 'stats': {}}
            stats = {}
            if not json_mode:
                print(msg("ssd_done", chars=len(ssd_result)))

        elif args.mode == 'deep-clean':
            # 深度清理:高压缩率 + 去除 AI 痕迹
            processor = DocSlimmer()
            result = processor.slim(text, 0.7, True)
            stats = result['stats']
            if not json_mode:
                print(msg("deep_clean", rate=stats.get('compression_rate', 0)))
                print(msg("deep_clean_chars", chars=stats.get('reduced_chars', 0)))

        elif args.mode == 'aggressive':
            # 激进压缩:高压缩率
            processor = DocSlimmer()
            result = processor.slim(text, 0.7, args.ai)
            stats = result['stats']
            if not json_mode:
                print(msg("aggressive", rate=stats.get('compression_rate', 0)))
                print(msg("aggressive_chars", chars=stats.get('reduced_chars', 0)))

        else:
            # standard 模式(默认)
            processor = DocSlimmer()
            result = processor.slim(text, args.compression, args.ai)
            stats = result['stats']
            if not json_mode:
                print(msg("standard", rate=stats.get('compression_rate', 0)))
                print(msg("standard_chars", chars=stats.get('reduced_chars', 0)))



    elif args.command == 'sanitize':

        sanitize_items = getattr(args, 'items', None)

        if _is_structured and _input_ext:
            # 结构化格式：使用 StructSanitizer
            from struct_sanitizer import sanitize_structured
            result_text, stats = sanitize_structured(text, _input_ext, sanitize_items)
            result = {'result': result_text, 'stats': stats}
        else:
            # 普通文本：使用 DocSanitizer
            processor = DocSanitizer()
            result = processor.sanitize(text, args.words, sanitize_items)
            stats = result['stats']

        if not json_mode:

            total = sum(v for k, v in stats.items() if v > 0)

            detail = ', '.join(f"{k}:{v}" for k, v in stats.items() if v > 0)

            print(msg("sanitize_done", total=total, detail=detail) if total > 0 else msg("sanitize_none"))



    # 输出(核心:永远不覆盖源文件)

    # 根据 slim 模式确定输出格式
    slim_fmt = None
    if args.command == 'slim' and args.mode == 'ssd':
        slim_fmt = 'ssd'
    elif args.command == 'slim' and args.mode == 'deep-clean':
        slim_fmt = 'txt'

    output_path = resolve_output_path(

        input_path=input_file or '.',

        action=args.command,

        user_output=args.output,

        out_dir=args.out_dir,

        fmt=slim_fmt or (args.format if hasattr(args, 'format') else None)

    )



    # 如果输出目录无法创建

    if output_path is None:

        if json_mode:

            print(json.dumps({"success": True, "output_path": None, "stats": stats,

                              "result": result['result'][:10000]}, ensure_ascii=False))

        else:

            print('\n' + '='*50)

            print(result['result'][:3000])

            if len(result['result']) > 3000:

                print(msg("truncated", chars=len(result['result'])))

        return



    # 写入文件

    write_ok = True

    write_error = None

    actual_output = str(output_path)

    try:

        fmt = slim_fmt or (args.format if (hasattr(args, 'format') and args.format) else output_path.suffix.lstrip('.') or 'txt')

        write_file(str(output_path), result['result'], fmt)

        if not json_mode:

            print(msg("saved", path=output_path))

    except ImportError as e:

        write_error = str(e)

        txt_path = str(output_path) + '.txt'

        write_txt(txt_path, result['result'])

        actual_output = txt_path

        if not json_mode:

            print(msg("saved_fallback", path=txt_path))

    except Exception as e:

        write_ok = False

        write_error = str(e)

        actual_output = None

        if not json_mode:

            safe_stderr(msg("err_save", msg=e))

            print(msg("perm_tip"))

            print('\n' + '='*50)

            print(result['result'][:3000])



    # JSON 输出

    if json_mode:

        json_out = {

            "success": write_ok,

            "action": args.command,

            "output_path": actual_output,

            "stats": stats,

        }

        if input_file:

            json_out["input_file"] = input_file

        print(json.dumps(json_out, ensure_ascii=False))





# ========== 图片压缩 ==========



def compress_image(input_path, output_path=None, quality=85, max_size=None):

    """

    压缩图片文件



    Args:

        input_path: 输入图片路径

        output_path: 输出图片路径,None 则覆盖原文件

        quality: JPEG 质量 (1-100)

        max_size: 最大尺寸 (width, height),None 则保持原尺寸



    Returns:

        dict: {'success': bool, 'original_size': int, 'new_size': int, 'output_path': str}

    """

    from PIL import Image

    import os



    try:

        # 获取原文件大小

        original_size = os.path.getsize(input_path)



        # 打开图片

        img = Image.open(input_path)



        # 转换 RGBA/RGB

        if img.mode in ('RGBA', 'P'):

            # 保持 RGBA 用于 PNG

            pass

        elif img.mode != 'RGB':

            img = img.convert('RGB')



        # 调整尺寸

        if max_size:

            img.thumbnail(max_size, Image.Resampling.LANCZOS)



        # 确定输出路径

        if output_path is None:

            output_path = input_path



        # 确定格式

        input_ext = os.path.splitext(input_path)[1].lower()



        if input_ext in ['.jpg', '.jpeg']:

            img.save(output_path, 'JPEG', quality=quality, optimize=True)

        elif input_ext == '.png':

            # PNG 使用不同的压缩方式

            img.save(output_path, 'PNG', optimize=True)

        elif input_ext == '.gif':

            img.save(output_path, 'GIF', optimize=True)

        else:

            img.save(output_path, quality=quality, optimize=True)



        # 获取新文件大小

        new_size = os.path.getsize(output_path)



        return {

            'success': True,

            'original_size': original_size,

            'new_size': new_size,

            'output_path': output_path,

            'saved': original_size - new_size,

            'saved_percent': round((1 - new_size/original_size) * 100, 1) if original_size > 0 else 0

        }



    except Exception as e:

        return {

            'success': False,

            'error': str(e)

        }





def format_size(size: int) -> str:
    """格式化文件大小"""
    if size < 1024:
        return f"{size}B"
    elif size < 1024 * 1024:
        return f"{size/1024:.1f}KB"
    else:
        return f"{size/1024/1024:.1f}MB"


def get_image_info(path):

    """获取图片信息"""

    from PIL import Image

    import os



    try:

        img = Image.open(path)

        return {

            'width': img.width,

            'height': img.height,

            'mode': img.mode,

            'format': img.format,

            'size': os.path.getsize(path),

            'size_str': format_size(os.path.getsize(path))

        }

    except Exception as e:

        return {'error': str(e)}






# Cython 编译需要:内联 format_size 避免跨模块导入问题
def format_size(size: int) -> str:
    """格式化文件大小"""
    if size < 1024:
        return f"{size}B"
    elif size < 1024 * 1024:
        return f"{size/1024:.1f}KB"
    else:
        return f"{size/1024/1024:.1f}MB"

if __name__ == "__main__":

    main()


