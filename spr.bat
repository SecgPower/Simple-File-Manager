:: @File    : spr.bat
:: @Author  : SECG (Hu Yerui)
:: @Version : 1.0.0
:: @Date    : 2026-02-22
:: @Copyright: Copyright (c) 2026 ASPR Studio. All rights reserved.
:: @Desc    : 启动文件管理器

@echo off
chcp 936 >nul
title SecgFileManager 启动器

set "choice="
set "NSUDO_PARAMS="
set "mode_name="
set "target_exe=SecgFileManager.exe"

echo dim r > "%temp%\sfm_choice.vbs"
echo r = MsgBox("请选择 SecgFileManager 运行权限："^&vbCrLf^&"1. TrustedInstaller (TI)"^&vbCrLf^&"2. SYSTEM"^&vbCrLf^&"3. 管理员 (当前用户高权限)",3+64,"权限选择") >> "%temp%\sfm_choice.vbs"
echo select case r >> "%temp%\sfm_choice.vbs"
echo case 6: wscript.echo 1 >> "%temp%\sfm_choice.vbs"
echo case 7: wscript.echo 2 >> "%temp%\sfm_choice.vbs"
echo case 2: wscript.echo 3 >> "%temp%\sfm_choice.vbs"
echo case else: wscript.echo 1 >> "%temp%\sfm_choice.vbs"
echo end select >> "%temp%\sfm_choice.vbs"

for /f "delims=" %%a in ('cscript //nologo "%temp%\sfm_choice.vbs" 2^>nul') do set "choice=%%a"

del /f /q "%temp%\sfm_choice.vbs" >nul 2>&1

if "%choice%"=="1" (
    set "NSUDO_PARAMS=-U:T -P:E -Wait"
    set "mode_name=TrustedInstaller (TI)"
) else if "%choice%"=="2" (
    set "NSUDO_PARAMS=-U:S -P:E -Wait"
    set "mode_name=SYSTEM"
) else if "%choice%"=="3" (
    set "NSUDO_PARAMS=-U:C -P:E -Wait"
    set "mode_name=管理员 (当前用户)"
) else (
    set "NSUDO_PARAMS=-U:T -P:E -Wait"
    set "mode_name=TrustedInstaller (TI) [默认]"
)

cls
echo ============================
echo.

if exist ".\NSudo.exe" (
    call ".\NSudo.exe" %NSUDO_PARAMS% ".\%target_exe%"
) else (
    echo 错误：找不到 NSudo.exe！
    pause
    exit /b 1
)

:WAIT_LOOP
tasklist /FI "IMAGENAME eq %target_exe%" /FI "STATUS eq RUNNING" 2>NUL | find /I "%target_exe%" >NUL
if errorlevel 1 (
    timeout /t 2 /nobreak >nul
    tasklist /FI "IMAGENAME eq %target_exe%" 2>NUL | find /I "%target_exe%" >NUL
    if errorlevel 1 (
        echo.
        echo %target_exe% 已退出
        timeout /t 2 /nobreak >nul
        
        set "task_name=SFM_Clean_%random%"
        set "runtime_dir=%cd%"
        schtasks /create /tn "%task_name%" /tr "cmd /c rmdir /s /q ""%runtime_dir%""" /sc once /st %time:~0,2%:%time:~3,2%:%time:~6,2% /sd %date:~0,4%-%date:~5,2%-%date:~8,2% /ru "SYSTEM" /f >nul 2>&1
        schtasks /run /tn "%task_name%" >nul 2>&1
        schtasks /delete /tn "%task_name%" /f >nul 2>&1
    ) else (
        goto WAIT_LOOP
    )
) else (
    timeout /t 1 /nobreak >nul
    goto WAIT_LOOP
)

exit /b 0