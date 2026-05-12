# SafeShrink 密小件

> 一键文档减肥、脱敏、SSD转换，完全离线，保护隐私

**版本：v1.1.8**  *(2026-05-12)*

| 功能 | 说明 |
|------|------|
| 🗜️ **文档减肥** | 压缩文档体积，去除冗余内容，保留结构 |
| 🔒 **智能脱敏** | 自动识别并脱敏手机号、身份证、银行卡、金额等 |
| 📝 **SSD 转换** | DOCX/PPTX/XLSX/PDF → .ssd，图片自动 Base64 内嵌 |
| 📦 **批量处理** | 支持文件夹一键批量处理，智能跳过已处理文件 |
| 🖼️ **OCR 识别** | 扫描件 PDF / 图片自动 OCR，输出可搜索文本 |

---

## 更新日志

### v1.1.8（2026-05-12）
- **修复**：批量处理双弹窗 — 添加 `_batch_compare_shown` 标志拦截递归调用
- **修复**：`_processing_lock` finally 块确保所有退出路径解锁
- **修复**：批量处理卡死 — 移除 `setDaemon` + 新增 `terminate_worker` + closeEvent 任务检测
- **修复**：进程残留 — 托盘退出调用 cleanup + build 强制终止残留进程
- **UI 修复**：单文件/批量 SSD 选项中 "扫描为Markdown" → "扫描为SSD"（5处）
- **构建**：build.py v2 — `auto-discover_hiddenimports()` 自动扫描本地模块（8个），无需手动维护
- **构建**：spec 文件恢复原始状态，由 build.py 处理 EXE 目录重命名

### v1.1.7（2026-05-10）
- **新增**：单文件 PDF OCR — `chk_ocr_pdf` 复选框，SSD 模式下显示
- **新增**：批量 PDF OCR — `batch_processor.py` / `batch_tab.py` 支持 `ocr_pdf` 参数
- **新增**：`is_scanned_pdf()` 智能检测扫描件，`ocr_pdf_pages()` 逐页 OCR 渲染

### v1.1.6（2026-05-09）
- **修复**：尺寸限制区域布局 — 重构输入框布局，增加间距，避免被上方区域压住
- **新增**：QSpinBox:disabled 样式，确保禁用状态下仍可见

### v1.1.5（2026-05-09）
- **修复**：选"扫描为SSD"后跳回"文件减肥"页面 — 彻底移除 `_on_img_format_changed` 中对 `format_combo` 的操作
- **新增**：build.py 自动同步 EXE 到桌面

### v1.1.4（2026-05-09）
- **新增**：图片模式 OCR — Tesseract v5.4.0 集成（chi_sim+eng），用户选择"扫描为SSD"时自动 OCR
- **新增**：`img_format_combo` 两选项（"图片压缩" / "扫描为SSD"）
- **修复**：`subprocess.run()` 添加 startupinfo 隐藏 Tesseract 黑窗口

### v1.1.3（2026-05-08）
- **新增**：批量处理 Tab — 多线程并行、图片 OCR 预处理
- **修复**：SSD 转换默认 `embed_images=False`，避免 PPTX 多图文件 token 暴涨
- **修复**：slider_frame 变量名错误、modes 列表不匹配

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
   ├─ 合同A.docx     →  合同A_脱敏.ssd
   ├─ 合同B.pdf      →  合同B_脱敏.ssd
   └─ 报价单.xlsx     →  报价单_脱敏.ssd
```

### 场景二：知识管理

将 Word/PPT 转为 SSD 格式，图片自动 Base64 内嵌，单文件即可分享

```
📂 /产品文档/
   ├─ 演示文稿.pptx   →  演示文稿.ssd（含嵌入图片）
   └─ 技术文档.docx   →  技术文档.ssd（含嵌入图片）
```

### 场景三：扫描件 OCR

对扫描件 PDF 进行 OCR，输出可搜索的文本

```
📄 扫描合同.pdf  →  📄 扫描合同.ssd（文字可搜索）
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
https://github.com/JinwaTech/safeshrink/releases
```

### 源码运行

```bash
# 克隆仓库
git clone https://github.com/JinwaTech/safeshrink.git
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
├── main_window_v2.py      # 主窗口、UI 布局
├── slim_tab.py            # 文档减肥 Tab（支持图片 OCR）
├── sanitize_tab.py        # 脱敏 Tab
├── batch_tab.py           # 批量处理 Tab（多线程并行）
├── safe_shrink.py         # 核心逻辑（CLI/模块）
├── safe_shrink_gui.py     # GUI 辅助逻辑
├── format_to_ssd.py       # SSD 格式转换实现（含 OCR 预处理）
├── batch_processor.py     # 批量处理引擎
├── settings_tab.py        # 设置 Tab
├── theme_manager.py       # 主题管理
├── history_manager.py     # 历史记录管理
├── file_status.py         # 处理状态检测
├── _ooxml_to_ssd.py       # Office 降级后备方案
├── main_window_v2.spec    # PyInstaller spec
├── build.py               # 构建脚本（auto-discover hiddenimports）
└── requirements.txt       # Python 依赖
```

---

## 🛠️ 技术栈

| 技术 | 用途 |
|------|------|
| Python 3.14 + PySide6（LGPL）| GUI 界面 |
| pypdf / pdfplumber / PyMuPDF | PDF 处理 |
| python-docx / openpyxl / python-pptx | Office 处理 |
| pdfminer.six | PDF 文本提取 |
| Pillow | 图片处理 |
| Tesseract v5.4.0（chi_sim+chi_tra+eng）| OCR 引擎 |
| 正则表达式 | 敏感信息识别 |

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 License

MIT-0 License — 免费使用、修改、分发，无需署名

---

## 🔗 相关链接

- [GitHub 仓库](https://github.com/JinwaTech/safeshrink)
- [SkillHub](https://skillhub.com/skills/safeshrink)
- [问题反馈](https://github.com/JinwaTech/safeshrink/issues)

---

<div align="center">

**如果对你有帮助，欢迎 ⭐ Star 支持！**

</div>