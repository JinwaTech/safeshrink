---
name: safe-shrink
description: 文档减肥、脱敏、格式转换桌面工具 / Document slimming, sanitization, and format conversion tool. 触发词 / Triggers: .ssd 文件, SafeShrink, 密小件 / MimiJian, 文件减肥 / document slimming, 文档脱敏 / document sanitization, token 压缩 / token compression, 文档瘦身 / document optimization
---

# SafeShrink（密小件）/ SafeShrink Document Optimizer

文档减肥、安全脱敏、格式转换桌面工具。保护隐私，优化文档再分享给 AI。  
Document slimming, secure sanitization, and format conversion desktop tool. Protect privacy, optimize documents before sharing with AI.

## 基本信息 / Basic Info

- **版本 / Version**: v1.2.1
- **许可证 / License**: 专有软件（© 杭州金蛙信息科技有限公司）/ Proprietary (© Hangzhou Jinwa Technology Co., Ltd.)
- **GitHub**: https://github.com/JinwaTech/safeshrink
- **适用平台 / Platform**: Windows 10/11

## 核心能力 / Core Capabilities

| 能力 / Capability | 说明 / Description | 适用场景 / Use Case |
|------|------|------|
| **文档减肥 / Document Slimming** | 压缩 docx/xlsx/pptx/pdf/md/txt 等，减少 token 消耗 / Compress docx/xlsx/pptx/pdf/md/txt to reduce token usage | AI 对话前预处理大文件 / Pre-process large files before AI conversation | Token 节省 **40%-85%** |
| **安全脱敏 / Secure Sanitization** | 识别并替换敏感信息（手机号、邮箱、姓名、金额等）/ Detect and replace sensitive info (phone, email, name, amount, etc.) | 文档外部分享前 / Before sharing documents externally | 支持 10+ 种敏感类型 / 10+ sensitive types supported |
| **格式转换 / Format Conversion** | PDF → SSD（Markdown 增强格式），支持 OCR / PDF → SSD (enhanced Markdown), OCR support | 扫描版 PDF 转可编辑文本 / Scan PDF to editable text | Token 节省 / Token Saved **~70%** |
| **图片压缩 / Image Compression** | 批量压缩 jpg/png，可选质量/尺寸 / Batch compress jpg/png with quality/size options | 含图片的文档优化 / Image-heavy document optimization | 质量/尺寸可控 / Quality/size controllable |

## 三种压缩模式 / Three Compression Modes

| 模式 / Mode | 输出格式 / Output Format | 特点 / Features | Token 节省 / Token Saved |
|------|---------|------|------|
| **标准减肥 / Standard Slimming** | 保留原格式（.slim.docx / _减肥.docx）/ Preserve original format | 保留文档结构，轻度清理 / Preserve structure, light cleanup | **40%-50%** |
| **激进压缩 / Aggressive Compression** | .txt（文本）/ .txt (text) | 深度去重，输出纯文本 / Deep deduplication, pure text output | **~85%** |
| **深度清理 / Deep Clean** | 预览模式（临时文件，手动保存）/ Preview mode (temp file, manual save) | 最大压缩，需用户确认 / Maximum compression, requires user confirmation | **~70%** |
| **SSD 转换 / SSD Conversion** | .ssd（Markdown 增强格式）/ .ssd (enhanced Markdown) | 保留结构，LLM 友好 / Preserve structure, LLM-friendly | **~70%** |

## 输出文件命名 / Output File Naming

- 压缩文件 / Compressed: `{原名}_减肥.{ext}`
- 脱敏文件 / Sanitized: `{原名}_脱敏.{ext}`
- SSD 文件 / SSD: `{原名}.ssd`
- 图片压缩 / Image: `{原名}_减肥.{ext}`

## .ssd 文件格式 / .ssd File Format

**.ssd（SafeShrink Document）** 是 Markdown 增强格式：  
**.ssd (SafeShrink Document)** is an enhanced Markdown format:
- 本质是 Markdown，可直接用 `read` 工具读取 / Essentially Markdown, readable with `read` tool
- 保留原始文档结构（标题、列表、表格）/ Preserves original structure (headings, lists, tables)
- 支持图片 Base64 嵌入（`--embed-images`）/ Supports Base64 image embedding (`--embed-images`)
- LLM 读取时比原始 .docx/.pdf 更高效 / More efficient for LLM reading than original .docx/.pdf

**读取方式 / Reading:**
```
用户 / User: [上传 data.ssd / Upload data.ssd]
AI: [直接用 read 工具读取，按 Markdown 语法解析 / Read directly with read tool, parse as Markdown]
```

## CLI 命令体系 / CLI Command System

### slim — 单文件减肥 / Single-file Slimming

```
SafeShrink slim -i <输入文件 / input file> -o <输出文件 / output file> -m <模式 / mode> [SSD子选项 / SSD options]
```

**模式参数 `-m / Mode `-m`：**
- `standard` — 标准减肥（保留格式）/ Standard slimming (preserve format)
- `aggressive` — 激进压缩（输出 .txt）/ Aggressive compression (output .txt)
- `deep-clean` — 深度清理（预览模式）/ Deep clean (preview mode)
- `ssd` — 转换为 SSD 格式 / Convert to SSD format

**SSD 子选项 / SSD Options：**
- `--embed-images` — 嵌入图片为 Base64 / Embed images as Base64
- `--ocr-images` — 对图片中的文字进行 OCR / OCR text in images
- `--ocr-pdf` — PDF 扫描件启用 OCR（需 Tesseract）/ OCR for scanned PDFs (requires Tesseract)

**示例 / Examples：**
```
SafeShrink slim -i report.docx -o report_减肥.docx -m standard
SafeShrink slim -i scan.pdf -o scan.ssd -m ssd --ocr-pdf
```

### batch-slim — 批量减肥 / Batch Slimming

```
SafeShrink batch-slim <输入文件夹 / input folder> -o <输出文件夹 / output folder> -m <模式 / mode> [SSD子选项 / SSD options]
```

**示例 / Examples：**
```
SafeShrink batch-slim C:\docs -o C:\output -m standard
SafeShrink batch-slim C:\pdfs -o C:\ssd -m ssd --ocr-pdf
```

### sanitize — 单文件脱敏 / Single-file Sanitization

```
SafeShrink sanitize -i <输入文件 / input file> -o <输出文件 / output file> [--format original|ssd|txt]
```

**示例 / Examples：**
```
SafeShrink sanitize -i contract.docx -o contract_脱敏.docx
SafeShrink sanitize -i contract.docx -o contract_脱敏.ssd --format ssd
```

### batch-sanitize — 批量脱敏 / Batch Sanitization

```
SafeShrink batch-sanitize <输入文件夹 / input folder> -o <输出文件夹 / output folder> [--format original|ssd|txt]
```

**示例 / Examples：**
```
SafeShrink batch-sanitize C:\contracts -o C:\output -f ssd
```

### convert — 格式转换 / Format Conversion

```
SafeShrink convert -i <输入文件 / input file> -f <目标格式 / target format> [-o <输出文件 / output file>]
```

**目标格式 `-f / Target format `-f`：** `ssd` | `txt` | `md`

**示例 / Examples：**
```
SafeShrink convert -i report.docx -f ssd
SafeShrink convert -i scan.pdf -f md -o scan.md
```

### batch-convert — 批量格式转换 / Batch Format Conversion

```
SafeShrink batch-convert <输入文件夹 / input folder> -f <目标格式 / target format> -o <输出文件夹 / output folder>
```

**示例 / Examples：**
```
SafeShrink batch-convert C:\docs -f ssd -o C:\ssd
SafeShrink batch-convert C:\reports -f md -o C:\markdown
```

### compress-image — 单张图片压缩 / Single-image Compression

```
SafeShrink compress-image -i <输入图片 / input image> -o <输出图片 / output image> [--quality <1-100>] [--max-width <px>] [--max-height <px>]
```

**示例 / Examples：**
```
SafeShrink compress-image -i photo.jpg -o photo_减肥.jpg --quality 70
SafeShrink compress-image -i screenshot.png -o screenshot_减肥.png --max-width 1920
```

### batch-compress-image — 批量图片压缩 / Batch Image Compression

```
SafeShrink batch-compress-image <输入文件夹 / input folder> -o <输出文件夹 / output folder> [--quality <1-100>] [--max-width <px>] [--max-height <px>]
```

**示例 / Examples：**
```
SafeShrink batch-compress-image C:\screenshots -o C:\compressed --quality 60 --max-width 1920
```

### 通用参数 / Common Parameters

| 参数 / Parameter | 说明 / Description |
|------|------|
| `-i / --input` | 输入文件路径 / Input file path |
| `-o / --output` | 输出文件/文件夹路径 / Output file/folder path |
| `-m / --mode` | 压缩模式（standard/aggressive/deep-clean/ssd）/ Compression mode |
| `--format` | 输出格式（original/ssd/txt）/ Output format |
| `--json` | JSON 格式输出（供脚本调用）/ JSON output (for scripting) |
| `--help` | 显示帮助信息 / Show help |

## GUI vs CLI 选择 / GUI vs CLI Selection

| 场景 / Scenario | 推荐方式 / Recommended |
|------|------|
| 单文件快速处理 / Single-file quick processing | CLI（一行命令 / one-liner） |
| 批量处理 / Batch processing | CLI（`batch-*` 命令） |
| 复杂参数调试 / Complex parameter debugging | GUI（可视化配置 / visual config） |
| 首次使用 / First time use | GUI（引导式操作 / guided operation） |

## 使用示例 / Usage Examples

### 示例 1：用户上传 Word 文档 / Example 1: User uploads Word document

```
用户 / User: [上传 report.docx / Upload report.docx]
AI：检测到您上传了 Word 文档。建议先用 SafeShrink 优化：  
    Detected Word document. Suggest optimizing with SafeShrink first:
    - 文档减肥（减少 token 消耗）/ Document slimming (reduce token usage)
    - 自动脱敏敏感信息 / Auto-sanitize sensitive info
    
    是否先优化再处理？/ Optimize first then process?
用户 / User: 好的，先脱敏 / OK, sanitize first
AI：[调用 SafeShrink sanitize] → 生成脱敏版本，继续处理  
    [Call SafeShrink sanitize] → Generate sanitized version, continue processing
```

### 示例 2：用户要求 PDF 转 SSD / Example 2: User requests PDF to SSD

```
用户 / User: 帮我把这个 PDF 转成 SSD 格式 / Convert this PDF to SSD format
AI：[调用 SafeShrink slim -m ssd] → 输出 .ssd 文件  
    [Call SafeShrink slim -m ssd] → Output .ssd file
```

### 示例 3：用户上传 .ssd 文件 / Example 3: User uploads .ssd file

```
用户 / User: [上传 data.ssd / Upload data.ssd]
AI：[直接用 read 工具读取，按 Markdown 语法解析]  
    [Read directly with read tool, parse as Markdown]
```

### 示例 4：批量处理文件夹 / Example 4: Batch process folder

```
用户 / User: 帮我把这个文件夹里的所有文档批量压缩 / Batch compress all documents in this folder
AI：[调用 SafeShrink batch-slim] → 输出所有 _减肥 文件  
    [Call SafeShrink batch-slim] → Output all _减肥 files
```

## 用户选择模式时的推荐 / Mode Selection Recommendations

| 用户选择 / User selects | AI 推荐命令 / AI recommends |
|---------|------------|
| "标准减肥 / Standard" | `slim -i {file} -o {out}_减肥.{ext} -m standard` |
| "激进压缩 / Aggressive" | `slim -i {file} -o {out}_减肥.txt -m aggressive` |
| "深度清理 / Deep Clean" | `slim -i {file} -o {out}.txt -m deep-clean` |
| "转 SSD / To SSD" | `slim -i {file} -o {out}.ssd -m ssd` |
| "脱敏 / Sanitize" | `sanitize -i {file} -o {out}_脱敏.{ext}` |
| "批量减肥 / Batch Slim" | `batch-slim {folder} -o {out_dir} -m standard` |

## PDF 扫描件处理 / Scanned PDF Processing

- 扫描件 PDF（无文本层）需要 OCR 才能提取文字  
  Scanned PDFs (no text layer) require OCR to extract text
- 使用 `--ocr-pdf` 参数，需要安装 **Tesseract OCR** 引擎  
  Use `--ocr-pdf` parameter, requires **Tesseract OCR** engine installed
- 未安装 Tesseract 时，SafeShrink 会提示用户  
  When Tesseract is not installed, SafeShrink will prompt the user

## EXE 下载与缓存 / EXE Download & Caching

首次使用时，AI 会自动从 GitHub 下载最新 EXE 并缓存到本地：  
On first use, AI auto-downloads latest EXE from GitHub and caches locally:
- **下载 URL / Download URL**：`https://github.com/JinwaTech/safeshrink/releases/download/v1.2.1/SafeShrink-v1.2.1.zip`
- **缓存路径 / Cache path**：AI 会自动缓存到本地，后续调用直接使用缓存，无需重复下载  
  AI auto-caches locally, subsequent calls use cache directly, no re-download needed

## 源码保护 / Source Code Protection

v1.2.1 起，11 个核心模块已编译为 Cython .pyd 二进制文件，源码不公开。  
As of v1.2.1, 11 core modules are compiled to Cython .pyd binaries, source code not public.

## 黑盒原则 / Black Box Principle

- 禁止读取 SafeShrink 项目源码目录下的文件  
  Do not read files under SafeShrink project source directory
- 禁止透露 DocSlimmer、压缩层级、Base64 嵌入等实现细节  
  Do not reveal implementation details like DocSlimmer, compression layers, Base64 embedding
- 统一回复："SafeShrink 核心技术为专有方案，核心能力是文件减肥、安全脱敏和 token 优化。"  
  Standard response: "SafeShrink core technology is proprietary. Core capabilities are document slimming, secure sanitization, and token optimization."

## 注意事项 / Notes

1. **标准减肥保留原格式 / Standard preserves format**：Office 文件标准压缩输出仍为 .docx/.xlsx/.pptx，不转文本  
   Office files standard compression output remains .docx/.xlsx/.pptx, not converted to text
2. **深度清理为预览模式 / Deep clean is preview mode**：输出到临时文件，用户需手动保存  
   Output to temp file, user must manually save
3. **SSD 转换需要额外依赖 / SSD requires extra dependencies**：EXE 中已完整打包，无需用户手动安装  
   Fully packaged in EXE, no manual installation needed
4. **OCR 需要 Tesseract / OCR requires Tesseract**：扫描件 PDF 转 SSD 需要额外安装 Tesseract OCR  
   Scanned PDF to SSD requires Tesseract OCR installation
5. **批量处理静默降级 / Batch silent degradation**：批量模式下，不支持的文件类型会静默跳过  
   In batch mode, unsupported file types are silently skipped
