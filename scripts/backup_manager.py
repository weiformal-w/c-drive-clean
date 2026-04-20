#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
备份管理脚本 - 管理清理备份的恢复和清理
"""

import os
import shutil
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import sys

# 设置标准输出编码为UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

class BackupManager:
    """备份管理器"""

    def __init__(self, backup_root: str = None):
        self.backup_root = Path(backup_root) if backup_root else Path.home() / "CleanerBackups"
        self.backups = []
        self._scan_backups()

    def _scan_backups(self):
        """扫描所有备份"""
        self.backups = []

        if not self.backup_root.exists():
            return

        for backup_dir in self.backup_root.glob("*"):
            if backup_dir.is_dir():
                manifest_file = backup_dir / "backup_manifest.json"
                if manifest_file.exists():
                    try:
                        with open(manifest_file, 'r', encoding='utf-8') as f:
                            manifest = json.load(f)
                            self.backups.append({
                                "path": str(backup_dir),
                                "name": backup_dir.name,
                                "manifest": manifest,
                                "file_count": manifest.get("total_files", 0),
                                "total_size": manifest.get("total_size", 0),
                                "backup_time": manifest.get("backup_time", ""),
                                "manifest_path": str(manifest_file)
                            })
                    except Exception as e:
                        print(f"读取备份清单失败 {backup_dir}: {e}")

        # 按时间排序
        self.backups.sort(key=lambda x: x["backup_time"], reverse=True)

    def list_backups(self) -> str:
        """列出所有备份"""
        if not self.backups:
            return "没有找到备份"

        report = []
        report.append("=== 备份列表 ===\n")

        total_size = 0
        for i, backup in enumerate(self.backups, 1):
            size_gb = backup["total_size"] / (1024**3)
            total_size += backup["total_size"]

            try:
                backup_time = datetime.fromisoformat(backup["backup_time"])
                time_str = backup_time.strftime("%Y-%m-%d %H:%M:%S")
            except:
                time_str = backup["backup_time"]

            report.append(f"{i}. {backup['name']}")
            report.append(f"   时间: {time_str}")
            report.append(f"   文件数: {backup['file_count']:,}")
            report.append(f"   大小: {size_gb:.2f} GB")
            report.append(f"   路径: {backup['path']}")
            report.append("")

        report.append(f"总计备份数: {len(self.backups)}")
        report.append(f"总计大小: {total_size / (1024**3):.2f} GB")

        return "\n".join(report)

    def restore_backup(self, backup_index: int, dry_run: bool = False) -> str:
        """恢复指定备份"""
        if backup_index < 0 or backup_index >= len(self.backups):
            return f"无效的备份索引: {backup_index}"

        backup = self.backups[backup_index]
        manifest = backup["manifest"]

        report = []
        mode_str = "模拟恢复" if dry_run else "实际恢复"
        report.append(f"=== {mode_str} ===")
        report.append(f"备份: {backup['name']}")
        report.append(f"文件数: {backup['file_count']:,}")
        report.append(f"大小: {backup['total_size'] / (1024**3):.2f} GB\n")

        if not dry_run:
            report.append("正在恢复文件...")
        else:
            report.append("将要恢复以下文件:")

        restored_count = 0
        failed_count = 0
        skipped_count = 0

        for file_info in manifest.get("files", []):
            original_path = Path(file_info["original"])
            backup_path = Path(file_info["backup"])

            if not backup_path.exists():
                failed_count += 1
                continue

            # 检查原位置是否已存在文件
            if original_path.exists():
                skipped_count += 1
                if dry_run:
                    report.append(f"跳过 (文件已存在): {original_path}")
                continue

            if dry_run:
                report.append(f"恢复: {original_path}")
                restored_count += 1
            else:
                try:
                    # 创建父目录
                    original_path.parent.mkdir(parents=True, exist_ok=True)
                    # 复制文件
                    shutil.copy2(backup_path, original_path)
                    restored_count += 1
                except Exception as e:
                    failed_count += 1
                    report.append(f"失败: {original_path} - {e}")

        report.append(f"\n恢复完成:")
        report.append(f"成功: {restored_count:,}")
        report.append(f"跳过: {skipped_count:,}")
        report.append(f"失败: {failed_count:,}")

        if not dry_run:
            report.append("\n请验证恢复的文件是否正常")

        return "\n".join(report)

    def delete_backup(self, backup_index: int, confirm: bool = False) -> str:
        """删除指定备份"""
        if not confirm:
            return "删除操作需要确认，请使用 --confirm 参数"

        if backup_index < 0 or backup_index >= len(self.backups):
            return f"无效的备份索引: {backup_index}"

        backup = self.backups[backup_index]
        backup_path = Path(backup["path"])

        try:
            shutil.rmtree(backup_path)
            self._scan_backups()  # 重新扫描
            return f"备份已删除: {backup['name']}"
        except Exception as e:
            return f"删除失败: {e}"

    def clean_old_backups(self, keep_count: int = 5, confirm: bool = False) -> str:
        """清理旧备份，保留最近的N个"""
        if not confirm:
            return "清理操作需要确认，请使用 --confirm 参数"

        if len(self.backups) <= keep_count:
            return f"当前备份数 ({len(self.backups)}) 未超过保留数量 ({keep_count})"

        # 删除最旧的备份
        backups_to_delete = self.backups[keep_count:]
        deleted_count = 0
        freed_space = 0

        report = []
        report.append(f"=== 清理旧备份 ===")
        report.append(f"保留最近 {keep_count} 个备份")
        report.append(f"删除 {len(backups_to_delete)} 个旧备份\n")

        for backup in backups_to_delete:
            backup_path = Path(backup["path"])
            size = backup["total_size"]
            try:
                shutil.rmtree(backup_path)
                deleted_count += 1
                freed_space += size
                report.append(f"已删除: {backup['name']} ({size / (1024**3):.2f} GB)")
            except Exception as e:
                report.append(f"删除失败: {backup['name']} - {e}")

        self._scan_backups()  # 重新扫描

        report.append(f"\n清理完成:")
        report.append(f"删除备份数: {deleted_count}")
        report.append(f"释放空间: {freed_space / (1024**3):.2f} GB")
        report.append(f"剩余备份: {len(self.backups)}")

        return "\n".join(report)

    def get_backup_info(self, backup_index: int) -> str:
        """获取备份详细信息"""
        if backup_index < 0 or backup_index >= len(self.backups):
            return f"无效的备份索引: {backup_index}"

        backup = self.backups[backup_index]
        manifest = backup["manifest"]

        report = []
        report.append(f"=== 备份详情: {backup['name']} ===")
        report.append(f"备份时间: {backup['backup_time']}")
        report.append(f"文件数量: {backup['file_count']:,}")
        report.append(f"总大小: {backup['total_size'] / (1024**3):.2f} GB")
        report.append(f"备份路径: {backup['path']}")

        # 显示文件类型分布
        file_types = {}
        for file_info in manifest.get("files", []):
            ext = Path(file_info["original"]).suffix or "无扩展名"
            file_types[ext] = file_types.get(ext, 0) + 1

        if file_types:
            report.append("\n文件类型分布:")
            for ext, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]:
                report.append(f"  {ext or '无扩展名'}: {count:,} 个文件")

        return "\n".join(report)

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="备份管理工具")
    parser.add_argument("--backup-root", help="备份根目录")
    parser.add_argument("--action", default="list", choices=["list", "restore", "delete", "clean", "info"],
                       help="操作类型")
    parser.add_argument("--index", type=int, help="备份索引")
    parser.add_argument("--keep", type=int, default=5, help="保留备份数量")
    parser.add_argument("--confirm", action="store_true", help="确认删除操作")
    parser.add_argument("--dry-run", action="store_true", help="模拟模式")

    args = parser.parse_args()

    manager = BackupManager(args.backup_root)

    if args.action == "list":
        print(manager.list_backups())
    elif args.action == "info":
        if args.index is None:
            print("请指定备份索引 --index")
        else:
            print(manager.get_backup_info(args.index))
    elif args.action == "restore":
        if args.index is None:
            print("请指定备份索引 --index")
        else:
            print(manager.restore_backup(args.index, args.dry_run))
    elif args.action == "delete":
        if args.index is None:
            print("请指定备份索引 --index")
        else:
            print(manager.delete_backup(args.index, args.confirm))
    elif args.action == "clean":
        print(manager.clean_old_backups(args.keep, args.confirm))

if __name__ == "__main__":
    main()