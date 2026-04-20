# C盘清理Skill使用指南

## 快速开始

### 基本使用
1. **分析磁盘状态**
   ```
   /clean-analyze
   ```

2. **安全清理（推荐首次使用）**
   ```
   /clean-run --basic --backup --dry-run
   ```

3. **实际清理**
   ```
   /clean-run --basic --backup
   ```

### 常用场景

#### C盘空间不足
```bash
# 第一步：深度分析
/clean-analyze --deep

# 第二步：预览清理效果
/clean-run --full --dry-run

# 第三步：执行清理
/clean-run --full --backup
```

#### 快速清理临时文件
```bash
/clean-run --basic --no-backup
```

#### 查找大文件
```bash
# 扫描大于200MB的文件
/clean-scan --size 200 --top 15

# 扫描当前目录
/clean-scan /path/to/directory --size 50
```

#### 备份管理
```bash
# 查看所有备份
/clean-backups list

# 恢复最近的备份
/clean-restore

# 清理旧备份（保留最近3个）
/clean-backups clean --keep 3
```

## 清理模式详解

### 基础清理 (--basic)
- **临时文件**: 系统临时文件夹
- **浏览器缓存**: Chrome, Edge等浏览器缓存
- **系统缓存**: Windows更新缓存、预读取文件
- **安全性**: 最安全，只清理明确可删除的文件
- **建议**: 日常维护使用

### 完整清理 (--full)
- **包含**: 基础清理的所有内容
- **额外清理**:
  - 回收站
  - 应用程序缓存 (Adobe, Office等)
  - 媒体播放器缓存
  - Windows Defender/Store缓存
  - OneDrive缓存
- **风险**: 极低，但会清除应用缓存可能影响应用启动速度
- **建议**: 定期深度清理使用

### 激进清理 (--aggressive)
- **包含**: 完整清理的所有内容
- **额外清理**:
  - 旧Windows文件
  - 服务包备份
  - 内存转储文件
  - 错误报告
  - 字体缓存
- **风险**: 低，但可能影响系统故障排查
- **建议**: 确认系统稳定后使用

## 安全特性

### 备份系统
```bash
# 启用备份（推荐）
/clean-run --backup

# 禁用备份（仅临时文件）
/clean-run --basic --no-backup

# 自定义备份位置
/clean-run --backup --backup-path "D:/MyBackups"
```

### 模拟模式
```bash
# 预览将删除的文件
/clean-run --dry-run

# 查看大文件但不删除
/clean-scan --dry-run
```

### 恢复功能
```bash
# 列出可用备份
/clean-backups list

# 查看备份详情
/clean-backups info --index 0

# 恢复指定备份
/clean-restore 0
```

## 高级用法

### 定时清理
建议每月执行一次：
```bash
# 每月1日执行
/clean-analyze --deep
/clean-run --full --backup
```

### 批量操作
```bash
# 分析 → 预览 → 清理
/clean-analyze && /clean-run --dry-run && /clean-run --backup
```

### 监控空间
```bash
# 定期检查
/clean-analyze | grep "可用空间"
```

## 故障排除

### 权限问题
如果遇到权限不足：
1. 以管理员身份运行命令提示符
2. 或者右键点击"以管理员身份运行"

### 文件占用
如果文件被占用无法删除：
- 工具会自动跳过占用文件
- 不会中断清理过程
- 在报告中显示失败的文件

### 备份空间不足
如果备份空间不足：
1. 使用 `--no-backup` 跳过备份
2. 或者指定其他驱动器：`--backup-path "D:/Backups"`
3. 或者先清理旧备份：`/clean-backups clean`

### 清理后问题
如果清理后系统异常：
1. 立即使用 `/clean-restore` 恢复备份
2. 检查备份列表：`/clean-backups list`
3. 恢复最近的备份

## 最佳实践

### 新手建议
1. **首次使用**: 从 `--basic --backup --dry-run` 开始
2. **逐步增加**: 确认无问题后使用 `--full`
3. **定期备份**: 保持备份功能开启
4. **监控系统**: 清理后检查应用运行状态

### 高级用户
1. **自动化**: 结合任务计划程序定时清理
2. **脚本化**: 编写批处理脚本批量操作
3. **监控**: 使用日志记录清理历史
4. **优化**: 根据使用情况调整清理策略

### 企业环境
1. **测试**: 先在测试环境验证
2. **审批**: 清理前获得IT部门批准
3. **备份**: 使用网络共享备份
4. **日志**: 保留详细清理记录

## 系统要求

- **操作系统**: Windows 7/8/10/11
- **Python版本**: 3.6+
- **权限**: 建议管理员权限
- **磁盘空间**: 备份需要额外空间

## 注意事项

### ⚠️ 重要警告
- 永远不要删除 `C:\Windows` 中的文件
- 不要清理 `Program Files` 目录
- 用户文档文件夹需特别小心
- 清理前确保重要数据已备份

### ⚠️ 不建议清理
- 正在运行的程序相关文件
- 数据库文件
- 虚拟机磁盘文件
- 开发项目文件

## 技术支持

如果遇到问题：
1. 检查错误日志
2. 使用 `--dry-run` 模式测试
3. 恢复备份并重试
4. 查看详细报告分析问题