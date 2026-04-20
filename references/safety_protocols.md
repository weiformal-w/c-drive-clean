# C盘清理安全协议

## 安全原则

### 核心安全规则
1. **永远保护系统文件**
2. **用户数据必须确认**
3. **备份是强制选项**
4. **模拟模式优先**

## 保护机制

### 1. 路径保护
```python
# 永远不清理的路径
PROTECTED_PATHS = {
    "Windows",           # Windows系统文件
    "Program Files",     # 程序文件
    "Program Files (x86)", # 32位程序
    "ProgramData",       # 程序数据
    "Boot",              # 启动文件
    "EFI",               # EFI分区
    "Recovery"           # 恢复分区
}
```

### 2. 文件类型保护
```python
# 危险文件扩展名（需要特殊确认）
DANGEROUS_EXTENSIONS = {
    '.exe', '.dll', '.sys', '.drv',  # 系统文件
    '.com', '.bat', '.cmd', '.ps1'   # 脚本文件
}
```

### 3. 用户数据保护
```python
# 用户文件夹需要明确确认
USER_DATA_PATHS = {
    "Documents",    # 文档
    "Desktop",      # 桌面
    "Downloads",    # 下载
    "Pictures",     # 图片
    "Music",        # 音乐
    "Videos"        # 视频
}
```

## 安全检查流程

### 第一层：路径检查
```python
def is_safe_path(file_path):
    """检查文件路径是否安全"""
    for protected in PROTECTED_PATHS:
        if protected in str(file_path):
            return False, "保护路径"
    return True, "路径安全"
```

### 第二层：扩展名检查
```python
def is_safe_extension(file_path):
    """检查文件扩展名是否安全"""
    if file_path.suffix in DANGEROUS_EXTENSIONS:
        return False, "危险扩展名"
    return True, "扩展名安全"
```

### 第三层：用户确认
```python
def requires_user_confirmation(file_path):
    """检查是否需要用户确认"""
    for user_path in USER_DATA_PATHS:
        if user_path in str(file_path):
            return True
    return False
```

## 备份策略

### 自动备份规则
- **默认**: 启用备份
- **例外**: 用户明确禁用
- **位置**: 默认用户主目录/备份时间戳
- **格式**: 保持原始目录结构

### 备份内容
```json
{
  "backup_time": "2025-04-20T14:30:22",
  "original_path": "C:\\Users\\...\\file.tmp",
  "backup_path": "C:\\Users\\...\\CleanerBackups\\20250420_143022\\file.tmp",
  "file_hash": "sha256_checksum",
  "file_size": 1024
}
```

### 恢复机制
1. **清单验证**: 检查备份完整性
2. **路径还原**: 恢复到原始位置
3. **冲突处理**: 已存在文件跳过
4. **日志记录**: 详细恢复报告

## 模拟模式

### 工作原理
- 扫描所有文件
- 显示将要删除的文件
- 计算释放空间
- **不实际删除任何文件**

### 使用场景
- **首次使用**: 了解清理效果
- **重大清理**: 确认清理范围
- **测试验证**: 验证清理策略
- **故障排查**: 分析清理目标

## 错误处理

### 权限错误
```python
try:
    file_path.unlink()
except PermissionError:
    # 跳过文件，记录警告
    warnings.append(f"权限不足: {file_path}")
    continue
```

### 文件占用
```python
try:
    file_path.unlink()
except FileNotFoundError:
    # 文件可能被删除或移动
    continue
except Exception as e:
    # 其他错误，记录并继续
    errors.append(f"删除失败: {file_path} - {e}")
```

### 备份失败
```python
def safe_delete_with_backup(file_path):
    try:
        backup_file(file_path)
        file_path.unlink()
    except BackupError:
        # 备份失败，询问用户
        user_confirm = ask_user("备份失败，是否继续删除？")
        if user_confirm:
            file_path.unlink()
```

## 应急程序

### 清理后问题
1. **停止清理**: 立即中断清理过程
2. **检查备份**: 确认备份完整性
3. **恢复备份**: 使用最近的备份
4. **系统检查**: 验证系统功能

### 备份恢复流程
```bash
# 1. 列出可用备份
/clean-backups list

# 2. 查看备份详情
/clean-backups info --index 0

# 3. 模拟恢复
/clean-restore 0 --dry-run

# 4. 实际恢复
/clean-restore 0
```

## 安全监控

### 清理前检查
- [ ] 磁盘使用率 > 80%
- [ ] 最近系统更新
- [ ] 重要应用程序运行
- [ ] 备份空间充足

### 清理后验证
- [ ] 系统启动正常
- [ ] 应用程序运行
- [ ] 用户数据完整
- [ ] 备份可访问

## 风险评估

### 低风险清理
- 临时文件
- 浏览器缓存
- 系统缓存
- 回收站

### 中等风险清理
- 应用缓存
- 媒体缓存
- 下载文件夹
- 旧文件备份

### 高风险清理（需要特别确认）
- 大文件删除
- 用户文档
- 应用程序数据
- 系统备份文件

## 合规性

### 数据保护
- 符合GDPR要求
- 用户数据保护
- 备份加密存储
- 定期数据清理

### 审计日志
```json
{
  "timestamp": "2025-04-20T14:30:22",
  "action": "delete",
  "file": "path/to/file",
  "backup": "backup/path",
  "user": "username",
  "result": "success"
}
```

## 最佳实践

### 1. 渐进式清理
```bash
# 第一步：基础清理
/clean-run --basic --backup

# 第二步：观察系统状态
# 等待1-2天

# 第三步：扩展清理
/clean-run --full --backup
```

### 2. 备份管理
```bash
# 每月清理旧备份
/clean-backups clean --keep 3

# 定期检查备份完整性
/clean-backups info
```

### 3. 监控和日志
- 保存清理日志
- 监控系统性能
- 记录异常情况
- 定期审查清理历史