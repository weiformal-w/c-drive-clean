#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大文件扫描脚本 - 扫描并分析C盘中的大文件
"""

import os
from pathlib import Path
from typing import List, Dict, Tuple
import json
from datetime import datetime
import sys

# 设置标准输出编码为UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

class LargeFileScanner:
    """大文件扫描器"""

    def __init__(self, drive_path: str = "C:\\"):
        self.drive_path = Path(drive_path)
        self.large_files = []

        # 跳过的系统路径
        self.skip_paths = {
            "Windows", "Program Files", "Program Files (x86)",
            "$Recycle.Bin", "System Volume Information", "Recovery"
        }

    def scan_large_files(self, min_size_mb: int = 100, limit: int = 20) -> List[Dict]:
        """扫描大文件"""
        min_bytes = min_size_mb * 1024 * 1024
        found_files = []

        # 搜索路径 - 聚焦用户目录
        search_paths = [
            self.drive_path / "Users",
            self.drive_path / "ProgramData",
        ]

        print(f"正在扫描 {min_size_mb}MB 以上的文件...")

        for search_path in search_paths:
            if not search_path.exists():
                continue

            for item in search_path.rglob("*"):
                if not item.is_file():
                    continue

                # 跳过系统路径
                if any(skip in str(item) for skip in self.skip_paths):
                    continue

                try:
                    size = item.stat().st_size
                    if size >= min_bytes:
                        file_info = {
                            "path": str(item),
                            "name": item.name,
                            "size_mb": round(size / (1024**2), 2),
                            "size_gb": round(size / (1024**3), 2),
                            "extension": item.suffix or "无",
                            "modified_time": datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                            "parent_dir": str(item.parent)
                        }
                        found_files.append(file_info)

                        # 提前退出如果找到足够的文件
                        if len(found_files) >= limit * 3:  # 收集更多然后排序
                            break

                except (PermissionError, FileNotFoundError, Exception):
                    continue

            if len(found_files) >= limit * 3:
                break

        # 按大小排序并取前N个
        found_files.sort(key=lambda x: x["size_mb"], reverse=True)
        self.large_files = found_files[:limit]

        return self.large_files

    def analyze_by_type(self) -> Dict[str, List[Dict]]:
        """按文件类型分析"""
        type_groups = {}

        for file_info in self.large_files:
            ext = file_info["extension"]
            if ext not in type_groups:
                type_groups[ext] = []
            type_groups[ext].append(file_info)

        return type_groups

    def analyze_by_directory(self) -> Dict[str, Dict]:
        """按目录分析"""
        dir_stats = {}

        for file_info in self.large_files:
            parent_dir = file_info["parent_dir"]
            if parent_dir not in dir_stats:
                dir_stats[parent_dir] = {
                    "files": [],
                    "total_size_mb": 0,
                    "file_count": 0
                }

            dir_stats[parent_dir]["files"].append(file_info)
            dir_stats[parent_dir]["total_size_mb"] += file_info["size_mb"]
            dir_stats[parent_dir]["file_count"] += 1

        return dir_stats

    def generate_report(self) -> str:
        """生成扫描报告"""
        if not self.large_files:
            return "没有找到大文件"

        report = []
        report.append("=== 大文件扫描报告 ===")
        report.append(f"扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"文件数量: {len(self.large_files)}\n")

        # 按大小排序的文件列表
        report.append("最大文件列表:")
        for i, file_info in enumerate(self.large_files, 1):
            size_str = f"{file_info['size_gb']:.2f} GB" if file_info['size_gb'] > 1 else f"{file_info['size_mb']:.2f} MB"
            report.append(f"{i}. {file_info['name']}")
            report.append(f"   大小: {size_str}")
            report.append(f"   类型: {file_info['extension']}")
            report.append(f"   路径: {file_info['path']}")
            report.append(f"   修改时间: {file_info['modified_time']}")
            report.append("")

        # 类型分析
        type_groups = self.analyze_by_type()
        if type_groups:
            report.append("文件类型统计:")
            for ext, files in sorted(type_groups.items(), key=lambda x: len(x[1]), reverse=True):
                total_size = sum(f["size_mb"] for f in files)
                report.append(f"  {ext or '无扩展名'}: {len(files)} 个文件, {total_size:.2f} MB")
            report.append("")

        # 目录分析
        dir_stats = self.analyze_by_directory()
        if dir_stats:
            report.append("占用最多的目录:")
            sorted_dirs = sorted(dir_stats.items(), key=lambda x: x[1]["total_size_mb"], reverse=True)[:5]
            for dir_name, stats in sorted_dirs:
                report.append(f"  {dir_name}")
                report.append(f"    文件数: {stats['file_count']}")
                report.append(f"    总大小: {stats['total_size_mb']:.2f} MB")

        return "\n".join(report)

    def export_results(self, output_path: str = "large_files_scan.json"):
        """导出扫描结果"""
        try:
            results = {
                "scan_time": datetime.now().isoformat(),
                "total_files": len(self.large_files),
                "files": self.large_files,
                "type_analysis": self.analyze_by_type(),
                "directory_analysis": self.analyze_by_directory()
            }

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            return f"扫描结果已保存到: {output_path}"
        except Exception as e:
            return f"保存结果失败: {e}"

    def suggest_cleanup(self) -> List[str]:
        """建议清理的文件"""
        suggestions = []

        # 查找明显的清理目标
        target_extensions = {".log", ".tmp", ".cache", ".old", ".bak"}
        target_dirs = ["Temp", "Cache", "Logs", "Backup"]

        for file_info in self.large_files:
            # 检查文件扩展名
            if file_info["extension"].lower() in target_extensions:
                suggestions.append(f"可安全删除: {file_info['path']} ({file_info['size_mb']:.2f} MB)")

            # 检查目录名
            for target_dir in target_dirs:
                if target_dir in file_info["parent_dir"]:
                    suggestions.append(f"检查目录: {file_info['parent_dir']} (包含 {file_info['size_mb']:.2f} MB)")
                    break

        return suggestions

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="大文件扫描工具")
    parser.add_argument("--drive", default="C:\\", help="驱动器路径")
    parser.add_argument("--min-size", "--size", type=int, default=100, help="最小文件大小(MB)")
    parser.add_argument("--limit", "--top", type=int, default=20, help="显示文件数量")
    parser.add_argument("--output", default="large_files_scan.json", help="输出JSON文件路径")
    parser.add_argument("--suggest", action="store_true", help="显示清理建议")

    args = parser.parse_args()

    scanner = LargeFileScanner(args.drive)

    print("正在扫描大文件...")
    scanner.scan_large_files(min_size_mb=args.min_size, limit=args.limit)

    print("\n" + scanner.generate_report())
    print(f"\n{scanner.export_results(args.output)}")

    if args.suggest:
        suggestions = scanner.suggest_cleanup()
        if suggestions:
            print("\n=== 清理建议 ===")
            for suggestion in suggestions[:10]:
                print(f"• {suggestion}")

if __name__ == "__main__":
    main()