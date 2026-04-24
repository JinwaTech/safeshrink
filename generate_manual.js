/**
 * SafeShrink 操作手册生成脚本
 * 生成 Word 文档 (.docx)
 */

const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
        PageBreak, LevelFormat, Header, Footer, PageNumber } = require('docx');
const fs = require('fs');

// 页面边距 (DXA 单位, 1440 = 1 英寸)
const PAGE_MARGIN = 1440;

// 表格边框样式
const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

// 创建标题段落
function createTitle(text) {
    return new Paragraph({
        heading: HeadingLevel.HEADING_1,
        spacing: { before: 400, after: 200 },
        children: [new TextRun({ text, bold: true, size: 32, font: "微软雅黑" })]
    });
}

// 创建二级标题
function createHeading2(text) {
    return new Paragraph({
        heading: HeadingLevel.HEADING_2,
        spacing: { before: 300, after: 150 },
        children: [new TextRun({ text, bold: true, size: 28, font: "微软雅黑" })]
    });
}

// 创建三级标题
function createHeading3(text) {
    return new Paragraph({
        heading: HeadingLevel.HEADING_3,
        spacing: { before: 200, after: 100 },
        children: [new TextRun({ text, bold: true, size: 24, font: "微软雅黑" })]
    });
}

// 创建正文段落
function createPara(text, options = {}) {
    return new Paragraph({
        spacing: { before: 100, after: 100 },
        indent: options.indent ? { left: 360 } : undefined,
        children: [new TextRun({ text, size: 22, font: "微软雅黑", ...options })]
    });
}

// 创建代码块
function createCodeBlock(code) {
    const lines = code.split('\n');
    return lines.map(line => new Paragraph({
        spacing: { before: 0, after: 0 },
        shading: { fill: "F5F5F5", type: ShadingType.CLEAR },
        indent: { left: 360 },
        children: [new TextRun({ text: line || ' ', size: 20, font: "Consolas" })]
    }));
}

// 创建表格
function createTable(headers, rows) {
    const headerRow = new TableRow({
        children: headers.map(h => new TableCell({
            borders,
            shading: { fill: "E8E8E8", type: ShadingType.CLEAR },
            margins: { top: 80, bottom: 80, left: 120, right: 120 },
            children: [new Paragraph({
                alignment: AlignmentType.CENTER,
                children: [new TextRun({ text: h, bold: true, size: 22, font: "微软雅黑" })]
            })]
        }))
    });

    const dataRows = rows.map(row => new TableRow({
        children: row.map((cell, idx) => new TableCell({
            borders,
            margins: { top: 80, bottom: 80, left: 120, right: 120 },
            children: [new Paragraph({
                children: [new TextRun({ text: cell, size: 22, font: "微软雅黑" })]
            })]
        }))
    }));

    return new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: headers.map(() => Math.floor(9360 / headers.length)),
        rows: [headerRow, ...dataRows]
    });
}

// 创建列表项
function createListItem(text, level = 0) {
    return new Paragraph({
        spacing: { before: 60, after: 60 },
        indent: { left: 720 + level * 360 },
        children: [new TextRun({ text: `• ${text}`, size: 22, font: "微软雅黑" })]
    });
}

// 主文档
const doc = new Document({
    styles: {
        default: {
            document: {
                run: { font: "微软雅黑", size: 22 }
            }
        }
    },
    sections: [{
        properties: {
            page: {
                margin: { top: PAGE_MARGIN, right: PAGE_MARGIN, bottom: PAGE_MARGIN, left: PAGE_MARGIN }
            }
        },
        headers: {
            default: new Header({
                children: [new Paragraph({
                    alignment: AlignmentType.RIGHT,
                    children: [new TextRun({ text: "SafeShrink 操作手册 V1.0.0", size: 18, font: "微软雅黑", color: "666666" })]
                })]
            })
        },
        footers: {
            default: new Footer({
                children: [new Paragraph({
                    alignment: AlignmentType.CENTER,
                    children: [
                        new TextRun({ text: "第 ", size: 18, font: "微软雅黑" }),
                        new TextRun({ children: [PageNumber.CURRENT], size: 18, font: "微软雅黑" }),
                        new TextRun({ text: " 页", size: 18, font: "微软雅黑" })
                    ]
                })]
            })
        },
        children: [
            // ===== 封面 =====
            new Paragraph({ spacing: { before: 2000 } }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                children: [new TextRun({ text: "SafeShrink", bold: true, size: 72, font: "微软雅黑" })]
            }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { before: 200 },
                children: [new TextRun({ text: "（密小件）", size: 36, font: "微软雅黑" })]
            }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { before: 400 },
                children: [new TextRun({ text: "文档处理工具", size: 32, font: "微软雅黑" })]
            }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { before: 600 },
                children: [new TextRun({ text: "操作手册", bold: true, size: 48, font: "微软雅黑" })]
            }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { before: 800 },
                children: [new TextRun({ text: "版本 V2.1.0", size: 24, font: "微软雅黑", color: "666666" })]
            }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { before: 200 },
                children: [new TextRun({ text: "2026年4月", size: 24, font: "微软雅黑", color: "666666" })]
            }),
            new PageBreak(),

            // ===== 目录 =====
            createTitle("目 录"),
            createPara("一、软件概述 ................................................ 3"),
            createPara("二、系统要求 ................................................ 3"),
            createPara("三、安装与启动 .............................................. 3"),
            createPara("四、图形界面操作 ............................................ 4"),
            createPara("    4.1 文件减肥 ............................................ 4"),
            createPara("    4.2 文档脱敏 ............................................ 6"),
            createPara("    4.3 批量处理 ............................................ 8"),
            createPara("    4.4 处理历史 ............................................ 9"),
            createPara("    4.5 设置 ................................................ 10"),
            createPara("五、命令行操作（CLI/Skill模式） ............................. 12"),
            createPara("六、技术原理 ................................................ 14"),
            createPara("七、常见问题 ................................................ 15"),
            createPara("八、附录 .................................................... 16"),
            new PageBreak(),

            // ===== 一、软件概述 =====
            createTitle("一、软件概述"),
            createPara("SafeShrink（密小件）是一款面向AI大模型时代的智能文档处理工具，提供文档减肥、敏感信息脱敏、批量处理三大核心功能。"),
            createHeading2("1.1 主要功能"),
            createListItem("文档减肥：压缩文档体积，移除冗余内容，优化Token消耗"),
            createListItem("敏感信息脱敏：自动识别并脱敏26种常见敏感信息类型"),
            createListItem("批量处理：文件夹级别批量处理，支持多线程并发"),
            createListItem("Token估算：实时估算文档的Token消耗量"),
            createListItem("SSD格式转换：将复杂文档转换为优化后的Markdown结构"),
            createHeading2("1.2 支持格式"),
            createTable(
                ["类型", "格式"],
                [
                    ["文本文件", ".txt, .md, .json, .csv, .xml, .html, .log"],
                    ["Word文档", ".docx"],
                    ["Excel表格", ".xlsx, .xls"],
                    ["PowerPoint", ".pptx"],
                    ["PDF文档", ".pdf"],
                    ["图片文件", ".jpg, .jpeg, .png, .gif, .bmp, .webp"]
                ]
            ),
            new Paragraph({ spacing: { before: 200 } }),

            // ===== 二、系统要求 =====
            createTitle("二、系统要求"),
            createHeading2("2.1 硬件要求"),
            createListItem("处理器：Intel/AMD x64 处理器"),
            createListItem("内存：4GB 以上（推荐8GB）"),
            createListItem("磁盘：1GB 可用空间"),
            createHeading2("2.2 软件要求"),
            createListItem("操作系统：Windows 10/11（64位）"),
            createListItem("运行时：无需额外依赖，独立可执行程序"),

            // ===== 三、安装与启动 =====
            createTitle("三、安装与启动"),
            createHeading2("3.1 安装方式"),
            createPara("SafeShrink 为绿色软件，无需安装。将 SafeShrink.exe 放置到任意目录即可运行。"),
            createHeading2("3.2 启动方式"),
            createListItem("双击 SafeShrink.exe 启动图形界面"),
            createListItem("命令行模式：SafeShrink.exe <command> [options]"),
            createHeading2("3.3 首次运行"),
            createPara("首次运行时，软件会在 %APPDATA%\\SafeShrink 目录下创建配置文件 settings.json。"),

            // ===== 四、图形界面操作 =====
            createTitle("四、图形界面操作"),
            createPara("SafeShrink 采用现代化侧边栏导航布局，左侧为功能导航，右侧为内容区域。"),
            
            // 4.1 文件减肥
            createHeading2("4.1 文件减肥"),
            createPara("文件减肥功能可压缩文档体积，移除冗余内容，优化大模型Token消耗。"),
            createHeading3("4.1.1 支持的文件类型"),
            createListItem("文本文件：.txt, .md, .json, .csv, .xml, .html, .log"),
            createListItem("Word文档：.docx"),
            createListItem("图片文件：.jpg, .jpeg, .png, .gif, .bmp, .webp"),
            createHeading3("4.1.2 操作步骤"),
            createListItem("点击「选择文件...」按钮，选择要处理的文件"),
            createListItem("根据文件类型，选择处理选项："),
            createPara("文本文件选项：", { bold: true }),
            createListItem("标准压缩：基础文本压缩，保留结构", 1),
            createListItem("激进压缩：移除注释、空行等冗余内容", 1),
            createListItem("保留结构：只清理格式问题", 1),
            createListItem("转换为SSD：转换为SafeShrink Document格式", 1),
            createPara("图片文件选项：", { bold: true }),
            createListItem("压缩质量：调整JPEG/PNG压缩质量（1-100）", 1),
            createListItem("尺寸限制：设置最大宽高，超出自动缩放", 1),
            createListItem("保留元数据：是否保留EXIF等元数据", 1),
            createListItem("点击「开始处理」按钮执行处理"),
            createListItem("处理完成后可预览结果、保存文件或撤销操作"),
            createHeading3("4.1.3 Token估算"),
            createPara("软件会实时估算文档的Token消耗量，帮助用户了解优化效果。Token估算基于GPT系列模型的Tokenizer算法。"),

            // 4.2 文档脱敏
            createHeading2("4.2 文档脱敏"),
            createPara("文档脱敏功能可自动识别并脱敏文档中的敏感信息，保护隐私数据安全。"),
            createHeading3("4.2.1 支持的敏感信息类型"),
            createTable(
                ["分类", "类型"],
                [
                    ["个人信息", "手机号、邮箱、身份证、护照号、银行卡、社保卡号、医保号、病历号"],
                    ["企业信息", "营业执照号、社会信用代码、合同编号、投标/成交价"],
                    ["技术信息", "IP地址、Mac地址、IMEI、车牌号"],
                    ["公文信息", "公文份号、公文密级、公文文号"],
                    ["其他", "固定电话"]
                ]
            ),
            createHeading3("4.2.2 场景预设"),
            createPara("软件提供五大场景预设，一键应用专业脱敏配置："),
            createListItem("通用文档：覆盖常见的个人和企业敏感信息"),
            createListItem("党政公文：增加公文份号、密级、文号等公文专用字段"),
            createListItem("金融合同：增加合同编号、投标价等金融专用字段"),
            createListItem("医疗档案：增加病历号、医保号等医疗专用字段"),
            createListItem("教育材料：覆盖基本的个人和技术敏感信息"),
            createHeading3("4.2.3 脱敏模式"),
            createListItem("简单遮蔽：将敏感信息替换为 *** （如：138****8888）"),
            createListItem("语义标签：用语义标签替代（如：<PERSON_PHONE.1>），大模型能理解类型但看不到实际内容"),
            createHeading3("4.2.4 操作步骤"),
            createListItem("点击「选择文件...」按钮，选择要处理的文件"),
            createListItem("选择场景预设或手动勾选需要脱敏的类型"),
            createListItem("选择脱敏模式（简单遮蔽或语义标签）"),
            createListItem("点击「开始脱敏」按钮执行处理"),
            createListItem("处理完成后可查看脱敏结果、保存文件或撤销操作"),
            createHeading3("4.2.5 Office文档脱敏"),
            createPara("对于 .docx、.xlsx、.pptx 文件，软件采用原生格式处理，脱敏后保持原有格式不变，包括："),
            createListItem("字体、颜色、大小等文本格式"),
            createListItem("表格、图表等复杂结构"),
            createListItem("页眉、页脚、批注等内容"),

            // 4.3 批量处理
            createHeading2("4.3 批量处理"),
            createPara("批量处理功能支持对整个文件夹进行统一处理，大幅提升工作效率。"),
            createHeading3("4.3.1 操作步骤"),
            createListItem("点击「选择文件夹...」按钮，选择要处理的文件夹"),
            createListItem("选择处理类型：文件减肥 或 文档脱敏"),
            createListItem("配置处理选项（与单文件处理相同）"),
            createListItem("点击「开始处理」按钮执行批量处理"),
            createListItem("处理过程中可查看实时进度和结果"),
            createHeading3("4.3.2 高级选项"),
            createListItem("递归扫描：是否扫描子目录"),
            createListItem("并发数：设置并发处理线程数（1-16）"),
            createListItem("输出目录：指定输出文件夹"),
            createListItem("保留结构：保持原有目录结构"),
            createListItem("备份原文件：处理前自动备份"),

            // 4.4 处理历史
            createHeading2("4.4 处理历史"),
            createPara("处理历史功能记录所有处理操作，方便追踪和撤销。"),
            createHeading3("4.4.1 历史记录内容"),
            createListItem("操作时间"),
            createListItem("操作类型（减肥/脱敏）"),
            createListItem("源文件路径"),
            createListItem("处理结果统计"),
            createHeading3("4.4.2 历史操作"),
            createListItem("查看详情：查看完整的处理记录"),
            createListItem("撤销操作：恢复到处理前的状态"),
            createListItem("清空历史：清除所有历史记录"),

            // 4.5 设置
            createTitle("4.5 设置"),
            createPara("设置功能提供丰富的配置选项，满足个性化需求。"),
            createHeading3("4.5.1 通用设置"),
            createListItem("语言：简体中文 / English"),
            createListItem("主题：浅色 / 深色"),
            createListItem("启动时检查更新"),
            createListItem("最小化到系统托盘"),
            createListItem("退出时确认"),
            createHeading3("4.5.2 输出设置"),
            createListItem("默认输出目录"),
            createListItem("自动备份原文件"),
            createListItem("覆盖前确认"),
            createListItem("保留目录结构"),
            createListItem("输出文件添加时间戳"),
            createHeading3("4.5.3 处理设置"),
            createListItem("并发线程数"),
            createListItem("图片压缩质量"),
            createListItem("文本压缩强度"),
            createListItem("PDF质量"),
            createListItem("移除空行"),
            createListItem("移除空白段落"),
            createListItem("Word深度清理"),
            createHeading3("4.5.4 脱敏设置"),
            createListItem("默认脱敏类型：勾选需要默认应用的脱敏类型"),
            createListItem("遮蔽字符：设置遮蔽字符（默认为 *）"),
            createListItem("保留首尾字符：手机号、银行卡等保留首尾部分字符"),
            createListItem("默认脱敏模式：简单遮蔽 / 语义标签"),
            createHeading3("4.5.5 界面设置"),
            createListItem("字体大小"),
            createListItem("表格行高"),
            createListItem("显示结果对话框"),
            createListItem("显示处理详情"),
            createHeading3("4.5.6 高级设置"),
            createListItem("日志级别"),
            createListItem("日志文件最大大小"),
            createListItem("启用缓存"),
            createListItem("缓存大小限制"),

            // ===== 五、命令行操作 =====
            createTitle("五、命令行操作（CLI/Skill模式）"),
            createPara("SafeShrink 提供命令行接口，支持脚本调用和自动化集成。"),
            createHeading2("5.1 基本语法"),
            ...createCodeBlock("SafeShrink.exe <command> [options]"),
            createHeading2("5.2 命令列表"),
            createTable(
                ["命令", "说明"],
                [
                    ["slim", "文档减肥"],
                    ["sanitize", "文档脱敏"],
                    ["--help", "显示帮助信息"],
                    ["--version", "显示版本信息"]
                ]
            ),
            createHeading2("5.3 文件减肥命令"),
            createHeading3("语法"),
            ...createCodeBlock("SafeShrink.exe slim -i <input> -o <output> [options]"),
            createHeading3("参数说明"),
            createTable(
                ["参数", "说明", "示例"],
                [
                    ["-i, --input", "输入文件路径", "-i document.docx"],
                    ["-o, --output", "输出文件路径", "-o output.txt"],
                    ["--format", "输出格式 (txt/md/json)", "--format md"],
                    ["--json", "输出JSON格式结果", "--json"]
                ]
            ),
            createHeading3("示例"),
            ...createCodeBlock("# 压缩Word文档\nSafeShrink.exe slim -i report.docx -o report_slim.txt\n\n# JSON格式输出\nSafeShrink.exe slim -i data.json -o result.txt --json"),
            createHeading2("5.4 文档脱敏命令"),
            createHeading3("语法"),
            ...createCodeBlock("SafeShrink.exe sanitize -i <input> -o <output> [options]"),
            createHeading3("参数说明"),
            createTable(
                ["参数", "说明", "示例"],
                [
                    ["-i, --input", "输入文件路径", "-i document.docx"],
                    ["-o, --output", "输出文件路径", "-o sanitized.docx"],
                    ["--words", "自定义脱敏词（空格分隔）", "--words 张三 李四"],
                    ["--json", "输出JSON格式结果", "--json"]
                ]
            ),
            createHeading3("示例"),
            ...createCodeBlock("# 脱敏Word文档\nSafeShrink.exe sanitize -i contract.docx -o contract_sanitized.docx\n\n# 自定义脱敏词\nSafeShrink.exe sanitize -i report.pdf -o report_sanitized.pdf --words 张三 李四 王五\n\n# JSON格式输出\nSafeShrink.exe sanitize -i data.xlsx -o result.xlsx --json"),
            createHeading2("5.5 JSON输出格式"),
            createPara("使用 --json 参数时，输出为机器可读的JSON格式："),
            ...createCodeBlock('{\n  "success": true,\n  "action": "sanitize",\n  "input_file": "document.docx",\n  "output_path": "output/sanitized_document.docx",\n  "stats": {\n    "手机号": 5,\n    "邮箱": 3,\n    "身份证": 2\n  }\n}'),

            // ===== 六、技术原理 =====
            createTitle("六、技术原理"),
            createHeading2("6.1 敏感信息识别"),
            createPara("软件采用正则表达式引擎识别敏感信息，内置26种预设规则："),
            createListItem("手机号：匹配中国大陆11位手机号"),
            createListItem("邮箱：匹配标准邮箱格式"),
            createListItem("身份证：匹配18位身份证号码"),
            createListItem("银行卡：匹配16-19位银行卡号"),
            createListItem("IP地址：匹配IPv4地址格式"),
            createListItem("... 等"),
            createHeading2("6.2 Token估算"),
            createPara("Token估算基于GPT系列模型的Tokenizer算法（BPE编码），支持中英文混合文本。"),
            createHeading2("6.3 SSD格式"),
            createPara("SSD（SafeShrink Document）是软件独有的文档格式，特点："),
            createListItem("基于Markdown语法，兼容性好"),
            createListItem("优化Token消耗，适合大模型处理"),
            createListItem("支持内嵌图片（Base64编码）"),
            createListItem("保留文档结构信息"),

            // ===== 七、常见问题 =====
            createTitle("七、常见问题"),
            createHeading2("Q1: 处理后的文件保存在哪里？"),
            createPara("默认保存在源文件同目录，可在设置中修改默认输出目录。"),
            createHeading2("Q2: 如何撤销处理操作？"),
            createPara("在处理历史中选择对应记录，点击「撤销」按钮即可恢复。批量处理前会自动创建备份。"),
            createHeading2("Q3: 为什么某些敏感信息没有被识别？"),
            createPara("可能原因："),
            createListItem("未勾选对应的敏感信息类型"),
            createListItem("信息格式不符合预设规则"),
            createListItem("文档编码问题导致读取失败"),
            createPara("解决方案：检查设置中的脱敏类型勾选，或使用自定义脱敏词功能。"),
            createHeading2("Q4: 支持哪些Office版本？"),
            createPara("支持 Office 2007 及以上版本创建的 .docx/.xlsx/.pptx 文件。不支持旧版 .doc/.xls/.ppt 格式（需先转换）。"),
            createHeading2("Q5: 如何批量处理大量文件？"),
            createPara("使用批量处理功能，支持设置并发线程数（最大16线程），可显著提升处理速度。"),

            // ===== 八、附录 =====
            createTitle("八、附录"),
            createHeading2("8.1 敏感信息正则表达式规则"),
            createTable(
                ["类型", "规则说明"],
                [
                    ["手机号", "1[3-9]\\d{9}"],
                    ["邮箱", "标准邮箱格式"],
                    ["身份证", "\\d{17}[\\dXx]"],
                    ["银行卡", "\\d{16,19}"],
                    ["IP地址", "\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}\\.\\d{1,3}"],
                    ["护照号", "[GE]\\d{8}"],
                    ["Mac地址", "([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}"],
                    ["IMEI", "\\d{15}"],
                    ["车牌号", "[京津沪渝冀...][A-Z][A-Z0-9]{5,6}"],
                    ["社保卡号", "\\d{18}"],
                    ["社会信用代码", "[0-9A-HJ-NPQRTUWXY]{2}\\d{6}[0-9A-HJ-NPQRTUWXY]{10}"],
                    ["营业执照号", "\\d{15}"],
                    ["公文份号", "第[一二三四五六七八九十百千万]+份"],
                    ["公文密级", "绝密|机密|秘密"],
                    ["公文文号", "[\\u4e00-\\u9fa5]+〔\\d{4}〕\\d+号"]
                ]
            ),
            createHeading2("8.2 键盘快捷键"),
            createTable(
                ["快捷键", "功能"],
                [
                    ["Ctrl+O", "打开文件"],
                    ["Ctrl+S", "保存文件"],
                    ["Ctrl+Z", "撤销操作"],
                    ["F5", "刷新"],
                    ["F11", "全屏模式"],
                    ["Esc", "退出全屏/关闭对话框"]
                ]
            ),
            createHeading2("8.3 版本历史"),
            createTable(
                ["版本", "日期", "更新内容"],
                [
                    ["V1.0.0", "2026-03", "首次发布"]
                ]
            ),
            createHeading2("8.4 技术支持"),
            createPara("如遇问题，请联系技术支持并提供以下信息："),
            createListItem("软件版本号"),
            createListItem("操作系统版本"),
            createListItem("问题截图或错误信息"),
            createListItem("复现步骤"),

            // 结束
            new Paragraph({ spacing: { before: 400 } }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                children: [new TextRun({ text: "— 文档结束 —", size: 20, font: "微软雅黑", color: "999999" })]
            })
        ]
    }]
});

// 生成文档
Packer.toBuffer(doc).then(buffer => {
    fs.writeFileSync("SafeShrink_操作手册_V1.0.0.docx", buffer);
    console.log("操作手册已生成: SafeShrink_操作手册_V1.0.0.docx");
});
