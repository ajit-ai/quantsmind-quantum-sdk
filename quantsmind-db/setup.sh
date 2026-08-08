#!/bin/bash
# QuantsMind Database System Setup Script for Linux
# This script sets up the development environment and builds the project

set -e

echo "========================================"
echo "QuantsMind Database System Setup"
echo "========================================"
echo ""

# Check if Rust is installed
echo "Checking for Rust..."
if ! command -v rustc &> /dev/null; then
    echo "ERROR: Rust is not installed"
    echo "Please install Rust from https://rustup.rs/"
    echo "Run: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
    exit 1
fi
echo "Rust is installed"
rustc --version
echo ""

# Check if Node.js is installed
echo "Checking for Node.js..."
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed"
    echo "Please install Node.js from https://nodejs.org/"
    echo "On Ubuntu/Debian: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt-get install -y nodejs"
    exit 1
fi
echo "Node.js is installed"
node --version
echo ""

# Check if npm is installed
echo "Checking for npm..."
if ! command -v npm &> /dev/null; then
    echo "ERROR: npm is not installed"
    exit 1
fi
echo "npm is installed"
npm --version
echo ""

# Check for Tauri dependencies on Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Checking for Tauri dependencies..."
    if ! dpkg -l | grep -q libwebkit2gtk-4.0-dev; then
        echo "Installing Tauri dependencies..."
        sudo apt-get update
        sudo apt-get install -y build-essential libwebkit2gtk-4.0-dev libssl-dev libgtk-3-dev libayatana-appindicator3-dev librsvg2-dev
    fi
    echo "Tauri dependencies installed"
    echo ""
fi

echo "========================================"
echo "Building QuantsMind Engine (Rust)"
echo "========================================"
cd quantsmind-engine
cargo build --release
echo "QuantsMind Engine built successfully"
cd ..
echo ""

echo "========================================"
echo "Installing QuantsMind Studio Dependencies"
echo "========================================"
cd quantsmind-studio
npm install
echo "Dependencies installed successfully"
cd ..
echo ""

echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "To run the QuantsMind Engine (CLI):"
echo "  cd quantsmind-engine"
echo "  cargo run --release"
echo ""
echo "To run the QuantsMind Studio (GUI):"
echo "  cd quantsmind-studio"
echo "  npm run tauri dev"
echo ""
echo "For production builds:"
echo "  Engine: cd quantsmind-engine && cargo build --release"
echo "  Studio: cd quantsmind-studio && npm run tauri build"
echo ""
