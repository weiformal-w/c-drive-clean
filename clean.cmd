@echo off
REM C盘清理助手 - Windows批处理包装
REM 使用方法: clean.cmd [命令] [选项]

set SCRIPT_DIR=%~dp0scripts
set PYTHON_CMD=python

REM 检查Python是否可用
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 找不到Python，请先安装Python 3.6+
    pause
    exit /b 1
)

REM 解析命令
if "%1"=="" goto show_help
if "%1"=="analyze" goto analyze
if "%1"=="clean" goto clean
if "%1"=="scan" goto scan
if "%1"=="backup" goto backup
if "%1"=="help" goto show_help
goto show_help

:analyze
shift
%PYTHON_CMD% "%SCRIPT_DIR%\analyzer.py" %*
goto end

:clean
shift
%PYTHON_CMD% "%SCRIPT_DIR%\cleaner.py" %*
goto end

:scan
shift
%PYTHON_CMD% "%SCRIPT_DIR%\scanner.py" %*
goto end

:backup
shift
%PYTHON_CMD% "%SCRIPT_DIR%\backup_manager.py" %*
goto end

:show_help
echo C盘清理助手 - 使用方法
echo.
echo 基本命令:
echo   clean.cmd analyze          分析C盘状态
echo   clean.cmd analyze --deep   深度分析(包括大文件)
echo.
echo   clean.cmd clean --basic    基础清理
echo   clean.cmd clean --dry-run  预览清理效果
echo   clean.cmd clean --full     完整清理
echo.
echo   clean.cmd scan             扫描大文件
echo   clean.cmd scan --min-size 200 --limit 15
echo.
echo   clean.cmd backup           管理备份
echo.
echo 详细选项请运行: clean.cmd [命令] --help
echo.

:end