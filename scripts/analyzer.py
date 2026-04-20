#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C盘分析脚本 - 分析磁盘使用情况和垃圾文件
"""

import os
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import json
import sys

# 设置标准输出编码为UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

class CDriveAnalyzer:
    """C盘分析器"""

    def __init__(self, drive_path: str = "C:\\"):
        self.drive_path = Path(drive_path)
        self.results = {
            "drive_info": {},
            "cleanable_items": {},
            "large_files": [],
            "warnings": []
        }

    def get_drive_info(self) -> Dict:
        """获取驱动器基本信息"""
        try:
            usage = shutil.disk_usage(self.drive_path)
            total_gb = usage.total / (1024**3)
            used_gb = usage.used / (1024**3)
            free_gb = usage.free / (1024**3)
            usage_percent = (usage.used / usage.total) * 100

            self.results["drive_info"] = {
                "total_gb": round(total_gb, 2),
                "used_gb": round(used_gb, 2),
                "free_gb": round(free_gb, 2),
                "usage_percent": round(usage_percent, 2),
                "status": "critical" if usage_percent > 90 else "warning" if usage_percent > 80 else "normal"
            }
            return self.results["drive_info"]
        except Exception as e:
            self.results["warnings"].append(f"无法获取磁盘信息: {str(e)}")
            return {}

    def analyze_temp_files(self) -> Dict:
        """分析临时文件"""
        temp_paths = [
            Path(os.environ.get("TEMP", "")),
            Path(os.environ.get("TMP", "")),
            self.drive_path / "Windows" / "Temp",
            self.drive_path / "Windows" / "Logs",
            self.drive_path / "Windows" / "SoftwareDistribution" / "Download"
        ]

        total_size = 0
        file_count = 0

        for temp_path in temp_paths:
            if temp_path.exists():
                try:
                    for item in temp_path.rglob("*"):
                        if item.is_file():
                            try:
                                size = item.stat().st_size
                                total_size += size
                                file_count += 1
                            except (PermissionError, FileNotFoundError):
                                continue
                except (PermissionError, Exception) as e:
                    self.results["warnings"].append(f"无法访问 {temp_path}: {str(e)}")

        self.results["cleanable_items"]["temp_files"] = {
            "description": "临时文件",
            "size_gb": round(total_size / (1024**3), 2),
            "file_count": file_count,
            "safe_to_clean": True
        }
        return self.results["cleanable_items"]["temp_files"]

    def analyze_browser_cache(self) -> Dict:
        """分析浏览器缓存"""
        browser_paths = [
            Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Default" / "Cache",
            Path.home() / "AppData" / "Local" / "Microsoft" / "Edge" / "User Data" / "Default" / "Cache",
            Path.home() / "AppData" / "Local" / "Mozilla" / "Firefox" / "Profiles"
        ]

        total_size = 0
        file_count = 0

        for browser_path in browser_paths:
            if browser_path.exists():
                try:
                    if "Firefox" in str(browser_path):
                        # Firefox处理多个profile
                        for profile in browser_path.glob("*"):
                            if profile.is_dir():
                                cache_folders = ["cache2", "startupCache"]
                                for cache_name in cache_folders:
                                    cache_path = profile / cache_name
                                    if cache_path.exists():
                                        total_size += self._calculate_folder_size(cache_path)
                    else:
                        total_size += self._calculate_folder_size(browser_path)
                except (PermissionError, Exception) as e:
                    self.results["warnings"].append(f"无法访问浏览器缓存 {browser_path}: {str(e)}")

        self.results["cleanable_items"]["browser_cache"] = {
            "description": "浏览器缓存",
            "size_gb": round(total_size / (1024**3), 2),
            "file_count": file_count,
            "safe_to_clean": True
        }
        return self.results["cleanable_items"]["browser_cache"]

    def analyze_system_cache(self) -> Dict:
        """分析系统缓存"""
        system_paths = [
            self.drive_path / "Windows" / "SoftwareDistribution" / "Download",
            self.drive_path / "Windows" / "Prefetch",
            self.drive_path / "Windows" / "Fonts" / " fonts_cache",
            self.drive_path / "ProgramData" / "Microsoft" / "Windows" / "SPP" / "Cache"
        ]

        total_size = 0
        file_count = 0

        for system_path in system_paths:
            if system_path.exists():
                try:
                    size, count = self._get_folder_size(system_path)
                    total_size += size
                    file_count += count
                except (PermissionError, Exception) as e:
                    self.results["warnings"].append(f"无法访问系统路径 {system_path}: {str(e)}")

        self.results["cleanable_items"]["system_cache"] = {
            "description": "系统缓存",
            "size_gb": round(total_size / (1024**3), 2),
            "file_count": file_count,
            "safe_to_clean": True
        }
        return self.results["cleanable_items"]["system_cache"]

    def scan_large_files(self, min_size_mb: int = 100, limit: int = 20) -> List[Dict]:
        """扫描大文件"""
        large_files = []
        min_bytes = min_size_mb * 1024 * 1024

        # 常见的大文件位置
        search_paths = [
            self.drive_path / "Users",
            self.drive_path / "Program Files",
            self.drive_path / "Program Files (x86)"
        ]

        try:
            for search_path in search_paths:
                if search_path.exists():
                    for item in search_path.rglob("*"):
                        if item.is_file():
                            try:
                                size = item.stat().st_size
                                if size >= min_bytes:
                                    large_files.append({
                                        "path": str(item),
                                        "size_mb": round(size / (1024**2), 2),
                                        "size_gb": round(size / (1024**3), 2),
                                        "modified": item.stat().st_mtime,
                                        "extension": item.suffix
                                    })
                            except (PermissionError, FileNotFoundError):
                                continue

                        if len(large_files) >= limit * 2:  # 收集更多然后排序
                            break

                if len(large_files) >= limit * 2:
                    break

            # 按大小排序并取前N个
            large_files.sort(key=lambda x: x["size_mb"], reverse=True)
            self.results["large_files"] = large_files[:limit]

        except Exception as e:
            self.results["warnings"].append(f"扫描大文件时出错: {str(e)}")

        return self.results["large_files"]

    def _calculate_folder_size(self, folder_path: Path) -> int:
        """计算文件夹大小"""
        total_size = 0
        try:
            for item in folder_path.rglob("*"):
                if item.is_file():
                    try:
                        total_size += item.stat().st_size
                    except (PermissionError, FileNotFoundError):
                        continue
        except Exception:
            pass
        return total_size

    def _get_folder_size(self, folder_path: Path) -> Tuple[int, int]:
        """获取文件夹大小和文件数量"""
        total_size = 0
        file_count = 0
        try:
            for item in folder_path.rglob("*"):
                if item.is_file():
                    try:
                        total_size += item.stat().st_size
                        file_count += 1
                    except (PermissionError, FileNotFoundError):
                        continue
        except Exception:
            pass
        return total_size, file_count

    def generate_report(self) -> str:
        """生成分析报告"""
        self.get_drive_info()

        report = []
        report.append("=== C盘分析报告 ===\n")

        # 驱动器信息
        if self.results["drive_info"]:
            info = self.results["drive_info"]
            status_emoji = "🔴" if info["status"] == "critical" else "🟡" if info["status"] == "warning" else "🟢"
            report.append(f"状态: {status_emoji}")
            report.append(f"总空间: {info['total_gb']} GB")
            report.append(f"已使用: {info['used_gb']} GB ({info['usage_percent']}%)")
            report.append(f"可用空间: {info['free_gb']} GB\n")

        # 可清理项目
        report.append("可清理空间估算:")
        total_cleanable = 0

        for item_name, item_data in self.results["cleanable_items"].items():
            if item_data.get("safe_to_clean", False):
                size_gb = item_data.get("size_gb", 0)
                total_cleanable += size_gb
                file_count = item_data.get("file_count", 0)
                report.append(f"- {item_data['description']}: {file_count:,} 个文件 ({size_gb} GB)")

        report.append(f"\n总计可释放: ~{round(total_cleanable, 2)} GB")

        # 大文件
        if self.results["large_files"]:
            report.append(f"\n大文件 (>100MB): {len(self.results['large_files'])} 个文件")
            for i, file_info in enumerate(self.results["large_files"][:10], 1):
                report.append(f"{i}. {file_info['path']}")
                report.append(f"   大小: {file_info['size_gb']} GB ({file_info['size_mb']} MB)")

        # 警告信息
        if self.results["warnings"]:
            report.append("\n⚠️ 警告信息:")
            for warning in self.results["warnings"][:5]:
                report.append(f"- {warning}")

        return "\n".join(report)

    def export_results(self, output_path: str = "analysis_results.json"):
        """导出分析结果到JSON"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            return f"分析结果已保存到: {output_path}"
        except Exception as e:
            return f"保存结果失败: {str(e)}"

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="C盘分析工具")
    parser.add_argument("--drive", default="C:\\", help="驱动器路径")
    parser.add_argument("--output", default="analysis_results.json", help="输出JSON文件路径")
    parser.add_argument("--large-files", "--deep", action="store_true", help="扫描大文件（深度扫描）")
    parser.add_argument("--min-size", type=int, default=100, help="最小文件大小(MB)")
    parser.add_argument("--quick", action="store_true", help="快速扫描（仅显示基本信息，不分析垃圾文件）")

    args = parser.parse_args()

    analyzer = CDriveAnalyzer(args.drive)

    print("正在分析C盘...")

    # 默认深度分析，除非用户指定 --quick 快速模式
    if not args.quick:
        analyzer.analyze_temp_files()
        analyzer.analyze_browser_cache()
        analyzer.analyze_system_cache()

    # 默认扫描大文件，除非用户指定 --quick 快速模式
    if not args.quick:
        print("正在扫描大文件...")
        analyzer.scan_large_files(min_size_mb=args.min_size)

    print("\n" + analyzer.generate_report())
    if not args.quick:
        print(f"\n{analyzer.export_results(args.output)}")
    else:
        print("\n💡 提示: 使用完整分析请运行: python analyzer.py")

if __name__ == "__main__":
    main()