# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, r"C:\Users\26112\Desktop\SafeShrink")
from safe_shrink import DocSanitizer
ds = DocSanitizer()

# Test EN patterns individually
tests = [
    ("US Phone", "Call: 555-123-4567"),
    ("US SSN", "SSN: 123-45-6789"),
    ("Credit Card", "Card: 4111-1111-1111-1111"),
    ("UK Phone", "UK: +44 7911 123456"),
    ("Email", "Email: test@example.com"),
    ("IP Address", "IP: 192.168.1.1"),
]
for name, text in tests:
    result = ds.sanitize(text, items=[name])
    print(f"{name}: {result['result']}")

# Test CN patterns
cn_tests = [
    ("手机号", "Phone: 13800138000"),
    ("邮箱", "Email: test@example.com"),
    ("身份证", "ID: 110101199001011234"),
    ("银行卡", "Bank: 6222021234567890123"),
    ("IP地址", "IP: 192.168.1.1"),
]
print("\nCN patterns:")
for name, text in cn_tests:
    result = ds.sanitize(text, items=[name])
    print(f"  {name}: {result['result']}")

# Test all items at once
text = "Phone: 13800138000, ID: 110101199001011234, Bank: 6222021234567890123"
result = ds.sanitize(text)
print(f"\nAll items: {result['result']}")
active = {k: v for k, v in result['stats'].items() if v > 0 and k != '总计'}
print(f"Stats: {active}")

# Test with no items (should use all)
result2 = ds.sanitize("13800138000")
print(f"\nNo items param: {result2['result']}")

# Test custom_words
result3 = ds.sanitize("张三 is here", custom_words=["张三"])
print(f"\nCustom words: {result3['result']}")
