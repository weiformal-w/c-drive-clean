#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C盘清理助手 - 用户友好的包装脚本
提供简化的命令接口和更好的用户体验
"""

import sys
import subprocess
from pathlib import Path

# 设置标准输出编码为UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

class CleanCommandHandler:
    """清理命令处理器"""

    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.analyzer_script = self.script_dir / "analyzer.py"
        self.cleaner_script = self.script_dir / "cleaner.py"
        self.scanner_script = self.script_dir / "scanner.py"
        self.backup_script = self.script_dir / "backup_manager.py"

    def run_analyze(self, args):
        """运行分析命令"""
        cmd = [sys.executable, str(self.analyzer_script)]

        # 转换参数
        if args.get('deep'):
            cmd.append("--large-files")
        if args.get('min_size'):
            cmd.extend(["--min-size", str(args['min_size'])])

        self._run_command(cmd)

    def run_clean(self, args):
        """运行清理命令"""
        cmd = [sys.executable, str(self.cleaner_script)]

        # 确定清理模式
        if args.get('basic'):
            cmd.append("--basic")
        elif args.get('full'):
            cmd.append("--full")
        elif args.get('aggressive'):
            cmd.append("--aggressive")
        else:
            cmd.append("--basic")  # 默认基础清理

        # 安全选项
        if args.get('dry_run'):
            cmd.append("--dry-run")
        elif args.get('force'):
            cmd.append("--actual-clean")
        else:
            cmd.append("--dry-run")  # 默认模拟模式

        # 备份选项
        if args.get('no_backup'):
            cmd.append("--no-backup")
        else:
            cmd.append("--backup")

        if args.get('backup_path'):
            cmd.extend(["--backup-path", args['backup_path']])

        self._run_command(cmd)

    def run_scan(self, args):
        """运行扫描命令"""
        cmd = [sys.executable, str(self.scanner_script)]

        if args.get('min_size'):
            cmd.extend(["--min-size", str(args['min_size'])])
        if args.get('limit'):
            cmd.extend(["--limit", str(args['limit'])])
        if args.get('suggest'):
            cmd.append("--suggest")

        self._run_command(cmd)

    def run_backup(self, args):
        """运行备份管理命令"""
        cmd = [sys.executable, str(self.backup_script_script)]

        action = args.get('action', 'list')
        cmd.extend(["--action", action])

        if action in ['restore', 'delete', 'info']:
            if args.get('index') is not None:
                cmd.extend(["--index", str(args['index'])])

        if action == 'clean':
            if args.get('keep'):
                cmd.extend(["--keep", str(args['keep'])])
            if args.get('confirm'):
                cmd.append("--confirm")

        self._run_command(cmd)

    def _run_command(self, cmd):
        """运行命令"""
        try:
            print(f"执行命令: {' '.join(cmd)}")
            result = subprocess.run(cmd, check=True, capture_output=False, text=True)
            return result.returncode == 0
        except subprocess.CalledProcessError as e:
            print(f"命令执行失败: {e}")
            return False
        except FileNotFoundError:
            print("错误: 找不到Python解释器或脚本文件")
            return False

def main():
    """主函数 - 处理命令行参数"""
    import argparse

    parser = argparse.ArgumentParser(description="C盘清理助手")
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 分析命令
    analyze_parser = subparsers.add_parser('analyze', help='分析C盘状态')
    analyze_parser.add_argument('--deep', action='store_true', help='深度扫描')
    analyze_parser.add_argument('--min-size', type=int, default=100, help='最小文件大小(MB)')

    # 清理命令
    clean_parser = subparsers.add_parser('clean', help='清理C盘')
    clean_group = clean_parser.add_mutually_exclusive_group()
    clean_group.add_argument('--basic', action='store_true', help='基础清理')
    clean_group.add_argument('--full', action='store_true', help='完整清理')
    clean_group.add_argument('--aggressive', action='store_true', help='激进清理')
    clean_parser.add_argument('--dry-run', action='store_true', help='模拟模式')
    clean_parser.add_argument('--force', action='store_true', help='强制执行')
    clean_parser.add_argument('--no-backup', action='store_true', help='不备份')
    clean_parser.add_argument('--backup-path', help='备份路径')

    # 扫描命令
    scan_parser = subparsers.add_parser('scan', help='扫描大文件')
    scan_parser.add_argument('--min-size', type=int, default=100, help='最小文件大小(MB)')
    scan_parser.add_argument('--limit', type=int, default=20, help='显示数量')
    scan_parser.add_argument('--suggest', action='store_true', help='显示建议')

    # 备份管理命令
    backup_parser = subparsers.add_parser('backup', help='备份管理')
    backup_parser.add_argument('action', nargs='?', default='list',
                               choices=['list', 'restore', 'delete', 'clean', 'info'],
                               help='操作类型')
    backup_parser.add_argument('--index', type=int, help='备份索引')
    backup_parser.add_argument('--keep', type=int, default=5, help='保留数量')
    backup_parser.add_argument('--confirm', action='store_true', help='确认操作')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    handler = CleanCommandHandler()

    # 转换参数为字典
    args_dict = vars(args)

    if args.command == 'analyze':
        handler.run_analyze(args_dict)
    elif args.command == 'clean':
        handler.run_clean(args_dict)
    elif args.command == 'scan':
        handler.run_scan(args_dict)
    elif args.command == 'backup':
        handler.run_backup(args_dict)
    else:
        parser.print_help()
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())