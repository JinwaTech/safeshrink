# -*- coding: utf-8 -*-
"""
file_status.py - 文件处理状态检测模块

功能：
1. 检测文件夹/文件是否已被 SafeShrink 处理过
2. 三层标记体系：文件名标记 + 隐藏标记文件 + 哈希索引
3. 支持"直接复制"文件的状态记录

使用：
    from file_status import FileStatusChecker
    checker = FileStatusChecker()
    status = checker.check_folder("/path/to/folder")
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional


# 标记文件名（隐藏）
MARKER_FILE = ".safeshrink_processed"

# 可处理的文件扩展名
PROCESSABLE_EXTENSIONS = {
    # 文档
    '.docx', '.doc', '.pdf', '.pptx', '.ppt', '.xlsx', '.xls',
    # 网页
    '.html', '.htm', '.mhtml',
    # 文本
    '.md', '.txt', '.csv', '.json', '.xml',
    # 图片
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.svg',
}

# 已处理文件的后缀标记
PROCESSED_SUFFIXES = ['_脱敏', '_slim', '_Markdown', '_减肥', '_已处理']


class FileStatusChecker:
    """文件处理状态检测器"""

    def __init__(self):
        self.marker_file = MARKER_FILE

    # ========================
    # 公共接口
    # ========================

    def check_folder(self, folder_path: str, action: str = None) -> dict:
        """
        检测文件夹处理状态

        Args:
            folder_path: 文件夹路径
            action: 当前操作类型 ('sanitize' / 'slim' / 'markdown')，
                   用于判断哪些后缀算"已处理"。为 None 时所有后缀都算。

        Returns:
            {
                'status': 'PROCESSED' | 'PARTIAL' | 'UNPROCESSED' | 'NOT_FOUND',
                'details': { ... }
            }
        """
        folder = Path(folder_path)
        if not folder.exists():
            return {'status': 'NOT_FOUND', 'details': {'error': '文件夹不存在'}}

        # 确定当前操作对应的"已处理后缀"
        # sanitize: 只认 _脱敏
        # slim: 认 _脱敏 / _减肥 / _slim / _已处理
        # markdown: 认所有后缀
        if action == 'sanitize':
            relevant_suffixes = {'_脱敏'}
        elif action == 'slim':
            relevant_suffixes = {'_脱敏', '_减肥', '_slim', '_已处理'}
        else:
            relevant_suffixes = PROCESSED_SUFFIXES

        # 第一层：检查标记文件
        marker = folder / self.marker_file
        if marker.exists():
            try:
                marker_data = json.loads(marker.read_text(encoding='utf-8'))
                # sanitize 操作：只认 sanitize 标记的文件（跳过 slim/markdown 标记）
                # slim 操作：认所有类型
                if action == 'sanitize':
                    marker_op = marker_data.get('operation', '')
                    if marker_op == 'sanitize':
                        return {'status': 'PROCESSED', 'details': marker_data}
                    # 其他操作（slim/markdown）不视为已脱敏
                else:
                    return {'status': 'PROCESSED', 'details': marker_data}
            except (json.JSONDecodeError, UnicodeDecodeError):
                pass

        # 第二层：按操作类型检查文件名模式
        return self._check_by_filename(folder, relevant_suffixes)

    def check_file(self, file_path: str) -> dict:
        """
        检测单个文件处理状态

        Returns:
            {
                'status': 'PROCESSED' | 'UNPROCESSED' | 'NOT_PROCESSABLE' | 'NOT_FOUND',
                'is_copy': bool,          # 是否为直接复制的文件
                'original_name': str,      # 原始文件名（如果可推断）
                'details': { ... }
            }
        """
        file = Path(file_path)

        # 检查文件名后缀（不依赖文件存在性）
        for suffix in PROCESSED_SUFFIXES:
            if suffix in file.stem:
                # 尝试推断原始文件名
                original_name = file.stem.replace(suffix, '') + file.suffix
                return {
                    'status': 'PROCESSED',
                    'is_copy': False,
                    'original_name': original_name,
                    'details': {
                        'type': suffix,
                        'file': file.name
                    }
                }

        # 检查是否为可处理格式（不依赖文件存在性，基于扩展名判断）
        if file.suffix.lower() in PROCESSABLE_EXTENSIONS:
            return {
                'status': 'UNPROCESSED',
                'is_copy': False,
                'original_name': file.name,
                'details': {'file': file.name, 'ext': file.suffix}
            }

        # 不可处理的文件（如视频、音频等）
        return {
            'status': 'NOT_PROCESSABLE',
            'is_copy': True,
            'original_name': file.name,
            'details': {'file': file.name, 'ext': file.suffix}
        }

    def is_processable(self, file_path: str) -> bool:
        """检查文件是否可被 SafeShrink 处理"""
        return Path(file_path).suffix.lower() in PROCESSABLE_EXTENSIONS

    # ========================
    # 标记文件写入
    # ========================

    def write_marker(self, folder_path: str, processed_files: list,
                     output_folder: str, operation: str = "batch",
                     options: dict = None):
        """
        在输出文件夹中写入标记文件

        Args:
            folder_path: 原始文件夹路径
            processed_files: 处理记录列表
                [
                    {
                        'original': '合同.docx',
                        'output': '合同_脱敏.md',
                        'type': 'sanitize',       # sanitize | slim | markdown | copy
                        'status': 'success'       # success | skipped | failed
                    },
                    ...
                ]
            output_folder: 输出文件夹路径
            operation: 操作类型（batch/sanitize/slim/markdown）
            options: 附加选项（脱敏项目、压缩参数等）
        """
        output = Path(output_folder)

        # 统计信息
        stats = {
            'total': len(processed_files),
            'success': sum(1 for f in processed_files if f.get('status') == 'success'),
            'copied': sum(1 for f in processed_files if f.get('type') == 'copy'),
            'skipped': sum(1 for f in processed_files if f.get('status') == 'skipped'),
            'failed': sum(1 for f in processed_files if f.get('status') == 'failed'),
        }

        marker_data = {
            'version': '1.0.0',
            'tool': 'SafeShrink',
            'operation': operation,
            'processed_at': datetime.now().isoformat(),
            'source_folder': str(Path(folder_path).resolve()),
            'output_folder': str(output.resolve()),
            'stats': stats,
            'files': processed_files,
            'options': options or {},
        }

        marker_path = output / self.marker_file
        marker_path.write_text(
            json.dumps(marker_data, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )

        return marker_data

    def append_to_marker(self, folder_path: str, new_files: list):
        """
        追加处理记录到已有标记文件（用于增量处理）
        """
        folder = Path(folder_path)
        marker = folder / self.marker_file

        if marker.exists():
            try:
                marker_data = json.loads(marker.read_text(encoding='utf-8'))
                marker_data['files'].extend(new_files)
                marker_data['processed_at'] = datetime.now().isoformat()

                # 更新统计
                all_files = marker_data['files']
                marker_data['stats'] = {
                    'total': len(all_files),
                    'success': sum(1 for f in all_files if f.get('status') == 'success'),
                    'copied': sum(1 for f in all_files if f.get('type') == 'copy'),
                    'skipped': sum(1 for f in all_files if f.get('status') == 'skipped'),
                    'failed': sum(1 for f in all_files if f.get('status') == 'failed'),
                }

                marker.write_text(
                    json.dumps(marker_data, ensure_ascii=False, indent=2),
                    encoding='utf-8'
                )
                return marker_data
            except (json.JSONDecodeError, UnicodeDecodeError):
                # 标记文件损坏，重新写入
                return self.write_marker(folder_path, new_files, str(folder))
        else:
            return self.write_marker(folder_path, new_files, str(folder))

    # ========================
    # 哈希计算
    # ========================

    @staticmethod
    def file_hash(file_path: str, algorithm: str = 'sha256') -> str:
        """
        计算文件哈希值

        Args:
            file_path: 文件路径
            algorithm: 哈希算法（sha256/md5）

        Returns:
            'sha256:abc123...' 或 'md5:def456...'
        """
        file = Path(file_path)
        if not file.exists():
            return f'{algorithm}:0000000000'

        h = hashlib.new(algorithm)
        with open(file, 'rb') as f:
            # 分块读取，支持大文件
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)

        return f'{algorithm}:{h.hexdigest()}'

    def verify_integrity(self, folder_path: str) -> dict:
        """
        验证已处理文件夹的完整性

        检查：
        1. 标记文件是否存在
        2. 记录的文件是否都存在
        3. 文件哈希是否匹配（如果有记录）

        Returns:
            {
                'valid': bool,
                'missing_files': [],
                'hash_mismatches': [],
                'extra_files': []   # 文件夹中有但标记文件中没记录的
            }
        """
        folder = Path(folder_path)
        marker = folder / self.marker_file

        if not marker.exists():
            return {
                'valid': False,
                'reason': 'NO_MARKER',
                'missing_files': [],
                'hash_mismatches': [],
                'extra_files': []
            }

        try:
            marker_data = json.loads(marker.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return {
                'valid': False,
                'reason': 'CORRUPTED_MARKER',
                'missing_files': [],
                'hash_mismatches': [],
                'extra_files': []
            }

        recorded_files = set()
        missing = []
        hash_mismatches = []

        for record in marker_data.get('files', []):
            output_name = record.get('output', '')
            recorded_files.add(output_name)

            output_path = folder / output_name
            if not output_path.exists():
                missing.append(output_name)
            elif record.get('hash'):
                # 验证哈希
                current_hash = self.file_hash(str(output_path))
                if current_hash != record['hash']:
                    hash_mismatches.append(output_name)

        # 检查多余文件
        extra = []
        for f in folder.iterdir():
            if f.name == self.marker_file:
                continue
            if f.name not in recorded_files and not f.name.startswith('.'):
                extra.append(f.name)

        return {
            'valid': len(missing) == 0 and len(hash_mismatches) == 0,
            'reason': 'OK' if len(missing) == 0 and len(hash_mismatches) == 0 else 'INCOMPLETE',
            'missing_files': missing,
            'hash_mismatches': hash_mismatches,
            'extra_files': extra
        }

    # ========================
    # 内部方法
    # ========================

    def _check_by_filename(self, folder: Path, relevant_suffixes: set = None) -> dict:
        """通过文件名模式检测处理状态"""
        if relevant_suffixes is None:
            relevant_suffixes = set(PROCESSED_SUFFIXES)

        total = 0
        processed = 0
        unprocessed = 0
        copied = 0
        files = []

        for f in folder.iterdir():
            if f.name.startswith('.') or f.is_dir():
                continue

            total += 1
            file_info = self._check_single_file(f, relevant_suffixes)
            files.append(file_info)

            if file_info['status'] == 'PROCESSED':
                processed += 1
            elif file_info['status'] == 'UNPROCESSED':
                unprocessed += 1
            elif file_info['is_copy']:
                copied += 1

        if total == 0:
            return {'status': 'UNPROCESSED', 'details': {'error': '空文件夹', 'files': []}}

        if processed > 0 and unprocessed == 0:
            return {
                'status': 'PROCESSED',
                'details': {
                    'total': total,
                    'processed': processed,
                    'copied': copied,
                    'method': 'filename_detection',
                    'files': files
                }
            }
        elif processed > 0 and unprocessed > 0:
            return {
                'status': 'PARTIAL',
                'details': {
                    'total': total,
                    'processed': processed,
                    'unprocessed': unprocessed,
                    'copied': copied,
                    'method': 'filename_detection',
                    'files': files
                }
            }
        else:
            return {
                'status': 'UNPROCESSED',
                'details': {
                    'total': total,
                    'processable': unprocessed,
                    'copied': copied,
                    'method': 'filename_detection',
                    'files': files
                }
            }

    def _check_single_file(self, file: Path, relevant_suffixes: set = None) -> dict:
        """检测单个文件（使用指定后缀集合）"""
        if relevant_suffixes is None:
            relevant_suffixes = set(PROCESSED_SUFFIXES)

        file_name = file.name if isinstance(file, Path) else Path(file).name
        file_stem = Path(file_name).stem

        # 只检查与当前操作相关的后缀
        matched_suffix = None
        for suffix in relevant_suffixes:
            if suffix in file_stem:
                matched_suffix = suffix
                break

        if matched_suffix:
            original_name = file_stem.replace(matched_suffix, '') + Path(file_name).suffix
            return {
                'status': 'PROCESSED',
                'is_copy': False,
                'original_name': original_name,
                'details': {
                    'type': matched_suffix,
                    'file': file_name
                }
            }

        # 检查是否为可处理格式
        ext = Path(file_name).suffix.lower()
        if ext in PROCESSABLE_EXTENSIONS:
            return {
                'status': 'UNPROCESSED',
                'is_copy': False,
                'original_name': file_name,
                'details': {'file': file_name, 'ext': ext}
            }

        return {
            'status': 'NOT_PROCESSABLE',
            'is_copy': True,
            'original_name': file_name,
            'details': {'file': file_name, 'ext': ext}
        }


# ========================
# 便捷函数
# ========================

def check_status(path: str) -> dict:
    """快速检测路径处理状态（自动判断文件/文件夹）"""
    checker = FileStatusChecker()
    p = Path(path)
    if p.is_dir():
        return checker.check_folder(str(p))
    elif p.is_file():
        return checker.check_file(str(p))
    else:
        return {'status': 'NOT_FOUND', 'details': {'error': '路径不存在'}}


def get_user_friendly_message(check_result: dict) -> str:
    """
    将检测结果转换为用户友好的提示文案

    Args:
        check_result: check_folder() 或 check_file() 的返回值

    Returns:
        用户可读的提示文案
    """
    status = check_result.get('status')
    details = check_result.get('details', {})

    if status == 'PROCESSED':
        stats = details.get('stats', {})
        total = stats.get('total', details.get('total', 0))
        copied = stats.get('copied', details.get('copied', 0))
        msg = f"✅ 该文件夹已处理完成"
        if copied > 0:
            msg += f"（含 {copied} 个直接复制的文件）"
        msg += "，可直接使用。"
        return msg

    elif status == 'PARTIAL':
        stats = details.get('stats', {})
        processed = stats.get('success', details.get('processed', 0))
        unprocessed = stats.get('total', details.get('unprocessed', 0)) - processed
        msg = f"⚠️ 检测到部分文件已处理（{processed} 个），{unprocessed} 个未处理。"
        msg += "\n是否重新处理全部文件？"
        return msg

    elif status == 'UNPROCESSED':
        total = details.get('total', 0)
        processable = details.get('processable', total)
        copied = details.get('copied', 0)
        msg = f"📄 检测到 {total} 个文件"
        if processable > 0:
            msg += f"（其中 {processable} 个可处理"
            if copied > 0:
                msg += f"，{copied} 个将直接复制"
            msg += "）。"
        msg += "\n建议先进行脱敏/减肥处理？"
        return msg

    elif status == 'NOT_PROCESSABLE':
        return f"📎 该文件为不可处理格式，将直接复制到输出文件夹。"

    elif status == 'NOT_FOUND':
        return "❌ 文件或文件夹不存在。"

    return "❓ 无法判断文件处理状态。"
