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

### 🎯 适用场景
这个skill会在以下情况自动触发：
- "清理C盘" / "释放空间"
- "删除垃圾文件" / "清理临时文件"
- "系统清理" / "磁盘优化"
- "C盘红了" / "空间不足"
- "大文件分析" / "空间占用"

## 使用方法

### 方式1：通过Claude Code（推荐）
只需要告诉Claude你需要清理C盘，skill会自动触发：
- "清理C盘"
- "释放磁盘空间" 
- "C盘红了"
- "删除临时文件"
- "分析磁盘占用"

Claude会自动执行合适的清理流程，无需手动输入命令。

### 方式2：直接使用Python脚本
```bash
# 分析C盘状态
python scripts/analyzer.py

# 深度分析（包括大文件）
python scripts/analyzer.py --large-files --min-size 100

# 模拟清理（安全预览）
python scripts/cleaner.py --basic --dry-run

# 实际清理并备份
python scripts/cleaner.py --basic --backup

# 扫描大文件
python scripts/scanner.py --min-size 100 --limit 20

# 管理备份
python scripts/backup_manager.py --action list
python scripts/backup_manager.py --action restore --index 0
```

### 方式3：使用批处理文件（Windows）
```bash
# 进入skill目录
cd C:\Users\lenovo\.claude\skills\c-drive-cleaner

# 分析C盘
.\clean.cmd analyze

# 模拟清理
.\clean.cmd clean --basic --dry-run

# 实际清理
.\clean.cmd clean --basic

# 扫描大文件
.\clean.cmd scan --min-size 200
```

### 清理模式参数
- `--basic`: 基础清理（临时文件、浏览器缓存）
- `--full`: 完整清理（包括应用缓存）
- `--aggressive`: 激进清理（更多文件类型）

### 安全选项参数
- `--dry-run`: 模拟模式，仅预览不删除
- `--backup`: 启用备份（推荐）
- `--actual-clean`: 实际执行清理（默认是模拟模式）

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
python scripts/analyzer.py --large-files
python scripts/cleaner.py --full --backup --actual-clean
```

### 应急清理
```bash
# C盘红了 - 紧急释放空间
python scripts/cleaner.py --aggressive --backup --actual-clean
```

### 大文件分析
```bash
# 找出占用空间的文件
python scripts/scanner.py --min-size 100 --limit 20 --suggest
```

## 安全说明

### 保护机制
- 系统关键文件夹自动保护
- 可执行文件需要确认
- 用户数据文件夹特别处理
- 所有操作都有备份选项

### 应急恢复
```bash
# 查看备份列表
python scripts/backup_manager.py --action list

# 恢复最新备份
python scripts/backup_manager.py --action restore --index 0

# 清理旧备份，保留最近3个
python scripts/backup_manager.py --action clean --keep 3 --confirm
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