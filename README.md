# SafeShrink 密小件

> 一键文档减肥、脱敏、Markdown转换，完全离线，保护隐私

**版本：v1.0.0**

---

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 🗜️ **文档减肥** | 压缩文档体积，去除冗余内容，保留结构 |
| 🔒 **智能脱敏** | 自动识别并脱敏手机号、身份证、银行卡、金额等 |
| 📝 **Markdown 转换** | DOCX/PPTX/XLSX/PDF → Markdown，图片自动 Base64 内嵌 |
| 📦 **批量处理** | 支持文件夹一键批量处理，智能跳过已处理文件 |

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

## 🔐 脱敏范围

| 类型 | 示例 |
|------|------|
| 手机号 | `13812345678` → `138****5678` |
| 邮箱 | `test@example.com` → `te***@example.com` |
| 身份证 | `110101199001011234` → `110***********1234` |
| 银行卡 | `6222021234567890123` → `622202******0123` |
| IP地址 | `192.168.1.1` → `***.***.***.***` |
| 金 额 | `500万元`、`87.81亿元`、`350,000` → `***` |
| 自定义 | 自定义敏感词手动添加 |

---

## 📖 使用场景

### 场景一：企业合规

批量处理合同文件夹，脱敏敏感信息后再分享

```
📂 /客户资料/
   ├─ 合同A.docx     →  合同A_脱敏.md
   ├─ 合同B.pdf      →  合同B_脱敏.md
   └─ 报价单.xlsx     →  报价单_脱敏.md
```

### 场景二：知识管理

将 Word/PPT 转为 Markdown，图片自动 Base64 内嵌，单文件即可分享

```
📂 /产品文档/
   ├─ 演示文稿.pptx   →  演示文稿.md（含嵌入图片）
   └─ 技术文档.docx   →  技术文档.md（含嵌入图片）
```

### 场景三：文档减肥

压缩文件夹中所有文档，减小存储体积

```
📂 /资料库/ (1.2GB)
   ↓ [批量减肥]
📂 /资料库_output/ (380MB)
   节省 68%
```

---

## 🛡️ 软件准则

| 准则 | 说明 |
|------|------|
| 🔒 **隐私优先** | 完全离线处理，数据不外传 |
| 🚫 **零删除** | 只压缩/脱敏，不删除原始内容 |
| 📁 **可回溯** | 保留原文件，输出到 output 文件夹 |
| ⚡ **批量高效** | 支持文件夹批量处理，智能跳过已处理文件 |

---

## 🚀 快速开始

### 下载 EXE（推荐）

```bash
# 下载 SafeShrink.exe，双击运行
https://github.com/yourname/safeshrink/releases
```

### 源码运行

```bash
# 克隆仓库
git clone https://github.com/yourname/safeshrink.git
cd safeshrink

# 安装依赖
pip install -r requirements.txt

# 启动
python start_gui.py
```

### SkillHub 安装

```bash
skillhub install safeshrink
```

---

## 📁 项目结构

```
SafeShrink/
├── safe_shrink.py           # 核心处理逻辑
├── safe_shrink_gui.py     # GUI 界面
├── batch_processor.py      # 批量处理引擎
├── batch_tab.py           # 批量处理 Tab
├── sanitize_markdown.py    # Markdown 脱敏（含金额检测）
├── format_to_markdown_v2.py  # Markdown 转换（含图片嵌入）
├── file_status.py          # 处理状态检测
├── sanitize_tab.py         # 脱敏 Tab
├── slim_tab.py            # 减肥 Tab
├── history_tab.py         # 历史记录 Tab
├── settings_tab.py        # 设置 Tab
├── theme_manager.py       # 主题管理
├── history_manager.py      # 历史记录管理
├── requirements.txt        # Python 依赖
├── main_window_v2.spec    # PyInstaller 配置
└── dist/                  # 打包后的 EXE
    └── SafeShrink.exe
```

---

## 🛠️ 技术栈

| 技术 | 用途 |
|------|------|
| Python 3.14 + PySide6 | GUI 界面 |
| MarkItDown | Markdown 转换 |
| pdfplumber / PyMuPDF | PDF 处理 |
| python-docx / openpyxl / python-pptx | Office 处理 |
| Pillow | 图片处理 |
| 正则表达式 | 敏感信息识别 |

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 License

MIT License - 免费使用、修改、分发

---

## 🔗 相关链接

- [GitHub 仓库](https://github.com/yourname/safeshrink)
- [SkillHub](https://skillhub.com/skills/safeshrink)
- [问题反馈](https://github.com/yourname/safeshrink/issues)

---

<div align="center">

**如果对你有帮助，欢迎 ⭐ Star 支持！**

</div>
