---
name: c-drive-cleaner
description: Windows C盘清理智能助手。当用户需要清理C盘、释放磁盘空间、删除垃圾文件、清理系统临时文件、清理应用缓存、优化磁盘空间或任何Windows系统清理相关任务时使用此skill。支持安全清理、模拟预览、备份恢复等多种清理模式。即使没有明确提到"清理"，只要涉及磁盘空间管理、垃圾文件处理、系统优化等需求，都应该使用此skill。
---

# Windows C盘清理助手

这是一个专用于Windows系统C盘清理的智能助手，基于经过验证的清理策略和安全机制。

## 触发条件

当用户提到以下需求时，应该使用此skill：
- 清理C盘/磁盘清理/释放空间
- 删除垃圾文件/临时文件/缓存
- 系统清理/系统优化
- C盘空间不足/磁盘红区
- 应用缓存清理/浏览器缓存清理
- Windows更新缓存清理
- 大文件扫描/空间占用分析
- 任何涉及Windows磁盘空间管理的需求

## 核心功能

### 1. 磁盘分析
- 扫描C盘空间使用情况
- 识别临时文件、缓存、垃圾文件
- 定位大文件（>100MB）
- 分析各类文件占用空间

### 2. 安全清理
支持多种清理项目：
- **基础清理**: 临时文件、回收站、浏览器缓存、系统日志
- **扩展清理**: 预读取文件、旧Windows文件、错误报告、内存转储
- **应用缓存**: Adobe、Office、Windows Media Player、VLC、Spotify等
- **系统清理**: DNS缓存、网络缓存、打印机临时文件、Windows Defender/Store/OneDrive缓存
- **大文件扫描**: 快速定位大文件供用户确认删除

### 3. 安全特性
- **多重安全检查**: 防止误删系统文件和重要数据
- **备份恢复**: 删除前自动备份，支持一键恢复
- **模拟模式**: 预览将要删除的文件，不实际删除
- **用户确认**: 重要操作前需明确获得用户同意

## 使用方法

这个skill提供了多种使用方式，从简单的命令到完整的清理流程。

### 方式1: 直接使用Python脚本（推荐）

#### 分析C盘状态
```bash
# 基础分析
python scripts/analyzer.py

# 深度分析（包括大文件）
python scripts/analyzer.py --large-files --min-size 100

# 快速分析
python scripts/analyzer.py --quick
```

#### 清理C盘
```bash
# 模拟模式（推荐首次使用）
python scripts/cleaner.py --basic --dry-run

# 基础清理（安全）
python scripts/cleaner.py --basic --backup

# 完整清理
python scripts/cleaner.py --full --backup

# 激进清理
python scripts/cleaner.py --aggressive --backup
```

#### 扫描大文件
```bash
# 扫描大于100MB的文件
python scripts/scanner.py --min-size 100 --limit 20

# 扫描大于200MB的文件，显示前15个
python scripts/scanner.py --min-size 200 --limit 15 --suggest
```

#### 备份管理
```bash
# 列出所有备份
python scripts/backup_manager.py --action list

# 恢复最近的备份
python scripts/backup_manager.py --action restore --index 0

# 清理旧备份
python scripts/backup_manager.py --action clean --keep 3 --confirm
```

### 方式2: 使用批处理文件（Windows）

```bash
# 进入skill目录
cd C:\Users\lenovo\.claude\skills\c-drive-cleaner

# 分析C盘
.\clean.cmd analyze

# 深度分析
.\clean.cmd analyze --large-files

# 模拟清理
.\clean.cmd clean --basic --dry-run

# 实际清理
.\clean.cmd clean --basic

# 扫描大文件
.\clean.cmd scan --min-size 200
```

### 方式3: 通过Agent触发（主要使用方式）

当用户提到以下需求时，这个skill会自动触发：
- "我的C盘满了/红了"
- "清理C盘/释放空间"
- "删除垃圾文件/临时文件"
- "系统清理/优化"
- "大文件分析"
- "磁盘空间管理"

Agent会自动执行适当的清理流程。

## 快速开始指南

### 推荐的工作流程

#### 1. 首次使用（安全第一）
```bash
# 第一步：分析C盘状态
python scripts/analyzer.py --quick

# 第二步：预览清理效果
python scripts/cleaner.py --basic --dry-run

# 第三步：确认后实际清理
python scripts/cleaner.py --basic --backup
```

#### 2. 日常维护
```bash
# 每月例行清理
python scripts/analyzer.py --large-files
python scripts/cleaner.py --full --backup
```

#### 3. 应急清理（C盘红了）
```bash
# 紧急释放空间
python scripts/cleaner.py --aggressive --backup
```

### 标准清理流程
1. **分析阶段**: 扫描系统，识别可清理文件
2. **预览阶段**: 显示将要清理的文件类型和空间
3. **确认阶段**: 获得用户明确同意
4. **备份阶段**: 创建备份（如启用）
5. **清理阶段**: 执行删除操作
6. **报告阶段**: 显示清理结果和释放空间

### 模拟模式流程
1. **扫描阶段**: 识别目标文件但不删除
2. **预览阶段**: 详细显示将要删除的文件列表
3. **报告阶段**: 显示预计释放的空间

### 应急恢复流程
1. **识别备份**: 列出可用备份
2. **选择备份**: 用户选择要恢复的备份
3. **恢复操作**: 将文件恢复到原位置
4. **验证结果**: 确认恢复成功

## 安全规则

### 必须遵守
- 删除任何文件前必须扫描并告知用户
- 系统关键文件（Windows、Program Files等）永远不删除
- 用户文档文件夹（Documents、Desktop等）需要明确确认
- 提供备份功能，除非用户明确拒绝

### 需要用户确认的情况
- 删除超过100MB的单个文件
- 清理用户文件夹中的内容
- 清理应用程序数据
- 执行激进清理模式

## 使用指南

### 首次使用建议
1. 先使用 `/clean-analyze --deep` 了解磁盘状态
2. 使用 `/clean-run --dry-run` 预览清理效果
3. 从 `/clean-run --basic` 开始保守清理
4. 确认无问题后逐步增加清理范围

### 常用场景
- **C盘红了**: `/clean-analyze` → `/clean-run --backup`
- **释放空间**: `/clean-run --full --backup`
- **快速清理**: `/clean-run --basic`
- **清理前预览**: `/clean-run --dry-run`
- **找大文件**: `/clean-scan --size 200 --top 10`

## 错误处理

### 常见问题
- **权限不足**: 建议以管理员身份运行
- **文件占用**: 跳过占用文件，继续其他清理
- **备份失败**: 警告用户，询问是否继续
- **空间不足**: 确保备份位置有足够空间

## 输出格式

### 分析报告
```
=== C盘分析报告 ===
总空间: 500 GB
已使用: 450 GB (90%)
可用空间: 50 GB

可清理空间估算:
- 临时文件: 2.5 GB
- 浏览器缓存: 1.2 GB
- 系统缓存: 3.8 GB
总计可释放: ~7.5 GB

大文件 (>100MB): 15 个文件，共 8.2 GB
```

### 清理报告
```
=== 清理完成 ===
清理模式: 基础清理
备份位置: D:\CleanerBackups\20250420_143022

删除文件:
- 临时文件: 2,345 个文件 (2.5 GB)
- 浏览器缓存: 890 个文件 (1.2 GB)
释放空间: 3.7 GB

耗时: 2分15秒
状态: ✅ 成功
```

## 技术说明

此skill基于Python实现，利用Windows系统API和文件系统操作。核心脚本位于 `scripts/` 目录，包括：
- `analyzer.py`: 磁盘分析脚本
- `cleaner.py`: 清理执行脚本  
- `backup_manager.py`: 备份管理脚本
- `scanner.py`: 大文件扫描脚本

所有操作都经过安全检查，确保不会影响系统稳定性。