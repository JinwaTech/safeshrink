# -*- coding: utf-8 -*-

"""

SafeShrink 批量处理模块 v2.1

==========================

支持文件夹批量处理，自动递归扫描、过滤、处理、输出汇总报告。

"""



import os

import sys

import json

import time

import traceback

from pathlib import Path

from datetime import datetime

from typing import List, Dict, Optional

from concurrent.futures import ThreadPoolExecutor, as_completed



# 导入主模块的类

try:

    from safe_shrink import DocSlimmer, DocSanitizer, read_file, DEPS

    HAS_CORE = True

except ImportError:

    HAS_CORE = False



# 导入文件状态检测模块

try:

    from file_status import FileStatusChecker, get_user_friendly_message

    HAS_STATUS_CHECKER = True

except ImportError:

    HAS_STATUS_CHECKER = False





# ========== 支持的文件格式 ==========



SUPPORTED_EXTENSIONS = {

    # 文本类

    '.txt', '.ssd', '.json', '.csv', '.xml', '.html', '.htm',

    '.log', '.ini', '.cfg', '.yaml', '.yml', '.js', '.ts', '.py', '.c', '.cpp', '.java',

    # Office类

    '.docx', '.xlsx', '.xls', '.pptx',

    # PDF

    '.pdf',

}





def scan_folder(folder_path: str, recursive: bool = True, max_depth: int = 10) -> List[Dict]:

    """

    扫描文件夹，返回所有支持的文件列表



    Returns:

        List[Dict] 每个文件的信息: {path, name, ext, size, relative_path}

    """

    folder = Path(folder_path)

    if not folder.exists():

        return []



    files = []



    def _scan(dir_path: Path, depth: int = 0):

        if depth > max_depth:

            return

        try:

            for item in dir_path.iterdir():

                if item.is_file():

                    ext = item.suffix.lower()

                    if ext in SUPPORTED_EXTENSIONS:

                        rel = item.relative_to(folder)

                        files.append({

                            'path': str(item),

                            'name': item.name,

                            'ext': ext,

                            'size': item.stat().st_size,

                            'relative_path': str(rel)

                        })

                elif item.is_dir() and recursive:

                    _scan(item, depth + 1)

        except PermissionError:

            pass



    _scan(folder)

    return files





def process_file(

    file_info: Dict,

    action: str,

    options: Dict,

    out_dir: str

) -> Dict:

    """

    处理单个文件，返回结果



    Returns:

        Dict 包含: path, name, ext, relative_path, status, input_size, output_size,

                  output_path, items_found, error, type (sanitize/slim/ssd/copy)

    """

    file_path = file_info['path']

    ext = file_info['ext']

    rel_path = file_info['relative_path']



    result = {

        'path': file_path,

        'name': file_info['name'],

        'ext': ext,

        'relative_path': rel_path,

        'status': 'pending',

        'input_size': file_info['size'],

        'output_size': 0,

        'output_path': '',

        'output_name': '',

        'items_found': {},

        'error': '',

        'type': action,  # sanitize / slim / ssd / copy

    }



    try:

        # 读取文件

        text = read_file(file_path)

        original_len = len(text)



        # 处理

        ssd_converted = False  # 标记是否成功转换为 SSD（初始化）



        if action == 'slim':

            # 检查是否需要转换为 SSD

            if options.get('convert_to_ssd', False):

                try:

                    from format_to_ssd import convert_to_ssd_v2, is_ssd_convertible

                    if is_ssd_convertible(file_path):

                        processed = convert_to_ssd_v2(file_path, optimize=True)

                        stats = {'compression_rate': 0}  # SSD 转换不计算压缩率

                        ssd_converted = True

                    else:

                        # 不支持的格式，用普通压缩

                        processor = DocSlimmer()

                        res = processor.slim(

                            text,

                            compression_rate=options.get('compression_rate', 0.3),

                            remove_ai=options.get('remove_ai', False)

                        )

                        processed = res['result']

                        stats = res['stats']

                except Exception as e:

                    # MarkItDown 转换失败，降级到普通压缩

                    print(f"      SSD 转换失败: {e}")

                    processor = DocSlimmer()

                    res = processor.slim(

                        text,

                        compression_rate=options.get('compression_rate', 0.3),

                        remove_ai=options.get('remove_ai', False)

                    )

                    processed = res['result']

                    stats = res['stats']

            else:

                # 不转换 SSD，用普通压缩

                processor = DocSlimmer()

                res = processor.slim(

                    text,

                    compression_rate=options.get('compression_rate', 0.3),

                    remove_ai=options.get('remove_ai', False)

                )

                processed = res['result']

                stats = res['stats']



        elif action == 'sanitize':

            orig_ext = Path(file_path).suffix.lower()



            # 先检查是否需要转换为 SSD
            if options.get('convert_to_ssd', False):
                try:
                    from format_to_ssd import convert_to_ssd_v2, is_ssd_convertible, MARKITDOWN_AVAILABLE
                    print(f"      [DEBUG] SSD 转换选项已启用，检查文件: {file_path}")
                    print(f"      [DEBUG] is_ssd_convertible: {is_ssd_convertible(file_path)}")
                    print(f"      [DEBUG] MARKITDOWN_AVAILABLE: {MARKITDOWN_AVAILABLE}")
                    
                    if is_ssd_convertible(file_path):
                        print(f"      [DEBUG] 开始 SSD 转换...")
                        # 先转为 SSD
                        ssd_content = convert_to_ssd_v2(file_path, optimize=True)
                        print(f"      [DEBUG] SSD 转换完成，长度: {len(ssd_content)}")
                        # 再对 SSD 内容脱敏
                        from sanitize_ssd import SSDSanitizer
                        sanitizer = SSDSanitizer()
                        
                        # UI类型名 -> 代码处理名 的映射
                        sanitize_type_map = {
                            '金额': '投标/成交价',
                        }
                        sanitize_items = options.get('sanitize_items', None)
                        if sanitize_items and isinstance(sanitize_items, list):
                            mapped_items = {}
                            for t in sanitize_items:
                                mapped_items[sanitize_type_map.get(t, t)] = True
                            sanitize_items = mapped_items
                        
                        res = sanitizer.sanitize(
                            ssd_content,
                            items=sanitize_items,
                            custom_words=options.get('custom_words', [])
                        )
                        processed = res['result']
                        stats = res['stats']
                        print(f"      [DEBUG] SSD 脱敏完成，长度: {len(processed)}")
                        # ★★★ 关键：SSD 脱敏后必须立即 return，否则 fallthrough 到后面的代码会覆盖结果
                        out_ext = '.md'
                        if options.get('backup', False):
                            backup_path = Path(output_base) / file_info['relative_path']
                            if backup_path.exists():
                                import shutil
                                backup_path.replace(backup_path.with_stem(backup_path.stem + '_原始'))
                        out_name = Path(file_info['name']).stem + '_脱敏' + out_ext
                        out_path = Path(output_base) / file_info['relative_path'].replace(
                            str(Path(file_info['name'])), out_name, 1)
                        out_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(str(out_path), 'w', encoding='utf-8') as f:
                            f.write(processed)
                        return {
                            'status': 'success',
                            'result': processed,
                            'output_name': out_name,
                            'output_size': out_path.stat().st_size,
                            'stats': stats,
                        }
                    else:
                        # 不支持 SSD 转换，直接脱敏
                        print(f"      [DEBUG] 文件不支持 SSD 转换")
                        ssd_converted = False
                except Exception as e:
                    print(f"      SSD 转换失败: {e}")
                    import traceback
                    traceback.print_exc()
                    ssd_converted = False
            
            # 未转换 SSD 或转换失败，使用普通脱敏
            if not ssd_converted:
                # UI类型名 -> 代码处理名 的映射
                sanitize_type_map = {
                    '金额': '投标/成交价',
                }

                # 转换 sanitize_items 的键名
                sanitize_items = options.get('sanitize_items', None)
                if sanitize_items and isinstance(sanitize_items, list):
                    mapped_items = {}
                    for t in sanitize_items:
                        mapped_items[sanitize_type_map.get(t, t)] = True
                    sanitize_items = mapped_items

                # SSD 文件使用专门的脱敏器
                if orig_ext == '.ssd':
                    from sanitize_ssd import SSDSanitizer
                    sanitizer = SSDSanitizer()
                    res = sanitizer.sanitize(
                        text,
                        items=sanitize_items,
                        custom_words=options.get('custom_words', [])
                    )
                    processed = res['result']
                    stats = res['stats']
                else:
                    # 其他文件使用普通脱敏器
                    # DocSanitizer 需要 list 格式的 items
                    sanitize_items_for_doc = None
                    if sanitize_items and isinstance(sanitize_items, dict):
                        sanitize_items_for_doc = list(sanitize_items.keys())
                    elif sanitize_items and isinstance(sanitize_items, list):
                        sanitize_items_for_doc = sanitize_items

                    processor = DocSanitizer()
                    res = processor.sanitize(
                        text,
                        custom_words=options.get('custom_words', []),
                        items=sanitize_items_for_doc
                    )
                    processed = res['result']
                    stats = res['stats']



        else:

            result['status'] = 'error'

            result['error'] = f'Unknown action: {action}'

            return result



        # 生成输出路径

        # 规则：减肥/脱敏时保持原文件扩展名（仅 SSD 转换输出 .md）

        if ssd_converted:

            # SSD 转换：输出为 .md 文件

            action_tag = 'SSD'

            out_ext = '.md'

            result['type'] = 'ssd'

        else:

            # 减肥/脱敏：保持原文件扩展名

            action_tag = '减肥' if action == 'slim' else '脱敏'

            orig_ext = Path(file_path).suffix.lower()

            # 特殊处理 Office 文档：减肥/脱敏后仍保持原格式
            
            if orig_ext in ('.docx', '.xlsx', '.pptx'):
            
                out_ext = orig_ext
            
            elif orig_ext == '.ssd':
            
                out_ext = '.ssd'
            
            elif orig_ext == '.pdf':
                # PDF 脱敏后无法保持原格式，输出为文本
                out_ext = '.txt'
            
            else:
            
                out_ext = orig_ext if orig_ext else '.txt'



        stem = Path(file_path).stem

        out_name = f"{stem}_{action_tag}{out_ext}"



        # 保持目录结构

        rel_dir = str(Path(rel_path).parent)

        if rel_dir == '.':

            target_dir = Path(out_dir)

        else:

            target_dir = Path(out_dir) / rel_dir



        target_dir.mkdir(parents=True, exist_ok=True)

        out_path = target_dir / out_name



        # 写入

        with open(out_path, 'w', encoding='utf-8') as f:

            f.write(processed)



        result['status'] = 'success'

        result['output_path'] = str(out_path)

        result['output_name'] = out_name

        result['original_chars'] = original_len

        result['output_chars'] = len(processed)

        # 使用实际写入的文件大小

        result['output_size'] = len(processed.encode('utf-8'))

        result['compression_rate'] = stats.get('compression_rate', 0)

        result['items_found'] = {k: v for k, v in stats.items() if v and k != '总计'}



        # Token 估算

        try:

            from safe_shrink import estimate_tokens

            result['original_tokens'] = estimate_tokens(text).get('total', 0)

            result['output_tokens'] = estimate_tokens(processed).get('total', 0)

        except Exception:

            result['original_tokens'] = 0

            result['output_tokens'] = 0



    except FileNotFoundError:

        result['status'] = 'error'

        result['error'] = '文件不存在'

    except PermissionError:

        result['status'] = 'error'

        result['error'] = '权限不足'

    except ImportError as e:

        result['status'] = 'skip'

        result['error'] = f'缺少依赖: {str(e)[:50]}'

    except Exception as e:

        result['status'] = 'error'

        result['error'] = f'{type(e).__name__}: {str(e)[:80]}'

        result['traceback'] = traceback.format_exc()



    return result





def batch_process(

    folder_path: str,

    action: str,

    options: Dict,

    recursive: bool = True,

    workers: int = 4,

    out_base: str = None,

    output_ext: str = None

) -> Dict:

    """

    批量处理文件夹



    Args:

        folder_path: 输入文件夹

        action: 'slim' 或 'sanitize'

        options: 处理选项

        recursive: 是否递归子文件夹

        workers: 并行处理线程数

        out_base: 输出基准目录，默认 output/



    Returns:

        Dict 汇总报告

    """

    if not HAS_CORE:

        return {'error': '核心模块未加载，请确保 safe_shrink.py 可正常导入'}



    folder = Path(folder_path).resolve()

    if not folder.exists():

        return {'error': f'文件夹不存在: {folder}'}

    if not folder.is_dir():

        return {'error': f'不是有效目录: {folder}'}



    start_time = time.time()

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')



    # 输出目录

    if out_base is None:

        out_base = folder.parent / f"{folder.name}_处理结果_{timestamp}"

    else:

        out_base = Path(out_base)



    # 扫描

    print(f"[扫描] {folder}")

    files = scan_folder(folder, recursive=recursive)

    print(f"[发现] {len(files)} 个支持的文件")



    # 状态检测：检查是否已处理

    pre_check = {'status': 'UNPROCESSED', 'details': {}}

    if HAS_STATUS_CHECKER:

        checker = FileStatusChecker()

        pre_check = checker.check_folder(str(folder))

        if pre_check['status'] == 'PROCESSED':

            print(f"[跳过] 文件夹已处理（标记文件存在），跳过重复处理")

            return {

                'folder': str(folder),

                'output_dir': str(out_base),

                'summary': {'total': 0, 'success': 0, 'error': 0, 'skip': 0},

                'results': [],

                'pre_check': pre_check,

                'error': '该文件夹已处理过，无需重复处理'

            }

        elif pre_check['status'] == 'PARTIAL':

            print(f"[注意] 检测到部分文件已处理，将重新处理全部文件")



    if not files:

        return {

            'folder': str(folder),

            'output_dir': str(out_base),

            'summary': {'total': 0, 'success': 0, 'error': 0, 'skip': 0},

            'results': [],

            'error': '未发现支持的文件'

        }



    # 处理

    results = []

    success_count = 0

    error_count = 0

    skip_count = 0

    total_input_size = 0

    total_output_size = 0



    print(f"[处理] 启动 {workers} 个线程...")



    with ThreadPoolExecutor(max_workers=workers) as executor:

        futures = {

            executor.submit(process_file, f, action, options, str(out_base)): f

            for f in files

        }



        for i, future in enumerate(as_completed(futures), 1):

            res = future.result()

            results.append(res)



            status_icon = {'success': 'OK', 'error': 'X', 'skip': '-', 'pending': '.'}[res['status']]



            if res['status'] == 'success':

                success_count += 1

                total_input_size += res['input_size']

                total_output_size += res['output_size']

                icon = 'OK'

            elif res['status'] == 'skip':

                skip_count += 1

                icon = '-'

            else:

                error_count += 1

                icon = 'X'



            # 打印进度

            ext = res['ext']

            name = res['name']

            info = ''

            if res['status'] == 'success' and action == 'slim':

                info = f"[{res['compression_rate']}%]"

            elif res['status'] == 'success' and action == 'sanitize':

                items = res['items_found']

                if items:

                    total_items = sum(v for v in items.values() if isinstance(v, int))

                    info = f"[脱敏{total_items}项]"



            print(f"  [{i}/{len(files)}] {icon} {name:40} {info}")



            if res['status'] == 'error':

                print(f"       错误: {res['error'][:80]}")

            elif res['status'] == 'skip':

                print(f"       跳过: {res['error']}")



    elapsed = time.time() - start_time



    # 汇总

    summary = {

        'total': len(files),

        'success': success_count,

        'error': error_count,

        'skip': skip_count,

        'total_input_size': total_input_size,

        'total_output_size': total_output_size,

        'size_reduced': total_input_size - total_output_size,

        'elapsed_seconds': round(elapsed, 1)

    }



    # 写入标记文件

    if HAS_STATUS_CHECKER and success_count > 0:

        checker = FileStatusChecker()

        # 构建处理记录

        processed_records = []

        for r in results:

            if r['status'] == 'success':

                processed_records.append({

                    'original': r['name'],

                    'output': r.get('output_name', Path(r['output_path']).name if r.get('output_path') else ''),

                    'type': r.get('type', action),

                    'status': 'success',

                    'items_found': r.get('items_found', {})

                })

            elif r['status'] == 'skip':

                processed_records.append({

                    'original': r['name'],

                    'output': '',

                    'type': 'copy',

                    'status': 'skipped',

                    'error': r.get('error', '')

                })

            elif r['status'] == 'error':

                processed_records.append({

                    'original': r['name'],

                    'output': '',

                    'type': action,

                    'status': 'failed',

                    'error': r.get('error', '')

                })



        # 写入标记文件

        try:

            marker_data = checker.write_marker(

                folder_path=str(folder),

                processed_files=processed_records,

                output_folder=str(out_base),

                operation=action,

                options=options

            )

            print(f"[标记] 写入处理记录到 {out_base / checker.marker_file}")

        except Exception as e:

            print(f"[警告] 写入标记文件失败: {e}")



    # 生成报告

    report = generate_report(folder, action, options, summary, results, str(out_base))



    return {

        'folder': str(folder),

        'output_dir': str(out_base),

        'summary': summary,

        'results': results,

        'report': report

    }





def generate_report(

    folder: Path,

    action: str,

    options: Dict,

    summary: Dict,

    results: List[Dict],

    output_dir: str

) -> str:

    """生成汇总报告"""



    action_name = '文档减肥' if action == 'slim' else '文档脱敏'

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')



    lines = [

        f"{'='*60}",

        f"  SafeShrink 批量处理报告",

        f"{'='*60}",

        f"",

        f"处理时间: {timestamp}",

        f"源文件夹: {folder}",

        f"输出目录: {output_dir}",

        f"处理动作: {action_name}",

        f"",

        f"{'='*60}",

        f"  汇总",

        f"{'='*60}",

        f"  总文件数: {summary['total']}",

        f"  成功: {summary['success']}",

        f"  失败: {summary['error']}",

        f"  跳过: {summary['skip']}",

    ]



    if summary['total_input_size'] > 0:

        rate = (summary['size_reduced'] / summary['total_input_size']) * 100

        lines.append(f"  原始大小: {format_size(summary['total_input_size'])}")

        lines.append(f"  处理后大小: {format_size(summary['total_output_size'])}")

        lines.append(f"  节省: {format_size(summary['size_reduced'])} ({rate:.1f}%)")



    lines.extend([f"  耗时: {summary['elapsed_seconds']}秒", f""])



    # 成功列表

    if summary['success'] > 0:

        lines.extend([f"{'='*60}", f"  成功文件", f"{'='*60}"])

        for r in results:

            if r['status'] == 'success':

                size_info = format_size(r['output_size'])

                items_info = ''

                if r['items_found']:

                    total_items = sum(v for v in r['items_found'].values() if isinstance(v, int))

                    items_info = f" | 脱敏{total_items}项"

                lines.append(f"  [OK] {r['relative_path']} ({size_info}){items_info}")



    # 失败列表

    if summary['error'] > 0:

        lines.extend([f"", f"{'='*60}", f"  失败文件", f"{'='*60}"])

        for r in results:

            if r['status'] == 'error':

                lines.append(f"  [X] {r['relative_path']}")

                lines.append(f"      {r['error']}")



    # 跳过列表

    if summary['skip'] > 0:

        lines.extend([f"", f"{'='*60}", f"  跳过文件（缺少依赖）", f"{'='*60}"])

        for r in results:

            if r['status'] == 'skip':

                lines.append(f"  [-] {r['relative_path']} | {r['error']}")



    report_text = '\n'.join(lines)



    # 保存报告

    report_path = Path(output_dir) / '处理报告.txt'

    with open(report_path, 'w', encoding='utf-8') as f:

        f.write(report_text)



    return report_text





def cmd_batch(args):

    """批量处理命令（供 safe_shrink.py 调用）"""

    if args.out_dir:

        out_dir = args.out_dir

    else:

        src_parent = str(Path(args.folder).resolve().parent)

        ts = datetime.now().strftime('%Y%m%d_%H%M%S')

        out_dir = os.path.join(src_parent, f"{Path(args.folder).name}_处理结果_{ts}")



    options = {}

    if args.command == 'batch-slim':

        options['compression'] = args.compression

        options['remove_ai'] = args.ai

        action = 'slim'

    else:

        options['custom_words'] = args.words or []

        options['sanitize_items'] = args.items or None

        action = 'sanitize'



    print(f"[批量{action}] 文件夹: {args.folder}")

    print(f"[输出] {out_dir}\n")



    result = batch_process(

        folder_path=args.folder,

        action=action,

        options=options,

        recursive=not args.no_recursive,

        workers=args.workers or 4,

        out_base=out_dir

    )



    if 'error' in result and result.get('total', 0) == 0:

        print(f"\n错误: {result['error']}")

        return



    s = result['summary']

    print(f"\n{'='*50}")

    print(f"  完成！耗时 {s['elapsed_seconds']}秒")

    print(f"  成功: {s['success']}  失败: {s['error']}  跳过: {s['skip']}")

    if s['total_input_size'] > 0:

        rate = s['size_reduced'] / s['total_input_size'] * 100

        print(f"  原始: {format_size(s['total_input_size'])} → 处理后: {format_size(s['total_output_size'])}")

        print(f"  节省: {format_size(s['size_reduced'])} ({rate:.1f}%)")

    print(f"  输出: {result['output_dir']}")

    print(f"  报告: {result['output_dir']}\\处理报告.txt")

    print(f"{'='*50}\n{result['report']}")





def format_size(size: int) -> str:

    """格式化文件大小"""

    if size < 1024:

        return f"{size}B"

    elif size < 1024 * 1024:

        return f"{size/1024:.1f}KB"

    else:

        return f"{size/1024/1024:.1f}MB"

