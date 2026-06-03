# -*- coding: utf-8 -*-
import sys, os, json
sys.path.insert(0, r"C:\Users\26112\Desktop\SafeShrink")
from struct_sanitizer import sanitize_structured

# Test JSON
data = json.dumps({"name": "Zhang San", "phone": "13800138000", "email": "test@example.com"}, ensure_ascii=False)
r = sanitize_structured(data, ".json", ["phone"])
print("JSON:", r)

# Test XML
xml = "<root><name>Zhang San</name><phone>13800138000</phone></root>"
r = sanitize_structured(xml, ".xml", ["phone"])
print("XML:", r)

# Test CSV
csv = "name,phone\nZhang San,13800138000\nLi Si,13900139000"
r = sanitize_structured(csv, ".csv", ["phone"])
print("CSV:", r)

# Test YAML
yaml = "name: Zhang San\nphone: 13800138000"
r = sanitize_structured(yaml, ".yaml", ["phone"])
print("YAML:", r)

# Test unsupported ext
r = sanitize_structured("hello", ".txt", ["phone"])
print("TXT:", r)

# Test with no items
r = sanitize_structured(data, ".json")
print("No items:", r)

# Check function signature
import inspect
print("\nsanitize_structured sig:", inspect.signature(sanitize_structured))
