# -*- coding: utf-8 -*-
"""
ssd_embed_images.py - 将 SSD / DOCX 中的本地图片转为 Base64 嵌入

支持三种输入：
1. SSD 文件（本地图片引用）
2. DOCX 文件（内置图片）
3. 已有占位符的 SSD（MarkItDown 输出）

使用：
    from ssd_embed_images import embed_images
    result = embed_images(source_path="input.docx", output_path="output.ssd")
"""

import base64
import io
import os
import re
import zipfile
from pathlib import Path
from typing import Dict, Optional, List, Tuple
from urllib.parse import unquote


# 支持的图片扩展名
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp', '.ico', '.tiff'}


def get_mime_type(ext: str) -> str:
    """获取 MIME 类型"""
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.svg': 'image/svg+xml',
        '.bmp': 'image/bmp',
        '.ico': 'image/x-icon',
        '.tiff': 'image/tiff',
    }
    return mime_types.get(ext.lower(), 'image/png')


def is_image_url(url: str) -> bool:
    """判断是否是需要跳过的图片（网络图片 / 已嵌入）"""
    url_lower = url.lower().strip()
    return (
        url_lower.startswith(('http://', 'https://', '//')) or
        url_lower.startswith('data:')
    )


def image_to_base64(image_data: bytes, mime_type: Optional[str] = None) -> str:
    """将图片数据转为 Base64 data URI"""
    if mime_type is None:
        mime_type = 'image/png'
    encoded = base64.b64encode(image_data).decode('ascii')
    return f'data:{mime_type};base64,{encoded}'


# ============================================================
# 方式一：处理 DOCX 文件（提取内置图片）
# ============================================================

def extract_images_from_docx(docx_path: str) -> List[Dict]:
    """
    从 DOCX 文件中提取所有图片

    Returns:
        [{'name': 'media/image1.png', 'data': b'...', 'size': 1024}, ...]
    """
    images = []
    with zipfile.ZipFile(docx_path, 'r') as z:
        for name in z.namelist():
            if 'media/' in name and not name.endswith('/'):
                ext = os.path.splitext(name)[1].lower()
                if ext in IMAGE_EXTENSIONS:
                    info = z.getinfo(name)
                    images.append({
                        'name': name,
                        'data': z.read(name),
                        'size': info.file_size,
                        'mime': get_mime_type(ext)
                    })
    return images


def docx_to_ssd_with_images(docx_path: str) -> Dict:
    """
    将 DOCX 转换为 SSD，同时嵌入图片为 Base64

    Returns:
        {
            'text': SSD 文本,
            'images': [{'index': 1, 'name': '...', 'embedded': True}, ...],
            'stats': {...}
        }
    """
    import markitdown

    # 提取图片
    images = extract_images_from_docx(docx_path)
    print(f"  从 DOCX 提取了 {len(images)} 张图片")

    # 转换为 SSD（得到占位符）
    md = markitdown.MarkItDown()
    result = md.convert(docx_path)
    ssd_text = result.text_content

    # 提取占位符位置
    # MarkItDown 输出格式: ![](data:image/png;base64...) 或 ![alt](path)
    # 我们需要把占位符替换为真正的 Base64
    placeholder_pattern = re.compile(
        r'!\[([^\]]*)\]\((data:image/[^)]+)\)',
        re.UNICODE
    )

    # 构建图片索引（按出现顺序）
    image_map = {}  # index -> image_data
    placeholder_count = [0]  # 用于计数的可变容器

    def replace_placeholder(match):
        alt_text = match.group(1)
        data_url = match.group(2)

        # 检查是否是占位符（base64... 结尾）
        if data_url.endswith('base64...'):
            idx = placeholder_count[0]
            placeholder_count[0] += 1

            if idx < len(images):
                img = images[idx]
                real_data_url = image_to_base64(img['data'], img['mime'])
                return f'![{alt_text}]({real_data_url})'
            else:
                # 没有对应的图片，保留原样
                return match.group(0)
        else:
            # 已经是完整的 data URL，跳过
            return match.group(0)

    # 执行替换
    new_text = placeholder_pattern.sub(replace_placeholder, ssd_text)

    stats = {
        'images_extracted': len(images),
        'images_total': placeholder_count[0],
        'images_embedded': sum(1 for i in range(min(placeholder_count[0], len(images)))),
    }

    return {
        'text': new_text,
        'images': images,
        'stats': stats
    }


# ============================================================
# 方式二：处理 SSD 文件（本地图片引用）
# ============================================================

def resolve_image_path(ref: str, ssd_path: Optional[str] = None) -> Optional[str]:
    """解析图片引用为绝对路径"""
    if not ref:
        return None

    ref = unquote(ref)

    # 清理 file:// 协议
    if ref.startswith('file://'):
        ref = ref[7:]

    # Windows 盘符
    if re.match(r'^[A-Za-z]:', ref):
        return ref if os.path.exists(ref) else None

    # 绝对路径
    if ref.startswith('/') or ref.startswith('\\'):
        return ref if os.path.exists(ref) else None

    # 相对路径
    if ssd_path:
        md_dir = os.path.dirname(os.path.abspath(ssd_path))
        abs_path = os.path.abspath(os.path.join(md_dir, ref))
        return abs_path if os.path.exists(abs_path) else None

    return None


def embed_images_in_ssd(
    ssd_text: str,
    ssd_path: Optional[str] = None,
    skip_large_images: bool = True,
    max_size_mb: float = 10.0
) -> Dict:
    """
    将 SSD 中的本地图片嵌入 Base64

    Args:
        ssd_text: SSD 文本内容
        ssd_path: SSD 文件路径（用于解析相对路径）
        skip_large_images: 是否跳过过大图片
        max_size_mb: 图片大小上限

    Returns:
        {
            'text': 转换后的 SSD,
            'stats': {...},
            'errors': [...]
        }
    """
    stats = {
        'images': 0,
        'embedded': 0,
        'skipped_online': 0,
        'skipped_large': 0,
        'skipped_error': 0,
        'total_size': 0,
    }
    errors = []

    IMAGE_PATTERN = re.compile(
        r'!\[([^\]]*)\]\(([^)\s]+)(?:\s+"[^"]*")?\)',
        re.UNICODE
    )

    def replace_image(match):
        alt_text = match.group(1) or ''
        image_ref = match.group(2).strip()
        original = match.group(0)

        stats['images'] += 1

        # 跳过网络图片和已嵌入的图片
        if is_image_url(image_ref):
            stats['skipped_online'] += 1
            return original

        # 解析图片路径
        image_path = resolve_image_path(image_ref, ssd_path)
        if not image_path:
            stats['skipped_error'] += 1
            errors.append(f"找不到图片: {image_ref}")
            return original

        # 检查大小
        try:
            file_size = os.path.getsize(image_path)
        except OSError:
            stats['skipped_error'] += 1
            errors.append(f"无法读取: {image_ref}")
            return original

        stats['total_size'] += file_size

        if skip_large_images and file_size > max_size_mb * 1024 * 1024:
            stats['skipped_large'] += 1
            return original

        # 读取并转换
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            ext = os.path.splitext(image_path)[1].lower()
            mime = get_mime_type(ext)
            base64_data = image_to_base64(image_data, mime)
            stats['embedded'] += 1
            return f'![{alt_text}]({base64_data})'
        except (IOError, OSError, base64.binascii.Error) as e:
            stats['skipped_error'] += 1
            errors.append(f"转换失败: {image_ref}")
            return original

    result_text = IMAGE_PATTERN.sub(replace_image, ssd_text)

    return {
        'text': result_text,
        'stats': stats,
        'errors': errors
    }


# ============================================================
# 统一入口
# ============================================================

def embed_images(source_path: str, output_path: Optional[str] = None) -> Dict:
    """
    统一入口：自动识别文件类型并处理

    Args:
        source_path: 输入文件（.docx / .ssd / .ssd）
        output_path: 输出 SSD 文件路径

    Returns:
        {
            'text': SSD 文本,
            'stats': {...},
            'output_path': 输出路径
        }
    """
    ext = os.path.splitext(source_path)[1].lower()

    if ext == '.docx':
        # DOCX: 提取内置图片并嵌入
        result = docx_to_ssd_with_images(source_path)
        stats = result['stats']
        text = result['text']
    elif ext in ('.ssd', '.ssd'):
        # SSD: 处理本地图片引用
        with open(source_path, 'r', encoding='utf-8') as f:
            text = f.read()
        result = embed_images_in_ssd(text, ssd_path=source_path)
        stats = result['stats']
        text = result['text']
    else:
        return {
            'text': '',
            'stats': {'error': f'不支持的文件格式: {ext}'},
            'output_path': None
        }

    # 确定输出路径
    if output_path is None:
        base, _ = os.path.splitext(source_path)
        output_path = f"{base}_嵌入.ssd"

    # 写入文件
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)

    return {
        'text': text,
        'stats': stats,
        'output_path': output_path
    }


# ============================================================
# CLI
# ============================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description='将图片嵌入 SSD')
    parser.add_argument('input', help='输入文件（.docx / .ssd）')
    parser.add_argument('-o', '--output', help='输出 SSD 文件')

    args = parser.parse_args()

    print(f"处理: {args.input}")
    result = embed_images(args.input, args.output)

    if 'error' in result['stats']:
        print(f"错误: {result['stats']['error']}")
        return 1

    stats = result['stats']
    print(f"完成: {result['output_path']}")
    print(f"  图片嵌入: {stats.get('images_embedded', stats.get('embedded', 0))}")
    print(f"  提取图片: {stats.get('images_extracted', 0)}")
    if result.get('errors'):
        print(f"  错误: {result['errors']}")

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
