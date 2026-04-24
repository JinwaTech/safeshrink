# SafeShrink 密小件

> 一键文档减肥、脱敏、Markdown转换，完全离线，保护隐私

**版本：v1.0.0** | [GitHub](https://github.com/yourname/safeshrink) · [下载 EXE](https://github.com/yourname/safeshrink/releases)

---

## ✨ 核心功能

| 功能 | 说明 | 效果 |
|------|------|------|
| 🗜️ **文档减肥** | 压缩文档体积，去除冗余内容 | 体积减少 **30%-70%** |
| 🔒 **智能脱敏** | 自动识别并脱敏敏感信息 | 支持 10+ 种敏感类型 |
| 📝 **Markdown 转换** | Office/PDF → Markdown | Token 消耗降低 **40%-60%** |
| 📦 **批量处理** | 文件夹一键批量处理 | 4 线程并行，智能跳过 |

---

## 💰 使用效果

### 📉 Token 节省对比

| 文档类型 | 原始 Token | 转换后 Token | 节省 | 相当于省钱* |
|----------|-----------|-------------|------|------------|
| 合同.docx (5页) | 3,200 | 1,800 | **44%** | ¥0.14 |
| 报告.pptx (20页) | 8,500 | 4,200 | **51%** | ¥0.43 |
| 手册.pdf (50页) | 15,000 | 7,500 | **50%** | ¥0.75 |
| 含图片文档 | 12,000 (含图片) | 5,500 | **54%** | ¥0.65 |

*按 GPT-4o 价格 ¥0.10/1K tokens 计算

### 🖼️ 转换效果示例

**文档减肥前后对比：**
```
📄 原始文档.docx     2.4 MB
📄 减肥后.docx       0.8 MB  ↓ 67%
```

**Markdown 转换效果：**
```
📄 合同.docx  →  📄 合同.md
- 文字：完整保留
- 表格：转为 Markdown 表格
- 图片：自动 Base64 内嵌（可选压缩）
- 格式：去除冗余样式，LLM 更易读
```

**智能脱敏效果：**
```
原文：
联系人：张三，电话：13812345678，报价：500万元

脱敏后：
联系人：张*，电话：138****5678，报价：***
```

---

## 🔐 脱敏范围

| 类型 | 示例 | 脱敏结果 |
|------|------|----------|
| 手机号 | `13812345678` | `138****5678` |
| 邮箱 | `test@example.com` | `te***@example.com` |
| 身份证 | `110101199001011234` | `110***********1234` |
| 银行卡 | `6222021234567890123` | `622202******0123` |
| IP地址 | `192.168.1.1` | `***.***.***.***` |
| 金额 | `500万元`、`87.81亿元` | `***` |
| 自定义 | 任意关键词 | 手动配置 |

---

## 📖 使用场景

### 💼 企业合规
批量处理合同，脱敏敏感信息后再分享给外部团队

```
📂 /客户资料/
   ├─ 合同A.docx     →  合同A_脱敏.md
   ├─ 合同B.pdf      →  合同B_脱敏.md
   └─ 报价单.xlsx    →  报价单_脱敏.md
```

### 📚 知识库建设
将 Office 文档转为 Markdown，降低 AI 知识库成本

```
📂 /产品文档/
   ├─ 演示文稿.pptx   →  演示文稿.md（嵌入图片）
   └─ 技术文档.docx   →  技术文档.md（嵌入图片）
```

### 💾 存储优化
压缩历史文档，节省存储空间

```
📂 /资料库/ (1.2GB)
   ↓ [批量减肥]
📂 /资料库_output/ (380MB)  节省 68%
```

---

## 🚀 快速开始

### 方式一：SkillHub 安装（推荐）

```bash
# 安装 SafeShrink Skill
skillhub install safeshrink

# 查看帮助
safeshrink --help
```

### 方式二：下载 EXE

```bash
# 下载 Windows 可执行文件
https://github.com/yourname/safeshrink/releases
```

### 方式三：源码运行

```bash
# 克隆仓库
git clone https://github.com/yourname/safeshrink.git
cd safeshrink

# 安装依赖
pip install -r requirements.txt

# 启动 GUI
python start_gui.py
```

---

## ⌨️ CLI 使用指南

### 文档减肥

```bash
# 单文件减肥
safeshrink slim input.docx -o output.docx

# 批量减肥（保留原文件，输出到 output 文件夹）
safeshrink slim ./docs --batch -o ./docs_slim

# 指定压缩强度（0.1-0.9，默认 0.3）
safeshrink slim input.docx --strength 0.5

# 同时去除 AI 生成标记
safeshrink slim input.docx --remove-ai
```

### 智能脱敏

```bash
# 单文件脱敏
safeshrink sanitize input.docx -o output.md

# 批量脱敏
safeshrink sanitize ./contracts --batch -o ./contracts_clean

# 指定脱敏类型
safeshrink sanitize input.docx --items phone,email,idcard

# 添加自定义敏感词
safeshrink sanitize input.docx --words "公司名,内部代号"
```

### Markdown 转换

```bash
# DOCX 转 Markdown
safeshrink convert input.docx -o output.md

# 批量转换
safeshrink convert ./docs --batch -o ./docs_md

# 嵌入图片（Base64）
safeshrink convert input.docx --embed-images

# 转换时压缩图片
safeshrink convert input.docx --embed-images --compress-images
```

### 批量处理

```bash
# 递归处理子文件夹
safeshrink slim ./docs --batch --recursive

# 4 线程并行处理
safeshrink sanitize ./docs --batch --workers 4

# 生成处理报告
safeshrink slim ./docs --batch --report report.txt
```

### 高级选项

```bash
# 查看版本
safeshrink --version

# 详细日志
safeshrink slim input.docx -v

# 仅预览，不实际处理
safeshrink slim input.docx --dry-run

# 配置文件处理
safeshrink --config config.json slim input.docx
```

---

## 📋 支持格式

| 类型 | 格式 | 减肥 | 脱敏 | Markdown |
|------|------|:----:|:----:|:--------:|
| **Office** | .docx, .xlsx, .pptx | ✅ | ✅ | ✅ |
| **PDF** | .pdf | ✅ | ✅ | ✅ |
| **网页** | .html, .htm | ✅ | ✅ | ✅ |
| **文本** | .txt, .md, .json, .csv | ✅ | ✅ | — |
| **图片** | .jpg, .png, .gif, .webp | ✅ | — | — |
| **代码** | .js, .py, .ts, .css, .sql | ✅ | ✅ | ✅ |

---

## 🛡️ 产品准则

| 准则 | 说明 |
|------|------|
| 🔒 **完全离线** | 无需联网，数据不出本地 |
| 🚫 **零删除** | 保留原文件，输出到新文件夹 |
| 📁 **可回溯** | 处理报告记录所有操作 |
| ⚡ **高效并行** | 多线程批量处理 |

---

## 📊 性能指标

| 指标 | 数值 |
|------|------|
| 处理速度 | ~50 页/秒（文档减肥） |
| 批量并行 | 4 线程默认，可配置 |
| 内存占用 | < 200MB（常规文档） |
| 支持单文件 | 最大 500MB |

---

## 🤝 贡献与支持

- 🐛 [提交 Issue](https://github.com/yourname/safeshrink/issues)
- 💡 [功能建议](https://github.com/yourname/safeshrink/discussions)
- ⭐ [Star 支持](https://github.com/yourname/safeshrink)

---

## 📄 License

MIT License - 免费使用、修改、分发

---

<div align="center">

**SafeShrink 密小件 — 让文档更轻、更安全、更 AI 友好**

[GitHub](https://github.com/yourname/safeshrink) · [SkillHub](https://skillhub.com/skills/safeshrink) · [问题反馈](https://github.com/yourname/safeshrink/issues)

</div>
