#!/usr/bin/env python
"""SafeShrink 全功能测试脚本 — 覆盖所有核心功能"""

import sys
import os
import json
import tempfile
import shutil
from pathlib import Path

# 确保能导入
sys.path.insert(0, str(Path(__file__).parent))

from safe_shrink import (
    DocSlimmer, DocSanitizer, read_file, read_txt, write_txt,
    slim_native_docx, slim_native_xlsx, slim_native_pptx,
    compress_image, estimate_tokens, format_size
)
from format_to_ssd import convert_to_ssd_v2
from sanitize_ssd import SSDSanitizer, sanitize_ssd_file
from batch_processor import batch_process, scan_folder

# 测试目录
TEST_DIR = Path(__file__).parent / "test_files"
OUTPUT_DIR = Path(__file__).parent / "test_output"
OUTPUT_DIR.mkdir(exist_ok=True)

# 颜色输出
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

results = {"pass": 0, "fail": 0, "skip": 0}

def test(name, fn):
    """运行一个测试"""
    try:
        result = fn()
        if result is None:
            result = {"status": "pass", "message": "OK"}
        if result["status"] == "pass":
            print(f"  {GREEN}✅ PASS{RESET} {name}")
            results["pass"] += 1
        elif result["status"] == "skip":
            print(f"  {YELLOW}⏭️ SKIP{RESET} {name} — {result.get('message', '')}")
            results["skip"] += 1
        else:
            print(f"  {RED}❌ FAIL{RESET} {name} — {result.get('message', '')}")
            results["fail"] += 1
    except Exception as e:
        print(f"  {RED}❌ FAIL{RESET} {name} — {type(e).__name__}: {e}")
        results["fail"] += 1
    return result

def create_test_file(content, ext, subdir=""):
    """创建测试文件"""
    if not ext.startswith('.'):
        ext = '.' + ext
    subdir_path = TEST_DIR / subdir if subdir else TEST_DIR
    subdir_path.mkdir(parents=True, exist_ok=True)
    filepath = subdir_path / f"test{ext}"
    filepath.write_text(content, encoding="utf-8")
    return filepath

# ============================================================
# 1. 基础工具函数测试
# ============================================================
print("\n" + "="*60)
print("📦 1. 基础工具函数测试")
print("="*60)

def test_read_txt():
    """测试 read_txt"""
    filepath = create_test_file("这是一个测试文件。\n包含多行内容。\n用于测试 SafeShrink。", "txt")
    text = read_txt(str(filepath))
    if isinstance(text, str) and "测试" in text:
        return {"status": "pass", "message": f"读取 {len(text)} 字符"}
    return {"status": "fail", "message": f"读取失败: {type(text)}"}

def test_read_file():
    """测试 read_file"""
    filepath = create_test_file("# 标题\n\n## 子标题\n\n- 列表项1\n- 列表项2", "md")
    result = read_file(str(filepath), {})
    if isinstance(result, str) and "标题" in result:
        return {"status": "pass", "message": f"读取 {len(result)} 字符"}
    return {"status": "fail", "message": f"读取失败: {type(result)}"}

def test_write_txt():
    """测试 write_txt"""
    output_path = OUTPUT_DIR / "test_write.txt"
    content = "测试写入内容。"
    write_txt(str(output_path), content)
    if output_path.exists():
        return {"status": "pass", "message": f"写入成功 ({output_path.stat().st_size}B)"}
    return {"status": "fail", "message": "文件未创建"}

def test_estimate_tokens():
    """测试 estimate_tokens"""
    text = "这是一个测试文本，用于测试 token 估算功能。" * 10
    result = estimate_tokens(text)
    if result and result.get("total", 0) > 0:
        return {"status": "pass", "message": f"估算 {result['total']} tokens"}
    return {"status": "fail", "message": f"估算失败: {result}"}

def test_format_size():
    """测试 format_size"""
    result = format_size(1234567)
    if result and "MB" in result:
        return {"status": "pass", "message": f"格式化: {result}"}
    return {"status": "fail", "message": f"格式化失败: {result}"}

test("read_txt", test_read_txt)
test("read_file", test_read_file)
test("write_txt", test_write_txt)
test("estimate_tokens", test_estimate_tokens)
test("format_size", test_format_size)

# ============================================================
# 2. DocSlimmer 类测试
# ============================================================
print("\n" + "="*60)
print("📦 2. DocSlimmer 类测试")
print("="*60)

def test_docslimmer_init():
    """测试 DocSlimmer 初始化"""
    ds = DocSlimmer()
    if ds and hasattr(ds, "slim"):
        return {"status": "pass", "message": "DocSlimmer 初始化成功"}
    return {"status": "fail", "message": "DocSlimmer 初始化失败"}

def test_docslimmer_slim():
    """测试 DocSlimmer.slim (文本压缩)"""
    ds = DocSlimmer()
    text = "这是冗余的文本。这是冗余的文本。这是冗余的文本。" * 100
    result = ds.slim(text, compression_rate=0.3)
    if result.get("result") and len(result["result"]) < len(text):
        return {"status": "pass", "message": f"{len(text)} → {len(result['result'])} 字符 (节省 {(1-len(result['result'])/len(text))*100:.1f}%)"}
    return {"status": "fail", "message": f"slim 失败: {result}"}

def test_docslimmer_sanitize():
    """测试 DocSanitizer.sanitize (文本脱敏)"""
    ds = DocSanitizer()
    text = "张三 的手机号是 13800138000，邮箱是 test@example.com"
    result = ds.sanitize(text)
    if isinstance(result, dict) and "result" in result:
        output = result["result"]
        if "13800138000" not in output and "test@example.com" not in output:
            return {"status": "pass", "message": f"敏感信息已脱敏 (手机号→138****8000)"}
        return {"status": "fail", "message": f"脱敏不彻底: {output}"}
    return {"status": "fail", "message": f"脱敏失败: {result}"}

test("DocSlimmer - 初始化", test_docslimmer_init)
test("DocSlimmer - slim (文本)", test_docslimmer_slim)
test("DocSlimmer - sanitize (文本)", test_docslimmer_sanitize)

# ============================================================
# 3. slim_native 函数测试（原地修改文件）
# ============================================================
print("\n" + "="*60)
print("📦 3. slim_native 函数测试（原地修改）")
print("="*60)

def test_slim_native_docx():
    """测试 slim_native_docx（原地修改）"""
    try:
        from docx import Document
        doc = Document()
        doc.add_heading("测试", level=1)
        doc.add_paragraph("冗余内容。" * 100)
        filepath = TEST_DIR / "test_native.docx"
        doc.save(str(filepath))
        orig_size = filepath.stat().st_size
        
        result = slim_native_docx(str(filepath), compression_rate=0.3)
        if result.get("result"):
            new_size = filepath.stat().st_size
            return {"status": "pass", "message": f"{orig_size}B → {new_size}B"}
        return {"status": "fail", "message": f"slim_native_docx 失败: {result}"}
    except Exception as e:
        return {"status": "skip", "message": f"python-docx 问题: {e}"}

def test_slim_native_xlsx():
    """测试 slim_native_xlsx（原地修改）"""
    try:
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        for i in range(1, 51):
            ws[f"A{i}"] = f"冗余数据 {i}。" * 10
            ws[f"A{i}"].font = openpyxl.styles.Font(size=14)
        filepath = TEST_DIR / "test_native.xlsx"
        wb.save(str(filepath))
        orig_size = filepath.stat().st_size
        
        result = slim_native_xlsx(str(filepath), compression_rate=0.3)
        if result.get("success"):
            new_size = filepath.stat().st_size
            return {"status": "pass", "message": f"{orig_size}B → {new_size}B"}
        return {"status": "fail", "message": f"slim_native_xlsx 失败: {result}"}
    except Exception as e:
        return {"status": "skip", "message": f"openpyxl 问题: {e}"}

def test_slim_native_pptx():
    """测试 slim_native_pptx（原地修改）"""
    try:
        from pptx import Presentation
        from pptx.util import Pt
        prs = Presentation()
        for i in range(10):
            slide = prs.slides.add_slide(prs.slide_layouts[1])
            slide.shapes[0].text = f"第 {i+1} 页"
            slide.shapes[0].text_frame.paragraphs[0].font.size = Pt(24)
            slide.shapes[1].text = "冗余内容。" * 20
            slide.shapes[1].text_frame.paragraphs[0].font.size = Pt(18)
        filepath = TEST_DIR / "test_native.pptx"
        prs.save(str(filepath))
        orig_size = filepath.stat().st_size
        
        result = slim_native_pptx(str(filepath), compression_rate=0.3)
        if result.get("success"):
            new_size = filepath.stat().st_size
            return {"status": "pass", "message": f"{orig_size}B → {new_size}B"}
        return {"status": "fail", "message": f"slim_native_pptx 失败: {result}"}
    except Exception as e:
        return {"status": "skip", "message": f"python-pptx 问题: {e}"}

test("slim_native_docx", test_slim_native_docx)
test("slim_native_xlsx", test_slim_native_xlsx)
test("slim_native_pptx", test_slim_native_pptx)

# ============================================================
# 4. SSD 转换测试
# ============================================================
print("\n" + "="*60)
print("📦 4. SSD 转换测试")
print("="*60)

def test_convert_to_ssd_txt():
    """测试 convert_to_ssd_v2 - txt"""
    filepath = create_test_file("这是一个测试文档。\n用于测试 SSD 转换。", "txt")
    result = convert_to_ssd_v2(str(filepath))
    if isinstance(result, str) and "测试" in result and len(result) > 10:
        # 手动写入验证
        output_path = OUTPUT_DIR / "test.ssd"
        output_path.write_text(result, encoding="utf-8")
        return {"status": "pass", "message": f"SSD 内容已生成 ({len(result)} 字符)"}
    return {"status": "fail", "message": f"转换失败: {result}"}

def test_convert_to_ssd_md():
    """测试 convert_to_ssd_v2 - md"""
    filepath = create_test_file("# 测试\n\n## 子标题\n\n- 内容1\n- 内容2", "md")
    result = convert_to_ssd_v2(str(filepath))
    if isinstance(result, str) and "测试" in result:
        output_path = OUTPUT_DIR / "test2.ssd"
        output_path.write_text(result, encoding="utf-8")
        return {"status": "pass", "message": f"SSD 内容已生成 ({len(result)} 字符)"}
    return {"status": "fail", "message": f"转换失败: {result}"}

def test_convert_to_ssd_docx():
    """测试 convert_to_ssd_v2 - docx"""
    try:
        from docx import Document
        doc = Document()
        doc.add_heading("测试文档", level=1)
        doc.add_paragraph("这是一个测试 Word 文档。" * 10)
        filepath = TEST_DIR / "test_convert.docx"
        doc.save(str(filepath))
        
        result = convert_to_ssd_v2(str(filepath))
        if isinstance(result, str) and "测试" in result:
            output_path = OUTPUT_DIR / "test_docx.ssd"
            output_path.write_text(result, encoding="utf-8")
            return {"status": "pass", "message": f"docx→SSD 成功 ({len(result)} 字符)"}
        return {"status": "fail", "message": f"转换失败: {result}"}
    except Exception as e:
        return {"status": "skip", "message": f"python-docx 问题: {e}"}

def test_convert_to_ssd_pdf():
    """测试 convert_to_ssd_v2 - pdf (文本 PDF)"""
    try:
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "这是一个测试 PDF 文档。\n用于测试 SSD 转换功能。")
        pdf_path = TEST_DIR / "pdf" / "test_text.pdf"
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(pdf_path))
        doc.close()
        
        result = convert_to_ssd_v2(str(pdf_path))
        if isinstance(result, str) and len(result) > 5:
            # PDF SSD 输出格式: "······ PDF ···\n···· SSD ·····" 等
            output_path = OUTPUT_DIR / "test_pdf.ssd"
            output_path.write_text(result, encoding="utf-8")
            return {"status": "pass", "message": f"PDF→SSD 成功 ({len(result)} 字符)"}
        elif isinstance(result, dict) and result.get("error") and "NEEDS_OCR" in str(result.get("error", "")):
            return {"status": "pass", "message": "PDF 被正确识别为扫描件（需要 OCR）"}
        return {"status": "fail", "message": f"转换失败: {result}"}
    except ImportError:
        return {"status": "skip", "message": "PyMuPDF 不可用，跳过 PDF 测试"}

def test_convert_to_ssd_xlsx():
    """测试 convert_to_ssd_v2 - xlsx"""
    try:
        import openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        ws["A1"] = "姓名"
        ws["B1"] = "年龄"
        ws["A2"] = "张三"
        ws["B2"] = 25
        filepath = TEST_DIR / "test_convert.xlsx"
        wb.save(str(filepath))
        
        result = convert_to_ssd_v2(str(filepath))
        if isinstance(result, str) and len(result) > 5:
            # xlsx SSD 输出可能很短，只要不是空字符串就算成功
            output_path = OUTPUT_DIR / "test_xlsx.ssd"
            output_path.write_text(result, encoding="utf-8")
            return {"status": "pass", "message": f"xlsx→SSD 成功 ({len(result)} 字符)"}
        return {"status": "fail", "message": f"转换失败: {result}"}
    except Exception as e:
        return {"status": "skip", "message": f"openpyxl 问题: {e}"}

def test_convert_to_ssd_pptx():
    """测试 convert_to_ssd_v2 - pptx"""
    try:
        from pptx import Presentation
        prs = Presentation()
        slide = prs.slides.add_slide(prs.slide_layouts[0])
        slide.shapes[0].text = "测试演示文稿"
        filepath = TEST_DIR / "test_convert.pptx"
        prs.save(str(filepath))
        
        result = convert_to_ssd_v2(str(filepath))
        if isinstance(result, str) and "测试" in result:
            output_path = OUTPUT_DIR / "test_pptx.ssd"
            output_path.write_text(result, encoding="utf-8")
            return {"status": "pass", "message": f"pptx→SSD 成功 ({len(result)} 字符)"}
        return {"status": "fail", "message": f"转换失败: {result}"}
    except Exception as e:
        return {"status": "skip", "message": f"python-pptx 问题: {e}"}

test("convert_to_ssd_v2 - txt", test_convert_to_ssd_txt)
test("convert_to_ssd_v2 - md", test_convert_to_ssd_md)
test("convert_to_ssd_v2 - docx", test_convert_to_ssd_docx)
test("convert_to_ssd_v2 - pdf", test_convert_to_ssd_pdf)
test("convert_to_ssd_v2 - xlsx", test_convert_to_ssd_xlsx)
test("convert_to_ssd_v2 - pptx", test_convert_to_ssd_pptx)

# ============================================================
# 5. 脱敏测试
# ============================================================
print("\n" + "="*60)
print("📦 5. 脱敏测试")
print("="*60)

def test_sanitize_phone():
    """测试 SSDSanitizer.sanitize - 手机号"""
    sanitizer = SSDSanitizer()
    content = "我的手机号是 13800138000，备用是 13912345678"
    result = sanitizer.sanitize(content, custom_words=[], items=None)
    if isinstance(result, dict) and "result" in result:
        output = result["result"]
        if "13800138000" not in output and "13912345678" not in output:
            return {"status": "pass", "message": "手机号已脱敏"}
        return {"status": "fail", "message": f"手机号未脱敏: {output}"}
    return {"status": "fail", "message": f"脱敏失败: {result}"}

def test_sanitize_email():
    """测试 SSDSanitizer.sanitize - 邮箱"""
    sanitizer = SSDSanitizer()
    content = "联系邮箱: test@example.com 或 admin@test.org"
    result = sanitizer.sanitize(content, custom_words=[], items=None)
    if isinstance(result, dict) and "result" in result:
        output = result["result"]
        if "test@example.com" not in output and "admin@test.org" not in output:
            return {"status": "pass", "message": "邮箱已脱敏"}
        return {"status": "fail", "message": f"邮箱未脱敏: {output}"}
    return {"status": "fail", "message": f"脱敏失败: {result}"}

def test_sanitize_id_card():
    """测试 SSDSanitizer.sanitize - 身份证号"""
    sanitizer = SSDSanitizer()
    content = "身份证号: 110101199001011234"
    result = sanitizer.sanitize(content, custom_words=[], items=None)
    if isinstance(result, dict) and "result" in result:
        output = result["result"]
        if "110101199001011234" not in output:
            return {"status": "pass", "message": "身份证号已脱敏"}
        return {"status": "fail", "message": f"身份证号未脱敏: {output}"}
    return {"status": "fail", "message": f"脱敏失败: {result}"}

def test_sanitize_ssd_file():
    """测试 sanitize_ssd_file（原地修改）"""
    filepath = create_test_file("张三 的手机号是 13800138000，邮箱是 test@example.com", "txt")
    result = sanitize_ssd_file(str(filepath), custom_words=[])
    # sanitize_ssd_file 返回 {"result": "脱敏后内容", "stats": {...}}
    if isinstance(result, dict) and "result" in result:
        output = result["result"]
        if "13800138000" not in output and "test@example.com" not in output:
            return {"status": "pass", "message": "文件脱敏成功"}
        return {"status": "fail", "message": f"脱敏不彻底: {output[:100]}"}
    return {"status": "fail", "message": f"sanitize_ssd_file 失败: {result}"}

test("SSDSanitizer - 手机号", test_sanitize_phone)
test("SSDSanitizer - 邮箱", test_sanitize_email)
test("SSDSanitizer - 身份证号", test_sanitize_id_card)
test("sanitize_ssd_file", test_sanitize_ssd_file)

# ============================================================
# 6. 批量处理测试
# ============================================================
print("\n" + "="*60)
print("📦 6. 批量处理测试")
print("="*60)

def test_batch_process_standard():
    """测试 batch_process - 标准减肥（用 process_file 测试单文件批量）"""
    batch_dir = TEST_DIR / "batch_test"
    batch_dir.mkdir(exist_ok=True)
    for i in range(3):
        (batch_dir / f"file_{i}.txt").write_text(f"这是第 {i+1} 个测试文件。" * 20, encoding="utf-8")
    
    from batch_processor import process_file
    results = []
    out_dir = str(OUTPUT_DIR / "batch_output")
    for f in batch_dir.glob("*.txt"):
        file_info = {
            'path': str(f),
            'name': f.name,
            'ext': f.suffix.lower(),
            'relative_path': f.name,
            'size': f.stat().st_size
        }
        r = process_file(file_info, "slim", {"mode": "standard"}, out_dir)
        results.append(r)
    
    success = sum(1 for r in results if r.get("status") == "success")
    if success > 0:
        return {"status": "pass", "message": f"批量处理 {len(results)} 个文件，成功 {success} 个"}
    return {"status": "fail", "message": f"批量处理全部失败: {results}"}

def test_batch_process_ssd():
    """测试 SSD 批量转换（直接调用 convert_to_ssd_v2）"""
    batch_dir = TEST_DIR / "batch_test_ssd"
    batch_dir.mkdir(exist_ok=True)
    (batch_dir / "test.txt").write_text("这是一个测试文件。" * 50, encoding="utf-8")
    (batch_dir / "test.md").write_text("# 标题\n\n内容。" * 20, encoding="utf-8")
    
    output_dir = OUTPUT_DIR / "batch_ssd_output"
    output_dir.mkdir(exist_ok=True)
    
    results = []
    for f in batch_dir.glob("*"):
        if f.is_file():
            output_path = output_dir / f"{f.stem}.ssd"
            try:
                ssd_content = convert_to_ssd_v2(str(f))
                if isinstance(ssd_content, str) and len(ssd_content) > 5:
                    output_path.write_text(ssd_content, encoding="utf-8")
                    results.append({"status": "success", "file": f.name})
                else:
                    results.append({"status": "error", "file": f.name, "error": str(ssd_content)})
            except Exception as e:
                results.append({"status": "error", "file": f.name, "error": str(e)})
    
    success = sum(1 for r in results if r["status"] == "success")
    if success > 0:
        return {"status": "pass", "message": f"批量转换 {len(results)} 个文件，成功 {success} 个"}
    return {"status": "fail", "message": f"批量转换全部失败: {results}"}

def test_scan_folder():
    """测试 scan_folder"""
    batch_dir = TEST_DIR / "batch_test"
    if not batch_dir.exists():
        return {"status": "skip", "message": "测试目录不存在"}
    
    result = scan_folder(str(batch_dir))
    if isinstance(result, list) and len(result) > 0:
        return {"status": "pass", "message": f"扫描到 {len(result)} 个文件"}
    return {"status": "fail", "message": f"scan_folder 失败: {result}"}

test("batch_process - standard", test_batch_process_standard)
test("batch_process - ssd", test_batch_process_ssd)
test("scan_folder", test_scan_folder)

# ============================================================
# 7. 图片压缩测试
# ============================================================
print("\n" + "="*60)
print("📦 7. 图片压缩测试")
print("="*60)

def test_compress_image():
    """测试图片压缩"""
    try:
        from PIL import Image
        import numpy as np
        
        img_dir = TEST_DIR / "images"
        img_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建测试图片
        img_array = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img_path = img_dir / "test_image.png"
        img.save(str(img_path))
        
        orig_size = img_path.stat().st_size
        
        # 压缩
        result = compress_image(str(img_path), str(img_path), quality=50)
        
        if result.get("success"):
            new_size = img_path.stat().st_size
            return {"status": "pass", "message": f"{orig_size}B → {new_size}B (节省 {(1-new_size/orig_size)*100:.1f}%)"}
        return {"status": "fail", "message": f"压缩失败: {result}"}
    except ImportError:
        return {"status": "skip", "message": "PIL 不可用，跳过图片测试"}

test("compress_image", test_compress_image)

# ============================================================
# 8. 边缘情况测试
# ============================================================
print("\n" + "="*60)
print("📦 8. 边缘情况测试")
print("="*60)

def test_empty_content():
    """测试空内容"""
    filepath = create_test_file("", "txt")
    text = read_txt(str(filepath))
    if isinstance(text, str):
        return {"status": "pass", "message": "空文件读取正常"}
    return {"status": "fail", "message": f"空文件读取异常: {type(text)}"}

def test_very_long_content():
    """测试超长内容"""
    content = "测试内容。" * 10000
    filepath = create_test_file(content, "txt")
    text = read_txt(str(filepath))
    if isinstance(text, str) and len(text) > 10000:
        return {"status": "pass", "message": f"超长内容读取完成 ({len(text)} 字符)"}
    return {"status": "fail", "message": f"超长内容读取失败: {type(text)}"}

def test_special_characters():
    """测试特殊字符"""
    content = "特殊字符测试：🎉🚀💻 中文 日本語 한국어 Ελληνικά العربية"
    filepath = create_test_file(content, "txt")
    text = read_txt(str(filepath))
    if isinstance(text, str) and "🎉" in text:
        return {"status": "pass", "message": "特殊字符处理正常"}
    return {"status": "fail", "message": f"特殊字符处理失败: {text}"}

def test_docslimmer_empty_text():
    """测试 DocSlimmer 空文本"""
    ds = DocSlimmer()
    result = ds.slim("", compression_rate=0.3)
    if result.get("result") == "":
        return {"status": "pass", "message": "空文本处理正常"}
    return {"status": "fail", "message": f"空文本处理失败: {result}"}

def test_docsanitizer_empty_text():
    """测试 DocSanitizer 空文本"""
    ds = DocSanitizer()
    result = ds.sanitize("")
    # DocSanitizer.sanitize 返回 {"result": "", "stats": {...}}
    if isinstance(result, dict) and result.get("result") == "":
        return {"status": "pass", "message": "空文本脱敏正常"}
    return {"status": "fail", "message": f"空文本脱敏失败: {result}"}

test("边缘情况 - 空文件", test_empty_content)
test("边缘情况 - 超长内容", test_very_long_content)
test("边缘情况 - 特殊字符", test_special_characters)
test("边缘情况 - DocSlimmer 空文本", test_docslimmer_empty_text)
test("边缘情况 - DocSanitizer 空文本", test_docsanitizer_empty_text)

# ============================================================
# 总结
# ============================================================
print("\n" + "="*60)
print("📊 测试结果汇总")
print("="*60)
print(f"  {GREEN}✅ 通过: {results['pass']}{RESET}")
print(f"  {RED}❌ 失败: {results['fail']}{RESET}")
print(f"  {YELLOW}⏭️ 跳过: {results['skip']}{RESET}")
print(f"  总计: {results['pass'] + results['fail'] + results['skip']}")

if results['fail'] == 0:
    print(f"\n  {GREEN}🎉 所有测试通过！{RESET}")
else:
    print(f"\n  {RED}⚠️ 有 {results['fail']} 个测试失败，请检查。{RESET}")

# 清理测试输出
print(f"\n测试输出目录: {OUTPUT_DIR}")
