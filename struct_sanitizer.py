# -*- coding: utf-8 -*-
"""
StructSanitizer - 结构化格式（JSON/XML/YAML/CSV）的安全脱敏器
只替换 string 类型的 value，不破坏数据结构。
"""

import re
import json
import csv
import io
import xml.etree.ElementTree as ET

# ===== 脱敏正则（与 DocSanitizer.PATTERNS 保持一致）=====

PATTERNS = {
    '手机号': r'(?<!\d)1[3-9]\d[\s\-]?\d{4}[\s\-]?\d{4}(?!\d)',
    '邮箱': r'\b[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,}\b',
    '身份证': r'(?<!\d)\d{17}[\dXx](?!\d)',
    '银行卡': r'(?<!\d)\d{16,19}(?!\d)',
    'IP地址': r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
    '社会信用代码': r'(?<!\d)91\d{16}(?!\d)',
    '营业执照号': r'(?<!\d)\d{15}(?!\d)',
    '开户许可证号': r'(?<!\d)[A-Z0-9]{14,16}(?!\d)',
    '投标/成交价': r'[¥￥]?\d{1,12}(?:\.\d{2})?(?![元])',
    '合同编号': r'(?<![a-zA-Z])[A-Z]{2,4}[-#]?\d{2,4}[-]?\d{2,8}(?![a-zA-Z])',
    '采购/订单编号': r'(?<![a-zA-Z])(?:CG|PO|DD|HT|FC)[-_]?\d{4,12}(?![a-zA-Z])',
    '固定电话': r'(?<!\d)0\d{2,3}[-]?\d{7,8}(?!\d)',
    '传真号': r'(?<!\d)(?:传真|Fax)[-:]?\s*0\d{2,3}[-]?\d{7,8}(?!\d)',
    '工号/学号': r'(?<![a-zA-Z])(?:工号|学号|员工号|编号)[-:]?\s*[A-Z0-9]{4,12}(?![a-zA-Z])',
    '项目代号': r'(?<![a-zA-Z])(?:项目[编号码]|PRJ|PROJ)[-_]?\d{2,8}(?![a-zA-Z])',
    '邮编': r'(?<!\d)\d{6}(?!\d)',

    # ===== 证件/设备标识 =====
    '护照号': r'(?<![A-Za-z])[EeGgPpDdSsHhLl][A-Za-z]?\d{7,9}(?!\d)',
    'Mac地址': r'(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}',
    'IMEI': r'(?<!\d)\d{15}(?!\d)',

    # ===== 车辆/社保 =====
    '车牌号': r'[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领警][A-Z][·]?[A-HJ-NP-Z0-9]{4,5}[A-HJ-NP-Z0-9挂学港澳]?',
    '社保卡号': r'(?<!\d)\d{14,18}(?!\d)',
    '医保卡号': r'(?<!\d)\d{10,18}(?!\d)',

    # ===== 医疗/公文 =====
    '病历号': r'(?:(?:BL|MR|EMR|MZ|ZY|门诊号?|住院号?|病历号?|病案号?)[::\-]?\d{4,}|[A-Z]{2,3}[-]?\d{6,12})',
    '公文份号': r'(?:(?:No|NO|Nr|No)[-:\s]*\d{4,}|份号[::\s]+\d+|\d{4,}[-]\d{4}[-]\d{4,}|第\d{2,4}[-]\d{4,}号|文件编号[::\s]*[A-Z]{2,3}[-_]\d{2,4}[-_]\d{3,})',
    '公文密级': r'(?:【[绝密机密秘密内部]+】|绝密\s*[★☆]?\s*\d*\s*年?|[机密秘密内部]+(?:文件|资料|通知|信息))',
    '公文文号': r'[\u4e00-\u9fa5]+发〔\d{4}〕\s*(?:第\s*)?\d+(?:号)?|[\u4e00-\u9fa5]*(?:政办发|发)〔\d{4}〕\s*(?:第\s*)?\d+号?|〔\d{4}〕(?:第?\s*\d+号?)',
}

# ===== 英文敏感信息正则 =====
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


def _mask_phone(m):
    p = m.group()
    digits = re.sub(r'\D', '', p)
    if len(digits) >= 7:
        return f"{digits[:3]}****{digits[-4:]}"
    return '****'


def _mask_email(m):
    e = m.group()
    parts = e.split('@')
    if len(parts) == 2:
        local = parts[0]
        if len(local) > 2:
            return f"{local[0]}***{local[-1]}@{parts[1]}"
        return f"***@{parts[1]}"
    return '***'


def _mask_id(m):
    c = m.group()
    if len(c) == 18:
        return f"{c[:4]}**********{c[-4:]}"
    return '*' * len(c)


def _mask_code(m):
    c = m.group()
    if len(c) <= 4:
        return '*' * len(c)
    half = len(c) // 2
    return f"{c[:half]}***{c[-half:]}"


def _mask_amount(m):
    return m.group()[:1] + '***'


MASK_FUNCTIONS = {
    '手机号': _mask_phone,
    '邮箱': _mask_email,
    '身份证': _mask_id,
    '银行卡': _mask_code,
    'IP地址': _mask_code,
    '社会信用代码': _mask_code,
    '营业执照号': _mask_code,
    '开户许可证号': _mask_code,
    '投标/成交价': _mask_amount,
    '合同编号': _mask_code,
    '采购/订单编号': _mask_code,
    '固定电话': _mask_phone,
    '传真号': lambda m: '***-********',
    '工号/学号': _mask_code,
    '项目代号': _mask_code,
    '邮编': lambda m: '******',
    # ===== 新增类型 =====
    '护照号': lambda m: m.group()[0] + '*' * (len(m.group()) - 2) + m.group()[-1],
    'Mac地址': lambda m: (':').join(m.group().split(':')[:1] + ['****'] + m.group().split(':')[-1:]),
    'IMEI': lambda m: m.group()[:6] + '******' + m.group()[-6:],
    '车牌号': lambda m: m.group()[:2] + '*' * (len(m.group()) - 2),
    '社保卡号': lambda m: m.group()[:4] + '*' * (len(m.group()) - 8) + m.group()[-4:],
    '医保卡号': lambda m: m.group()[:4] + '*' * (len(m.group()) - 6) + m.group()[-4:],
    '病历号': lambda m: re.sub(r'\d', '*', m.group()),
    '公文份号': lambda m: re.sub(r'\d', '*', m.group()),
    '公文密级': lambda m: '*' * len(m.group()),
    '公文文号': lambda m: re.sub(r'\d+(?=号)', lambda x: '*' * len(x.group()), m.group()),
}

# ===== 英文脱敏函数 =====
EN_MASK_FUNCTIONS = {
    'Phone': lambda m: re.sub(r'\d', '*', m.group()[:-4]) + m.group()[-4:],
    'Email': _mask_email,
    'SSN': lambda m: '***-**-' + m.group()[-4:],
    'Credit Card': lambda m: '****-****-****-' + re.sub(r'\D', '', m.group())[-4:],
    'IP Address': _mask_code,
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


def _sanitize_string(text, items):
    """对单个字符串应用脱敏正则"""
    result = text
    for item_name in items:
        if item_name in PATTERNS:
            pattern = PATTERNS[item_name]
            mask_fn = MASK_FUNCTIONS.get(item_name, _mask_code)
            result = re.sub(pattern, mask_fn, result)
        elif item_name in EN_PATTERNS:
            pattern = EN_PATTERNS[item_name]
            mask_fn = EN_MASK_FUNCTIONS.get(item_name, _mask_code)
            result = re.sub(pattern, mask_fn, result)
    return result


def _sanitize_value(value, items):
    """递归遍历数据结构，只对 string 值做脱敏"""
    if isinstance(value, str):
        return _sanitize_string(value, items)
    elif isinstance(value, dict):
        return {k: _sanitize_value(v, items) for k, v in value.items()}
    elif isinstance(value, list):
        return [_sanitize_value(item, items) for item in value]
    return value


# ===== JSON =====

def sanitize_json(text, items=None):
    """JSON 脱敏：解析 → 遍历 value → 脱敏 → 重新序列化"""
    if items is None:
        items = list(PATTERNS.keys()) + list(EN_PATTERNS.keys())
    try:
        obj = json.loads(text)
    except json.JSONDecodeError:
        # 非法 JSON，回退到文本脱敏
        return _sanitize_string(text, items), {}

    sanitized = _sanitize_value(obj, items)
    result = json.dumps(sanitized, ensure_ascii=False, indent=2)

    # 统计
    stats = {}
    for item_name in items:
        if item_name in PATTERNS:
            count = len(re.findall(PATTERNS[item_name], text))
            if count > 0:
                stats[item_name] = count

    return result, stats


# ===== CSV =====

def sanitize_csv(text, items=None):
    """CSV 脱敏：逐 cell 脱敏"""
    if items is None:
        items = list(PATTERNS.keys()) + list(EN_PATTERNS.keys())

    # 检测分隔符
    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff(text[:1024])
    except csv.Error:
        dialect = csv.excel

    reader = csv.reader(io.StringIO(text), dialect)
    rows = list(reader)

    stats = {}
    sanitized_rows = []
    for row in rows:
        new_row = []
        for cell in row:
            new_cell = _sanitize_string(cell, items)
            new_row.append(new_cell)
        sanitized_rows.append(new_row)

    output = io.StringIO()
    writer = csv.writer(output, dialect)
    writer.writerows(sanitized_rows)
    result = output.getvalue()

    # 统计
    for item_name in items:
        if item_name in PATTERNS:
            count = len(re.findall(PATTERNS[item_name], text))
            if count > 0:
                stats[item_name] = count

    return result, stats


# ===== XML =====

def sanitize_xml(text, items=None):
    """XML 脱敏：遍历 text 节点和属性"""
    if items is None:
        items = list(PATTERNS.keys()) + list(EN_PATTERNS.keys())

    try:
        # 注册常见命名空间避免 ns0 前缀
        namespaces = dict([node for _, node in ET.iterparse(io.StringIO(text), events=['start-ns'])])
        for prefix, uri in namespaces.items():
            if prefix:
                ET.register_namespace(prefix, uri)

        root = ET.fromstring(text)
    except ET.ParseError:
        return _sanitize_string(text, items), {}

    # 遍历所有元素
    for elem in root.iter():
        if elem.text and elem.text.strip():
            elem.text = _sanitize_string(elem.text, items)
        if elem.tail and elem.tail.strip():
            elem.tail = _sanitize_string(elem.tail, items)
        for attr_name in elem.attrib:
            elem.attrib[attr_name] = _sanitize_string(elem.attrib[attr_name], items)

    result = ET.tostring(root, encoding='unicode', xml_declaration=True)

    stats = {}
    for item_name in items:
        if item_name in PATTERNS:
            count = len(re.findall(PATTERNS[item_name], text))
            if count > 0:
                stats[item_name] = count

    return result, stats


# ===== YAML =====

def sanitize_yaml(text, items=None):
    """YAML 脱敏：解析 → 遍历 value → 脱敏 → 重新序列化"""
    if items is None:
        items = list(PATTERNS.keys()) + list(EN_PATTERNS.keys())

    try:
        import yaml
        data = yaml.safe_load(text)
    except Exception:
        return _sanitize_string(text, items), {}

    if data is None:
        return text, {}

    sanitized = _sanitize_value(data, items)
    result = yaml.dump(sanitized, allow_unicode=True, default_flow_style=False, sort_keys=False)

    stats = {}
    for item_name in items:
        if item_name in PATTERNS:
            count = len(re.findall(PATTERNS[item_name], text))
            if count > 0:
                stats[item_name] = count

    return result, stats


# ===== 统一入口 =====

FORMAT_HANDLERS = {
    '.json': sanitize_json,
    '.xml': sanitize_xml,
    '.html': sanitize_xml,  # HTML 当 XML 处理（容错）
    '.htm': sanitize_xml,
    '.yaml': sanitize_yaml,
    '.yml': sanitize_yaml,
    '.csv': sanitize_csv,
}


def sanitize_structured(text, ext, items=None):
    """
    结构化格式脱敏统一入口。
    返回 (result_text, stats_dict)
    """
    handler = FORMAT_HANDLERS.get(ext.lower())
    if handler:
        return handler(text, items)
    # 不支持的格式，回退到文本脱敏
    return _sanitize_string(text, items or list(PATTERNS.keys()) + list(EN_PATTERNS.keys())), {}
