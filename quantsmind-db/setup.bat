@echo off
REM QuantsMind Database System Setup Script for Windows
REM This script sets up the development environment and builds the project

echo ========================================
echo QuantsMind Database System Setup
echo ========================================
echo.

REM Check if Rust is installed
echo Checking for Rust...
rustc --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Rust is not installed or not in PATH
    echo Please install Rust from https://rustup.rs/
    pause
    exit /b 1
)
echo Rust is installed
rustc --version
echo.

REM Check if Node.js is installed
echo Checking for Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)
echo Node.js is installed
node --version
echo.

REM Check if npm is installed
echo Checking for npm...
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: npm is not installed or not in PATH
    pause
    exit /b 1
)
echo npm is installed
npm --version
echo.

echo ========================================
echo Building QuantsMind Engine (Rust)
echo ========================================
cd quantsmind-engine
cargo build --release
if %errorlevel% neq 0 (
    echo ERROR: Failed to build QuantsMind Engine
    pause
    exit /b 1
)
echo QuantsMind Engine built successfully
cd ..
echo.

echo ========================================
echo Installing QuantsMind Studio Dependencies
echo ========================================
cd quantsmind-studio
call npm install
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Node.js dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully
cd ..
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To run the QuantsMind Engine (CLI):
echo   cd quantsmind-engine
echo   cargo run --release
echo.
echo To run the QuantsMind Studio (GUI):
echo   cd quantsmind-studio
echo   npm run tauri dev
echo.
echo For production builds:
echo   Engine: cd quantsmind-engine && cargo build --release
echo   Studio: cd quantsmind-studio && npm run tauri build
echo.
pause
