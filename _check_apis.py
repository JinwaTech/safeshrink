# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Check DocSanitizer
from safe_shrink import DocSanitizer, estimate_tokens, get_lang

print("=== CN PATTERNS ===")
for k in DocSanitizer.PATTERNS.keys():
    print(f"  {k}")

print("\n=== EN PATTERNS ===")
if hasattr(DocSanitizer, "EN_PATTERNS"):
    for k in DocSanitizer.EN_PATTERNS.keys():
        print(f"  {k}")

print("\n=== estimate_tokens ===")
r = estimate_tokens("Hello world")
print(f"  EN: {r}")
r2 = estimate_tokens("x" * 100)
print(f"  100 chars: {r2}")

print("\n=== get_lang ===")
print(f"  CN: {get_lang(chr(20320)+chr(22909))}")
print(f"  EN: {get_lang('Hello world')}")

print("\n=== DocSanitizer.sanitize ===")
ds = DocSanitizer()
text = "Phone: 13800138000, Email: test@example.com"
result = ds.sanitize(text, ["phone", "email"])
print(f"  Input:  {text}")
print(f"  Output: {result}")

print("\n=== StructSanitizer ===")
from struct_sanitizer import sanitize_structured
import json
data = json.dumps({"name": "张三", "phone": "13800138000"}, ensure_ascii=False)
r = sanitize_structured(data, ".json", ["phone"])
print(f"  JSON input:  {data}")
print(f"  JSON output: {r}")
