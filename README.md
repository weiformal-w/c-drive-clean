# C盘清理助手 Skill

基于Windows C盘清理工具的智能助手skill，帮助用户安全清理系统垃圾文件、临时文件和应用缓存。

## 功能特性

### 🎯 核心功能
- **磁盘分析**: 扫描C盘空间使用情况，识别垃圾文件
- **安全清理**: 多种清理模式，从基础到深度清理
- **备份恢复**: 自动备份删除的文件，支持一键恢复
- **大文件扫描**: 快速定位占用大空间的文件

### 🔒 安全特性
- **多重安全检查**: 防止误删系统文件
- **模拟模式**: 预览将要删除的文件
- **备份机制**: 删除前自动备份
- **用户确认**: 重要操作前需明确同意

### 🚀 斜杠命令
- `/clean-analyze`: 分析C盘状态
- `/clean-run`: 执行清理操作
- `/clean-restore`: 恢复备份文件
- `/clean-backups`: 管理备份文件
- `/clean-scan`: 扫描大文件

## 使用方法

### 基本使用
1. **分析磁盘**: `/clean-analyze`
2. **预览清理**: `/clean-run --dry-run`
3. **执行清理**: `/clean-run --backup`

### 清理模式
- `--basic`: 基础清理（临时文件、浏览器缓存）
- `--full`: 完整清理（包括应用缓存）
- `--aggressive`: 激进清理（更多文件类型）

### 安全选项
- `--dry-run`: 模拟模式，仅预览
- `--backup`: 启用备份（推荐）
- `--no-backup`: 禁用备份
- `--backup-path`: 自定义备份位置

## 安装说明

### 系统要求
- Windows 7/8/10/11
- Python 3.6+
- 建议管理员权限

### 安装步骤
1. 将此skill目录复制到Claude Code的skills目录
2. 重启Claude Code
3. skill会自动加载

## 文件结构

```
c-drive-cleaner/
├── SKILL.md              # Skill主文件
├── scripts/              # 执行脚本
│   ├── analyzer.py      # 磁盘分析脚本
│   ├── cleaner.py       # 清理执行脚本
│   ├── backup_manager.py # 备份管理脚本
│   └── scanner.py       # 大文件扫描脚本
├── references/           # 参考文档
│   ├── usage_guide.md   # 使用指南
│   └── safety_protocols.md # 安全协议
├── evals/               # 测试评估
│   └── evals.json      # 测试用例
└── README.md            # 本文件
```

## 使用场景

### 日常清理
```bash
# 每月例行清理
/clean-analyze
/clean-run --full --backup
```

### 应急清理
```bash
# C盘红了
/clean-analyze --deep
/clean-run --aggressive --backup
```

### 大文件分析
```bash
# 找出占用空间的文件
/clean-scan --size 200 --top 10
```

## 安全说明

### 保护机制
- 系统关键文件夹自动保护
- 可执行文件需要确认
- 用户数据文件夹特别处理
- 所有操作都有备份选项

### 应急恢复
```bash
# 如果清理后出现问题
/clean-backups list
/clean-restore 0
```

## 技术架构

### 脚本功能
- **analyzer.py**: 磁盘使用分析，垃圾文件识别
- **cleaner.py**: 安全清理执行，备份管理
- **backup_manager.py**: 备份创建、恢复、清理
- **scanner.py**: 大文件扫描，空间分析

### 设计原则
- 安全第一：多重检查机制
- 用户控制：所有操作需确认
- 可逆操作：完整备份恢复
- 渐进清理：从安全到激进

## 注意事项

### ⚠️ 重要提醒
1. 首次使用建议从 `--basic` 模式开始
2. 推荐始终启用 `--backup` 选项
3. 清理前确保重要数据已备份
4. 系统文件夹（Windows, Program Files）永远不删除

### 不适合场景
- 服务器环境生产清理
- 数据库文件清理
- 虚拟机磁盘文件
- 开发项目目录

## 维护和更新

### 版本历史
- v1.0: 初始版本，基础清理功能
- 未来计划：定时清理、详细报告、多语言支持

### 问题反馈
如遇到问题，请：
1. 检查错误日志
2. 使用模拟模式测试
3. 恢复备份重试
4. 查看安全协议文档

## 许可证
MIT License

## 贡献
欢迎贡献改进建议和代码！