# -*- coding: utf-8 -*-
import sys, os, json
sys.path.insert(0, r"C:\Users\26112\Desktop\SafeShrink")
from struct_sanitizer import sanitize_structured

# Test with correct CN pattern names
data = json.dumps({"name": "Zhang San", "phone": "13800138000"}, ensure_ascii=False)
r = sanitize_structured(data, ".json", ["手机号"])
print("JSON with 手机号:", r[0])

# Test with wrong pattern name
r2 = sanitize_structured(data, ".json", ["phone"])
print("JSON with phone:", r2[0])

# Test with no items
r3 = sanitize_structured(data, ".json")
print("JSON no items:", r3[0])
