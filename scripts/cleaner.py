#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C盘清理脚本 - 执行安全的文件清理操作
"""

import os
import shutil
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple
import json
from datetime import datetime
import sys
import ctypes
import subprocess
import time

# 设置标准输出编码为UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def is_admin() -> bool:
    """检查是否具有管理员权限"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """尝试以管理员权限重新运行程序"""
    if sys.platform != 'win32':
        return False

    try:
        # 获取当前脚本路径
        script = sys.executable
        params = ' '.join(['"' + arg + '"' if ' ' in arg else arg for arg in sys.argv])

        # 请求提升权限
        ret = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", script, params, None, 1
        )
        return ret > 32
    except:
        return False

class CDriveCleaner:
    """C盘清理器 - 带完整安全检查和备份功能"""

    def __init__(self, dry_run: bool = False, backup_enabled: bool = True, backup_path: str = None):
        self.dry_run = dry_run
        self.backup_enabled = backup_enabled
        self.backup_path = Path(backup_path) if backup_path else Path.home() / "CleanerBackups" / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_manifest = []

        # 安全路径 - 这些路径永远不会被清理
        self.protected_paths = {
            "Windows", "Program Files", "Program Files (x86)",
            "ProgramData", "$Recycle.Bin", "System Volume Information",
            "Boot", "EFI", "Recovery"
        }

        # 用户数据路径 - 需要特别确认
        self.user_data_paths = {
            "Documents", "Desktop", "Downloads", "Pictures",
            "Music", "Videos", "Contacts", "Favorites", "Links"
        }

        self.cleaning_stats = {
            "deleted_files": 0,
            "freed_space": 0,
            "failed_deletions": 0,
            "backed_up_files": 0
        }

        # 进度跟踪
        self.progress_callbacks = {
            'on_start': lambda msg: print(f"🚀 {msg}"),
            'on_progress': lambda msg, current, total: print(f"⏳ {msg}: {current}/{total}"),
            'on_complete': lambda msg: print(f"✅ {msg}"),
            'on_error': lambda msg: print(f"❌ {msg}")
        }

    def is_safe_to_clean(self, file_path: Path) -> Tuple[bool, str]:
        """检查文件是否安全删除"""
        path_str = str(file_path)

        # 检查保护路径
        for protected in self.protected_paths:
            if protected in path_str.split(os.sep):
                return False, f"受保护路径: {protected}"

        # 检查用户数据路径
        for user_path in self.user_data_paths:
            if user_path in path_str.split(os.sep):
                return False, f"用户数据路径: {user_path}"

        # 检查文件扩展名
        dangerous_extensions = {'.exe', '.dll', '.sys', '.drv', '.com', '.bat', '.cmd', '.ps1'}
        if file_path.suffix.lower() in dangerous_extensions:
            return False, f"可执行文件: {file_path.suffix}"

        return True, "安全"

    def clean_temp_files(self) -> Dict:
        """清理临时文件 - 增强版"""
        temp_paths = [
            Path(os.environ.get("TEMP", "")),
            Path(os.environ.get("TMP", "")),
            Path("C:\\Windows\\Temp"),
            Path("C:\\Windows\\Logs"),
            Path(os.environ.get("LOCALAPPDATA", "")) / "Temp",
        ]

        results = []
        for temp_path in temp_paths:
            if temp_path.exists():
                result = self._clean_directory(temp_path, "temp_files")
                results.append(result)

        return {
            "category": "temp_files",
            "description": "临时文件",
            "results": results,
            "total_freed": sum(r.get("freed_space", 0) for r in results),
            "total_files": sum(r.get("deleted_count", 0) for r in results)
        }

    def clean_browser_cache(self) -> Dict:
        """清理浏览器缓存 - 增强版"""
        browser_paths = [
            Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Default" / "Cache",
            Path.home() / "AppData" / "Local" / "Microsoft" / "Edge" / "User Data" / "Default" / "Cache",
            Path.home() / "AppData" / "Local" / "Mozilla" / "Firefox" / "Profiles",
        ]

        results = []
        for browser_path in browser_paths:
            if browser_path.exists():
                result = self._clean_directory(browser_path, "browser_cache")
                results.append(result)

        return {
            "category": "browser_cache",
            "description": "浏览器缓存",
            "results": results,
            "total_freed": sum(r.get("freed_space", 0) for r in results),
            "total_files": sum(r.get("deleted_count", 0) for r in results)
        }

    def clean_application_cache(self) -> Dict:
        """清理应用程序缓存 - 新增功能"""
        app_paths = [
            # Adobe缓存
            Path.home() / "AppData" / "Roaming" / "Adobe" / "Acrobat" / "DC",
            # Office缓存
            Path.home() / "AppData" / "Local" / "Microsoft" / "Office",
            # Windows Defender
            Path("C:\\ProgramData\\Microsoft\\Windows Defender\\Scans\\History\\CacheManager"),
            # Windows Store缓存
            Path.home() / "AppData" / "Local" / "Microsoft" / "WindowsStore",
            # OneDrive缓存
            Path.home() / "AppData" / "Local" / "Microsoft" / "OneDrive",
            # Windows Media Player
            Path.home() / "AppData" / "Local" / "Microsoft" / "Media Player",
            # 搜索索引
            Path("C:\\ProgramData\\Microsoft\\Windows\\Search"),
            # 通知缓存
            Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Notifications",
            # 网络缓存
            Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "WebCache",
        ]

        results = []
        for app_path in app_paths:
            if app_path.exists():
                result = self._clean_directory(app_path, "application_cache")
                results.append(result)

        return {
            "category": "application_cache",
            "description": "应用缓存",
            "results": results,
            "total_freed": sum(r.get("freed_space", 0) for r in results),
            "total_files": sum(r.get("deleted_count", 0) for r in results)
        }

    def clean_system_cache(self) -> Dict:
        """清理系统缓存 - 增强版，包含Windows更新缓存等高价值项目"""
        system_paths = [
            # Windows更新缓存（通常最大）
            Path("C:\\Windows\\SoftwareDistribution\\Download"),
            # 传递优化缓存（Windows更新临时文件）
            Path("C:\\Windows\\SoftwareDistribution\\DeliveryOptimization"),
            # 预读取文件
            Path("C:\\Windows\\Prefetch"),
            # 缩略图缓存
            Path.home() / "AppData" / "Local" / "Microsoft" / "Windows" / "Explorer",
            # 内存转储文件
            Path("C:\\Windows\\Memory.dmp"),
            Path("C:\\Windows\\Minidump"),
            # 字体缓存
            Path("C:\\Windows\\System32\\FntCache.dat"),
            # 安装程序缓存
            Path("C:\\Windows\\Installer\\$PatchCache$"),
            # 驱动备份
            Path("C:\\Windows\\System32\\DriverStore\\FileRepository"),
        ]

        results = []
        for system_path in system_paths:
            if system_path.exists():
                result = self._clean_directory(system_path, "system_cache")
                results.append(result)

        return {
            "category": "system_cache",
            "description": "系统缓存",
            "results": results,
            "total_freed": sum(r.get("freed_space", 0) for r in results),
            "total_files": sum(r.get("deleted_count", 0) for r in results)
        }

    def clean_recycle_bin(self) -> Dict:
        """清理回收站"""
        recycle_path = Path("C:\\$Recycle.Bin")

        if not recycle_path.exists():
            return {
                "category": "recycle_bin",
                "description": "回收站",
                "results": [],
                "total_freed": 0,
                "total_files": 0,
                "status": "回收站为空或不存在"
            }

        result = self._clean_directory(recycle_path, "recycle_bin", recursive=True)
        return {
            "category": "recycle_bin",
            "description": "回收站",
            "results": [result],
            "total_freed": result.get("freed_space", 0),
            "total_files": result.get("deleted_count", 0)
        }

    def _clean_directory(self, directory: Path, category: str, recursive: bool = True) -> Dict:
        """清理指定目录 - 带进度显示"""
        if not directory.exists():
            return {
                "directory": str(directory),
                "status": "目录不存在",
                "deleted_count": 0,
                "freed_space": 0
            }

        deleted_count = 0
        freed_space = 0
        failed_count = 0
        skipped_files = []

        try:
            # 触发开始回调
            self.progress_callbacks['on_start'](f"开始扫描: {directory}")

            items = list(directory.rglob("*")) if recursive else list(directory.glob("*"))
            total_items = len(items)
            processed_items = 0

            # 触发进度回调
            self.progress_callbacks['on_progress'](f"扫描目录: {directory.name}", 0, total_items)

            last_progress_time = time.time()

            for item in items:
                if not item.is_file():
                    continue

                # 进度显示（每秒最多更新一次，避免过于频繁）
                current_time = time.time()
                if current_time - last_progress_time >= 1.0:
                    processed_items += 1
                    self.progress_callbacks['on_progress'](
                        f"清理中: {directory.name}",
                        processed_items,
                        total_items
                    )
                    last_progress_time = current_time

                # 安全检查
                is_safe, reason = self.is_safe_to_clean(item)
                if not is_safe:
                    skipped_files.append({"path": str(item), "reason": reason})
                    continue

                try:
                    file_size = item.stat().st_size

                    # 备份文件
                    if self.backup_enabled and not self.dry_run:
                        if self._backup_file(item):
                            self.cleaning_stats["backed_up_files"] += 1

                    # 删除文件
                    if not self.dry_run:
                        item.unlink()
                        deleted_count += 1
                        freed_space += file_size
                    else:
                        # 模拟模式 - 只统计
                        deleted_count += 1
                        freed_space += file_size

                except PermissionError as e:
                    failed_count += 1
                    # 记录权限失败的文件，用于后续提示
                    if failed_count <= 5:  # 只显示前5个
                        print(f"⚠️ 权限不足: {item}")
                    continue
                except FileNotFoundError as e:
                    # 文件已被删除，忽略
                    continue

            # 触发完成回调
            self.progress_callbacks['on_complete'](f"完成清理: {directory.name} (释放 {self._format_size(freed_space)})")

        except Exception as e:
            self.progress_callbacks['on_error'](f"清理失败: {directory} - {str(e)}")
            return {
                "directory": str(directory),
                "status": f"错误: {str(e)}",
                "deleted_count": deleted_count,
                "freed_space": freed_space,
                "failed_count": failed_count
            }

        return {
            "directory": str(directory),
            "status": "completed",
            "deleted_count": deleted_count,
            "freed_space": freed_space,
            "failed_count": failed_count,
            "skipped_count": len(skipped_files),
            "skipped_samples": skipped_files[:5]  # 只显示前5个跳过的文件
        }

    def _backup_file(self, file_path: Path) -> bool:
        """备份单个文件"""
        try:
            # 创建备份目录结构
            relative_path = file_path.relative_to(file_path.anchor)
            backup_file_path = self.backup_path / relative_path

            # 创建父目录
            backup_file_path.parent.mkdir(parents=True, exist_ok=True)

            # 复制文件
            shutil.copy2(file_path, backup_file_path)

            # 记录到清单
            self.backup_manifest.append({
                "original": str(file_path),
                "backup": str(backup_file_path),
                "size": file_path.stat().st_size,
                "hash": self._calculate_file_hash(file_path),
                "timestamp": datetime.now().isoformat()
            })

            return True
        except Exception as e:
            print(f"备份失败 {file_path}: {e}")
            return False

    def _calculate_file_hash(self, file_path: Path) -> str:
        """计算文件哈希值"""
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return "unknown"

    def save_backup_manifest(self):
        """保存备份清单"""
        if self.backup_enabled and self.backup_manifest:
            manifest_path = self.backup_path / "backup_manifest.json"
            try:
                with open(manifest_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        "backup_time": datetime.now().isoformat(),
                        "total_files": len(self.backup_manifest),
                        "total_size": sum(item["size"] for item in self.backup_manifest),
                        "files": self.backup_manifest
                    }, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"保存备份清单失败: {e}")

    def generate_report(self, results: List[Dict]) -> str:
        """生成清理报告"""
        report = []
        mode_str = "模拟模式" if self.dry_run else "实际清理"
        backup_str = f"\n备份位置: {self.backup_path}" if self.backup_enabled else "\n未启用备份"

        report.append(f"=== C盘清理{mode_str} ===")
        report.append(f"清理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{backup_str}\n")

        total_freed = 0
        total_files = 0

        for result in results:
            description = result.get("description", "未知类别")
            freed_space = result.get("total_freed", 0)
            file_count = result.get("total_files", 0)

            if freed_space > 0:
                total_freed += freed_space
                total_files += file_count
                report.append(f"✓ {description}: {file_count:,} 个文件 ({self._format_size(freed_space)})")

        if total_freed == 0:
            report.append("没有找到可清理的文件")
        else:
            report.append(f"\n总计释放空间: {self._format_size(total_freed)}")
            report.append(f"总计文件数: {total_files:,}")

        if self.dry_run:
            report.append("\n⚠️ 这是模拟模式，没有实际删除文件")
            report.append("如需实际清理，请使用 --actual-clean 参数")

        return "\n".join(report)

    def _format_size(self, bytes_size: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} TB"

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="C盘清理工具")
    parser.add_argument("--dry-run", action="store_true", help="模拟模式，不实际删除")
    parser.add_argument("--actual-clean", "--force", action="store_true", help="实际执行清理")
    parser.add_argument("--backup", action="store_true", default=True, help="启用备份（默认）")
    parser.add_argument("--no-backup", action="store_true", help="禁用备份")
    parser.add_argument("--backup-path", help="自定义备份路径")
    parser.add_argument("--basic", action="store_true", help="基础清理")
    parser.add_argument("--full", action="store_true", help="完整清理")
    parser.add_argument("--aggressive", action="store_true", help="激进清理")
    parser.add_argument("--admin", action="store_true", help="请求管理员权限")

    args = parser.parse_args()

    # 检查管理员权限
    if args.admin and not is_admin():
        print("正在请求管理员权限...")
        if run_as_admin():
            print("已以管理员权限重新启动")
            return
        else:
            print("⚠️ 无法获取管理员权限，某些清理操作可能失败")
            print("建议：右键点击命令提示符，选择'以管理员身份运行'")

    # 显示权限状态
    if not is_admin():
        print("⚠️ 注意：未以管理员身份运行")
        print("某些系统文件清理可能失败，建议以管理员身份运行")
        print("提示：使用 --admin 参数自动请求管理员权限\n")

    # 确定清理模式
    dry_run = args.dry_run or not args.actual_clean
    backup_enabled = args.backup and not args.no_backup

    cleaner = CDriveCleaner(
        dry_run=dry_run,
        backup_enabled=backup_enabled,
        backup_path=args.backup_path
    )

    print("=== C盘清理工具 ===")
    print(f"模式: {'模拟模式' if dry_run else '实际清理'}")
    print(f"备份: {'启用' if backup_enabled else '禁用'}")
    print(f"权限: {'管理员' if is_admin() else '普通用户'}")
    print(f"开始时间: {datetime.now().strftime('%H:%M:%S')}")
    print("="*50)

    results = []
    start_time = time.time()

    # 基础清理
    print("\n📋 [1/4] 清理临时文件...")
    results.append(cleaner.clean_temp_files())

    print("\n📋 [2/4] 清理浏览器缓存...")
    results.append(cleaner.clean_browser_cache())

    print("\n📋 [3/4] 清理系统缓存...")
    results.append(cleaner.clean_system_cache())

    # 完整清理
    if args.full:
        print("\n📋 [4/4] 清理应用缓存...")
        results.append(cleaner.clean_application_cache())

        print("\n📋 [5/5] 清理回收站...")
        results.append(cleaner.clean_recycle_bin())

    elapsed_time = time.time() - start_time

    # 保存备份清单
    if backup_enabled and not dry_run:
        cleaner.save_backup_manifest()
        print(f"\n备份已保存到: {cleaner.backup_path}")

    # 生成报告
    print("\n" + "="*50)
    print(f"完成时间: {datetime.now().strftime('%H:%M:%S')}")
    print(f"总耗时: {elapsed_time:.1f}秒")
    print("="*50)
    print("\n" + cleaner.generate_report(results))

if __name__ == "__main__":
    main()