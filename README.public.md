# SafeShrink 密小件

> 一键文档减肥、脱敏、SSD转换，完全离线，保护隐私

**版本：v1.1.8** | [GitHub](https://github.com/JinwaTech/safeshrink) · [下载 EXE](https://github.com/JinwaTech/safeshrink/releases/latest)

---

## ✨ 核心功能

| 功能 | 说明 | 效果 |
|------|------|------|
| 🗜️ **文档减肥** | 压缩文档体积，去除冗余内容 | 体积减少 **30%-70%** |
| 🔒 **智能脱敏** | 自动识别并脱敏敏感信息 | 支持 10+ 种敏感类型 |
| 📝 **SSD 转换** | Office/PDF → .ssd 格式 | Token 消耗降低 **40%-60%** |
| 📦 **批量处理** | 文件夹一键批量处理 | 多线程并行，智能跳过 |
| 🖼️ **OCR 识别** | 扫描件 PDF / 图片自动 OCR | 输出可搜索文本 |

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

### 📄 转换效果示例

**SSD 转换效果：**
```
📄 合同.docx  →  📄 合同.ssd
- 文字：完整保留
- 表格：转为 .ssd 表格格式
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
   ├─ 合同A.docx     →  合同A_脱敏.ssd
   ├─ 合同B.pdf      →  合同B_脱敏.ssd
   └─ 报价单.xlsx    →  报价单_脱敏.ssd
```

### 📚 知识库建设
将 Office 文档转为 .ssd 格式，降低 AI 知识库成本

```
📂 /产品文档/
   ├─ 演示文稿.pptx   →  演示文稿.ssd（嵌入图片）
   └─ 技术文档.docx   →  技术文档.ssd（嵌入图片）
```

### 🖼️ 扫描件 OCR
对扫描件 PDF 进行 OCR，输出可搜索文本

```
📄 扫描合同.pdf  →  📄 扫描合同.ssd（文字可搜索）
```

---

## 🚀 快速开始

### 方式一：下载 EXE（推荐）

前往 [GitHub Releases](https://github.com/JinwaTech/safeshrink/releases/latest) 下载 `SafeShrink.exe`，双击运行，无需安装。

### 方式二：SkillHub 安装

```bash
# 安装 SafeShrink Skill
skillhub install safeshrink
```

### 方式三：源码运行

```bash
git clone https://github.com/JinwaTech/safeshrink.git
cd safeshrink
pip install -r requirements.txt
python start_gui.py
```

---

## 📋 支持格式

| 类型 | 格式 | 减肥 | 脱敏 | SSD |
|------|------|:----:|:----:|:--------:|
| **Office** | .docx, .xlsx, .pptx | ✅ | ✅ | ✅ |
| **PDF** | .pdf | ✅ | ✅ | ✅ |
| **网页** | .html, .htm | ✅ | ✅ | ✅ |
| **文本** | .txt, .ssd, .json, .csv | ✅ | ✅ | — |
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
| 批量并行 | 多线程默认，智能调度 |
| 内存占用 | < 200MB（常规文档） |
| 支持单文件 | 最大 500MB |
| OCR 支持 | 扫描件 PDF + 图片 |

---

## 🤝 贡献与支持

- 🐛 [提交 Issue](https://github.com/JinwaTech/safeshrink/issues)
- 💡 [功能建议](https://github.com/JinwaTech/safeshrink/discussions)
- ⭐ [Star 支持](https://github.com/JinwaTech/safeshrink)

---

## 📄 License

MIT-0 License — 免费使用、修改、分发，无需署名

---

<div align="center">

**SafeShrink 密小件 — 让文档更轻、更安全、更 AI 友好**

[GitHub](https://github.com/JinwaTech/safeshrink) · [下载 EXE](https://github.com/JinwaTech/safeshrink/releases/latest) · [问题反馈](https://github.com/JinwaTech/safeshrink/issues)

</div>