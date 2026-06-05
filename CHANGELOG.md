# SafeShrink Changelog

## [v1.2.4] - 2026-06-05

### Fixed
- 设置页标签不翻译（英文切回中文时 13 个标签仍显示英文）
- 导航栏不切换（apply_language 读实例属性而非类属性）
- "减肠"错别字（history_tab 筛选下拉框 + translations.py）
- CJK 字体渲染（CSS font-family 顺序）

### Changed
- spec 恢复 collect_submodules（EXE 18.4MB / dist 182MB）
- 8 个 .pyd 全部重编译
- format_to_ssd.py UTF-16 → UTF-8
- 构建环境 Python 3.14 → 3.13.13

### Links
- **GitHub Release**: https://github.com/JinwaTech/safeshrink/releases/tag/v1.2.4
- **完整打包**: SafeShrink-v1.2.4.zip（128MB，含 _internal 目录）
## [v1.2.1] - 2026-05-25

### 🛡️ 源码保护（重大变更）
- 11 个核心模块编译为 Cython .pyd 二进制文件，源码不再公开
- 删除 GitHub 历史版本（v1.0.0~v1.2.0），仅保留 v1.2.1 Release
- 本地 git 历史完整保留（524 个 commit），可随时回溯

### 🐛 已修复
- **单文档脱敏 [Errno 22] Invalid argument**：`load_file_content()` 未设置 `self._current_file_path`，导致重载 Excel 时路径无效
- **Cython 循环依赖**：`safe_shrink.py` 自引用导入导致编译失败，已删除冗余导入
- **版本号不一致**：源码硬编码 `v1.0.0` 已修正为 `v1.2.1`
- **主界面左下角版本号**：两处 `v0.9.0` 已修正为 `v1.2.1`
- **requirements.txt 严重滞后**：更新为 PySide6、PyMuPDF 等当前依赖

### 📦 依赖审计
- 删除 4 个已废弃包：pikepdf、doc2docx、chardet、tqdm
- 补充 17 个实际在用但未列出包：PyMuPDF、pypdfium2、onnxruntime、magika、markitdown、mammoth、cobble、beautifulsoup4、soupsieve、lxml、defusedxml、xlsxwriter、xlrd、numpy、protobuf、requests、click
- 修正 5 个版本偏差：PySide6 6.11.0→6.11.1、pypdf 6.9.2→6.12.1、MarkItDown 0.0.2→0.1.5、Pillow 12.1.1→12.2.0、charset-normalizer 3.4.1→3.4.7

### 📁 仓库清理
- 删除 44 个无关文件（测试文件、临时脚本、构建辅助脚本、备份文件、日志文件等）
- 删除内部文档（DESIGN.md、README.md）从 GitHub，仅保留在本地
- 公开文档重命名为 README.public.md（GitHub 自动识别）
- 仓库从 98 个文件减至 30 个

### 📄 新增文件
- `CHANGELOG.md`：版本变更日志
- `LICENSE`：MIT-0（Skill 包许可证）

### 🔧 技术细节
- Python 3.13 + PySide6 + Cython .pyd
- PyInstaller onedir 模式，EXE 21.67MB，_internal 目录 1575 文件
- markitdown 完整打包（`collect_all` + `collect_data_files`）
- markitdown → magika → onnxruntime 依赖链完整

### 📥 下载
- **GitHub Release**：https://github.com/JinwaTech/safeshrink/releases/tag/v1.2.1
- **完整打包**：SafeShrink-v1.2.1.zip（115MB，含 _internal 目录）

---

## [v1.2.0] - 2026-05-23

### 🐛 已修复
- **单文件状态残留**：切换模式后旧路径仍被命中，已清除 `deep_cleaned_path` 和 `compressed_path`
- **PPTX/XLSX 标准压缩报错**：`slim_native_pptx/xlsx` 缺少 `success` 键，临时文件路径污染源目录
- **批量减肥 `_减肥` 后缀缺失**：GBK→UTF-8 编码膨胀导致 `saved_bytes <= 0` 误判
- **模式切换状态泄漏**：`detect_file_type()` 未清除路径，`save_result()` 命中旧路径

### 🎨 改进
- 标准减肥压缩率阈值从 0.5 提升至 0.7
- 批量处理命名逻辑统一，图片压缩输出加 `_减肥` 后缀
- 压缩无效时不再复制原文件

### 📦 EXE 修复
- markitdown EXE 打包修复（`collect_all` + `collect_data_files`）
- PDF 扫描件误判为扫描件修复（空字符串绕过 NEEDS_OCR 检查）

---

## [v1.1.8] - 2026-05-14

### 🐛 已修复
- 批量处理弹窗重复 bug
- 单文件处理保留原格式
- 图片/Word 临时文件泄漏
- 日历导航栏箭头图标显示

### 📦 EXE
- EXE 18.70MB，Python 3.13 + PySide6
- markitdown 依赖链完整打包

---

## [v1.1.10] - 2026-05-22

### 🎨 图标修复
- S logo 居中（质心 123,121）
- 圆角 radius=42
- 乳白色背景扩展至画布边缘
- 7 种内嵌尺寸（16~256）

---

## [v1.1.11] - 2026-05-22

### 🎨 图标修复 v13
- 保持 logo 位置不变
- 背景向右下角扩展至画布边缘（留 2px 边距）
- 背景色硬编码 RGB(245,240,232)

---

[Unreleased]: https://github.com/JinwaTech/safeshrink/compare/v1.2.4...HEAD
[v1.2.4]: https://github.com/JinwaTech/safeshrink/releases/tag/v1.2.4
[v1.2.1]: https://github.com/JinwaTech/safeshrink/releases/tag/v1.2.1
[v1.2.0]: https://github.com/JinwaTech/safeshrink/releases/tag/v1.2.0
[v1.1.8]: https://github.com/JinwaTech/safeshrink/releases/tag/v1.1.8

