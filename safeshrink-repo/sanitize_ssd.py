# -*- coding: utf-8 -*-
"""
sanitize_ssd.py - SSD 文件专用脱敏模块

功能：
1. 分块处理 SSD（代码块、表格、引用等保持原样）
2. 对段落和普通文本进行脱敏
3. 支持：手机号、邮箱、身份证、银行卡、IP地址

特点：
- 保持 SSD 语法完全不变
- 仅对文档主体内容进行脱敏处理
"""

import re
from pathlib import Path


class SSDSanitizer:
    """
    SSD 文件脱敏器
    策略：逐行/逐块处理，识别 SSD 结构并保护
    """
    
    def __init__(self):
        self._stats = {}
    
    def _count_sensitive(self, text: str, items: dict) -> dict:
        """统计敏感信息数量"""
        import re as regex_module

        stats = {}

        # 保护 Base64 嵌入的图片
        text_for_count = re.sub(r'data:image/[^)]+;base64,[A-Za-z0-9+/=]+', '[图片]', text)
        
        if items.get('手机号', True):
            stats['手机号'] = len(re.findall(r'\b1[3-9]\d{9}\b', text_for_count))
        if items.get('邮箱', True):
            stats['邮箱'] = len(re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', text_for_count))
        if items.get('身份证', True):
            # 15位或18位身份证
            stats['身份证'] = len(re.findall(r'\b\d{15}\b|\b\d{18}\b|\b\d{17}[\dXx]\b', text_for_count))
        if items.get('银行卡', True):
            stats['银行卡'] = len(re.findall(r'\b\d{13,19}\b', text_for_count))
        if items.get('IP地址', True):
            stats['IP地址'] = len(re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', text_for_count))
        if items.get('投标/成交价', True):
            # 仅匹配有明确金额上下文的数字，排除"2024年""1800户"等误报
            amount_patterns = [
                # ¥/$/€ + 数字
                r'(?<![a-zA-Z0-9])[¥$€£]\s*[\d,]+(?:\.\d+)?',
                # 数字 + 单位（万/亿/元/人/天/年/套）
                r'(?<![a-zA-Z0-9])[\d]+(?:\.\d+)?\s*[亿万万千]?\s*(?:元|万|亿|人|天|年|套|美元|欧元|英镑)',
                # 数字 + 逗号（3位分隔的大额数字，常见于合同价格）
                r'(?<![a-zA-Z0-9])[\d]{1,3}(?:,[\d]{3}){2,}(?:\.\d+)?',
                # 带金额关键词的数字
                r'(?<![a-zA-Z0-9])(?:报价|成交价?|投标价?|合同价?|总价?|预算|金额|费用)\s*[:：]?\s*[\d,]+(?:\.\d+)?',
            ]
            count = 0
            for pat in amount_patterns:
                count += len(re.findall(pat, text_for_count))
            stats['投标/成交价'] = count
        if items.get('护照号', True):
            stats['护照号'] = len(re.findall(r'\b[Ee1-9][A-Z0-9]{7,9}\b', text_for_count))
        if items.get('社保卡号', True):
            stats['社保卡号'] = len(re.findall(r'\b\d{18}\b', text_for_count))
        if items.get('Mac地址', True):
            stats['Mac地址'] = len(re.findall(r'\b([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b', text_for_count))
        if items.get('IMEI', True):
            stats['IMEI'] = len(re.findall(r'\b\d{15}\b', text_for_count))
        if items.get('车牌号', True):
            stats['车牌号'] = len(re.findall(
                r'\b[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领警][A-Z][A-Z0-9]{4,5}[A-Z0-9挂学港澳](?:\.[A-Z])?\b', text_for_count))
        if items.get('公文份号', True):
            # 份号：№+6位数字 或 NO+数字，顶格标注
            stats['公文份号'] = len(re.findall(r'№\d{6,}|NO\d{6,}|Nr\d{6,}|N[rR]\d{6,}', text_for_count))
        if items.get('公文密级', True):
            # 密级标注：绝密★/机密★/秘密★ + 数字+年
            stats['公文密级'] = len(re.findall(r'(?:绝密|机密|秘密)\s*[★☆]?\s*\d+\s*年', text_for_count))
        if items.get('公文文号', True):
            # 文号：〔年份〕部门字第XX号，如"〔2024〕人社字第0382号"
            stats['公文文号'] = len(re.findall(r'〔\d{4}〕[\u4e00-\u9fa5]+字第\d+号', text_for_count))
        if items.get('医保号', True):
            # 医保卡号：18位，与身份证格式相近，但前6位为地区码；取18位数字串（与身份证同）
            stats['医保号'] = len(re.findall(r'\b\d{18}\b', text_for_count))
        if items.get('病历号', True):
            # 病历号：医院自定义格式，常见前缀+数字串
            # 匹配常见格式：BL/MR/EMR/门诊/住院 + 数字
            stats['病历号'] = len(re.findall(
                r'\b(?:BL|MR|EMR|门诊号?|住院号?|病历号?|病案号?)\s*[：:]?\s*\d{4,}\b'
                r'|(?<![a-zA-Z0-9])\d{8,10}(?![a-zA-Z0-9])', text_for_count))
        
        return stats
    
    def _mask_phone(self, phone: str) -> str:
        return phone[:3] + '****' + phone[-4:]
    
    def _mask_email(self, email: str) -> str:
        parts = email.split('@')
        if len(parts[0]) > 2:
            return parts[0][:2] + '***@' + parts[1]
        return '***@' + parts[1]
    
    def _mask_id_card(self, id_card: str) -> str:
        if len(id_card) == 18:
            return id_card[:3] + '***********' + id_card[-4:]
        return id_card[:3] + '****' + id_card[-4:]
    
    def _mask_bank_card(self, card: str) -> str:
        return card[:6] + '******' + card[-4:]

    def _mask_passport(self, p: str) -> str:
        if len(p) >= 4:
            return p[0] + '*' * (len(p) - 2) + p[-1]
        return '*' * len(p)

    def _mask_mac(self, m: str) -> str:
        parts = re.split(r'[:-]', m)
        if len(parts) >= 3:
            return (parts[0] + ':' + parts[1] + ':' + parts[2] + ':**:**:**').upper()
        return '**:**:**:**:**:**'

    def _mask_imei(self, imei: str) -> str:
        return imei[:6] + '******' + imei[-2:]

    def _mask_plate(self, plate: str) -> str:
        if len(plate) >= 3:
            return plate[:2] + '*' * (len(plate) - 2)
        return '*' * len(plate)

    def _sanitize_line(self, line: str, items: dict, custom_words: list) -> str:
        """对单行文本进行脱敏"""
        # 保护 Base64 嵌入的图片（data:image/...;base64,...）
        # 用占位符临时替换，处理完再还原
        base64_places = {}
        def protect_base64(m):
            placeholder = f'__BASE64_PLACEHOLDER_{len(base64_places)}__'
            base64_places[placeholder] = m.group(0)
            return placeholder
        line = re.sub(r'data:image/[^)]+;base64,[A-Za-z0-9+/=]+', protect_base64, line)

        text = line

        if items.get('手机号', True):
            text = re.sub(r'\b1[3-9]\d{9}\b', lambda m: self._mask_phone(m.group(0)), text)
        
        if items.get('邮箱', True):
            text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', 
                         lambda m: self._mask_email(m.group(0)), text)
        
        if items.get('身份证', True):
            text = re.sub(r'\b\d{15}\b|\b\d{18}\b|\b\d{17}[\dXx]\b', 
                         lambda m: self._mask_id_card(m.group(0)), text)
        
        if items.get('银行卡', True):
            text = re.sub(r'\b\d{13,19}\b', lambda m: self._mask_bank_card(m.group(0)), text)
        
        if items.get('IP地址', True):
            text = re.sub(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '***.***.***.***', text)
        
        # 脱敏金额（仅匹配有金额上下文的数字，排除"2024年""1800户"等误报）
        if items.get('投标/成交价', True):
            amount_patterns = [
                r'(?<![a-zA-Z0-9])[¥$€£]\s*[\d,]+(?:\.\d+)?',
                r'(?<![a-zA-Z0-9])[\d]+(?:\.\d+)?\s*[亿万万千]?\s*(?:元|万|亿|人|天|年|套|美元|欧元|英镑)',
                r'(?<![a-zA-Z0-9])[\d]{1,3}(?:,[\d]{3}){2,}(?:\.\d+)?',
                r'(?<![a-zA-Z0-9])(?:报价|成交价?|投标价?|合同价?|总价?|预算|金额|费用)\s*[:：]?\s*[\d,]+(?:\.\d+)?',
            ]
            for pat in amount_patterns:
                text = re.sub(pat, '***', text)
        
        if items.get('护照号', True):
            text = re.sub(r'\b[Ee1-9][A-Z0-9]{7,9}\b',
                         lambda m: self._mask_passport(m.group(0)), text)
        
        if items.get('社保卡号', True):
            text = re.sub(r'\b\d{18}\b', lambda m: self._mask_id_card(m.group(0)), text)
        
        if items.get('Mac地址', True):
            text = re.sub(r'\b([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b',
                         lambda m: self._mask_mac(m.group(0)), text)
        
        if items.get('IMEI', True):
            text = re.sub(r'\b\d{15}\b', lambda m: self._mask_imei(m.group(0)), text)
        
        if items.get('车牌号', True):
            text = re.sub(r'\b[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领警][A-Z][A-Z0-9]{4,5}[A-Z0-9挂学港澳](?:\.[A-Z])?\b',
                         lambda m: self._mask_plate(m.group(0)), text)
        
        if items.get('公文份号', True):
            # 份号：保留前缀符号（№/NO/Nr等），遮罩数字部分
            def mask_docnum(m):
                prefix = m.group(1)
                digits = re.sub(r'[^0-9]', '', m.group(0))
                return prefix + '*' * len(digits)
            text = re.sub(r'(№|NO|Nr|N[rR])\d{6,}', mask_docnum, text)
        
        if items.get('公文密级', True):
            # 密级标注：保留密级词（绝密/机密/秘密），遮罩期限
            text = re.sub(r'((?:绝密|机密|秘密)\s*[★☆]?\s*)\d+(\s*年)',
                         lambda m: m.group(1) + '***' + m.group(2), text)
        
        if items.get('公文文号', True):
            # 文号：保留年份和部门，遮罩序号
            text = re.sub(r'(〔\d{4}〕[\u4e00-\u9fa5]+字第)\d+(号)',
                         lambda m: m.group(1) + '***' + m.group(2), text)
        
        if items.get('医保号', True):
            text = re.sub(r'\b\d{18}\b', lambda m: self._mask_id_card(m.group(0)), text)
        
        if items.get('病历号', True):
            text = re.sub(
                r'\b(?:BL|MR|EMR|门诊号?|住院号?|病历号?|病案号?)\s*[：:]?\s*\d{4,}\b'
                r'|(?<![a-zA-Z0-9])\d{8,10}(?![a-zA-Z0-9])',
                lambda m: self._mask_id_card(m.group(0)) if m.group(0).isdigit() else re.sub(r'\d+', '***', m.group(0)),
                text)
        
        # 自定义词
        if custom_words:
            for word in custom_words:
                if len(word) >= 2:
                    text = re.sub(re.escape(word), word[0] + '*' * (len(word) - 1), text)

        # 还原 Base64 图片
        for placeholder, original in base64_places.items():
            text = text.replace(placeholder, original)

        return text
    
    def _is_code_block(self, line: str, in_code: bool) -> bool:
        """检测是否是代码块边界"""
        # 检查 ``` 包围的代码块
        if line.strip().startswith('```'):
            return True
        return False
    
    def _is_table_row(self, line: str) -> bool:
        """检测是否是表格行"""
        line = line.strip()
        # 表格行必须以 | 开头和结尾（或只有一边）
        if '|' in line:
            # 跳过分隔行 |---|---|
            if re.match(r'^\|?[\s\-:|]+\|$', line.replace(' ', '')):
                return False
            return True
        return False
    
    def _is_ref_block(self, line: str) -> bool:
        """检测是否是引用块"""
        return line.lstrip().startswith('>')
    
    def _is_header(self, line: str) -> bool:
        """检测是否是标题行"""
        return bool(re.match(r'^#{1,6}\s+', line))
    
    def _is_list_item(self, line: str) -> bool:
        """检测是否是列表项"""
        stripped = line.lstrip()
        # 无序列表 - * +
        if re.match(r'^[-*+]\s+', stripped):
            return True
        # 有序列表 1. 2.
        if re.match(r'^\d+\.\s+', stripped):
            return True
        # 任务列表 - [ ] - [x]
        if re.match(r'^[-*+]\s+\[[ x]\]\s+', stripped):
            return True
        return False
    
    def _is_link_ref(self, line: str) -> bool:
        """检测是否是链接/图片引用行"""
        stripped = line.strip()
        # 图片 ![alt](url)
        if re.match(r'!\[[^\]]*\]\([^)]+\)', stripped):
            return True
        # 链接 [text](url)
        if re.match(r'\[[^\]]+\]\([^)]+\)', stripped):
            return True
        return False
    
    def _is_html_tag(self, line: str) -> bool:
        """检测是否包含 HTML 标签"""
        return bool(re.search(r'<[^>]+>', line))
    
    def sanitize(self, content: str, items: dict = None, custom_words: list = None) -> dict:
        """
        对 SSD 内容进行脱敏
        
        Args:
            content: SSD 原文
            items: 要检测的敏感信息类型
            custom_words: 自定义敏感词列表
        
        Returns:
            {'result': 脱敏后内容, 'stats': {'手机号': 0, '邮箱': 1, ...}}
        """
        if items is None:
            items = {'手机号': True, '邮箱': True, '身份证': True, 
                    '银行卡': True, 'IP地址': True}
        
        # 先统计原始内容中的敏感信息
        stats = self._count_sensitive(content, items)
        
        lines = content.split('\n')
        result_lines = []
        in_code_block = False
        
        for line in lines:
            # 代码块检测（``` 包围的多行代码块）
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                result_lines.append(line)
                continue
            
            # 在代码块内，不处理
            if in_code_block:
                result_lines.append(line)
                continue
            
            # 对所有行进行脱敏
            processed = self._sanitize_line(line, items, custom_words)
            result_lines.append(processed)
        
        return {
            'result': '\n'.join(result_lines),
            'stats': stats
        }


def sanitize_ssd_file(file_path: str, items: dict = None, custom_words: list = None) -> dict:
    """对单个 SSD 文件进行脱敏"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    sanitizer = SSDSanitizer()
    return sanitizer.sanitize(content, items, custom_words)
