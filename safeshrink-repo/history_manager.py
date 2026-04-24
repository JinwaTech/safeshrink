"""
处理历史管理器
功能：记录和管理文件处理历史
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime


class HistoryManager:
    """处理历史管理器"""
    
    def __init__(self, history_file=None):
        if history_file is None:
            # 优先使用 AppData 目录（稳定持久）
            # PyInstaller 打包后 EXE 目录会被重建，不能放那里
            appdata = os.environ.get('APPDATA', '')
            if appdata:
                appdata_dir = Path(appdata) / 'SafeShrink'
                appdata_dir.mkdir(parents=True, exist_ok=True)
                history_file = appdata_dir / 'processing_history.json'
            else:
                # Fallback: EXE 所在目录
                if getattr(sys, 'frozen', False):
                    base_dir = Path(sys.executable).parent.resolve()
                else:
                    base_dir = Path(__file__).parent.resolve()
                history_file = base_dir / 'processing_history.json'
        
        self.history_file = Path(history_file)
        self.max_records = 100  # 最多保存100条记录
        self.history = self.load_history()
    
    def load_history(self):
        """加载历史记录"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return []
        return []
    
    def save_history(self):
        """保存历史记录"""
        try:
            # 只保留最近的记录
            records = self.history[-self.max_records:]
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史失败: {e}")
    
    def add_record(self, file_name, file_path, action, original_size, new_size, output_path=None,
                   original_tokens=None, new_tokens=None):
        """添加处理记录"""
        record = {
            'id': datetime.now().strftime('%Y%m%d%H%M%S'),
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'file_name': file_name,
            'file_path': str(file_path),
            'action': action,  # 'slim' 或 'sanitize'
            'original_size': original_size,
            'new_size': new_size,
            'saved_size': original_size - new_size if original_size > 0 else 0,
            'saved_percent': round((1 - new_size/original_size) * 100, 1) if original_size > 0 else 0,
            'output_path': str(output_path) if output_path else None,
            'original_tokens': original_tokens,
            'new_tokens': new_tokens,
        }
        
        self.history.append(record)
        self.save_history()
        return record
    
    def add_batch_record(self, total_files, success_count, total_saved, action='slim',
                          original_tokens=None, new_tokens=None):
        """添加批量处理记录"""
        record = {
            'id': datetime.now().strftime('%Y%m%d%H%M%S'),
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'file_name': f'批量处理 ({total_files}个文件)',
            'file_path': None,
            'action': action,
            'original_size': 0,
            'new_size': 0,
            'saved_size': total_saved,
            'saved_percent': 0,
            'output_path': None,
            'batch': True,
            'total_files': total_files,
            'success_count': success_count,
            'original_tokens': original_tokens,
            'new_tokens': new_tokens,
        }
        
        self.history.append(record)
        self.save_history()
        return record
    
    def get_history(self, limit=50):
        """获取历史记录"""
        return self.history[-limit:][::-1]  # 倒序，最新的在前

    def filter_history(self, filename=None, action=None, date_from=None, date_to=None, limit=50):
        """筛选历史记录

        Args:
            filename: 文件名关键字（不区分大小写，包含匹配）
            action: 操作类型筛选，'slim' 或 'sanitize'
            date_from: 起始日期，格式 'YYYY-MM-DD'，含当天
            date_to: 结束日期，格式 'YYYY-MM-DD'，含当天
            limit: 最大返回条数
        Returns:
            倒序（最新在前）的筛选结果列表
        """
        records = self.history[::-1]  # 先倒序，从新到旧
        filtered = []
        for r in records:
            # 文件名筛选
            if filename:
                fn = r.get('file_name', '')
                if filename.lower() not in fn.lower():
                    continue
            # 操作类型筛选
            if action and r.get('action') != action:
                continue
            # 日期范围筛选
            if date_from:
                if r.get('time', '')[:10] < date_from:
                    continue
            if date_to:
                if r.get('time', '')[:10] > date_to:
                    continue
            filtered.append(r)
            if len(filtered) >= limit:
                break
        return filtered

    def clear_history(self):
        """清空历史"""
        self.history = []
        self.save_history()
    
    def delete_record(self, record_id):
        """删除单条记录"""
        self.history = [r for r in self.history if r['id'] != record_id]
        self.save_history()
    
    @staticmethod
    def format_size(size):
        """格式化文件大小"""
        if size is None or size == 0:
            return "-"
        for unit in ['B', 'KB', 'MB', 'GB']:
            if abs(size) < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    @staticmethod
    def get_action_name(action):
        """获取操作名称"""
        names = {
            'slim': '文件减肥',
            'sanitize': '文档脱敏'
        }
        return names.get(action, action)
