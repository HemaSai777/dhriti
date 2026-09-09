#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo '==============================================='
echo '  SAHAYA - Render Build Script                 '
echo '==============================================='

# 1. Install Backend Python Dependencies
echo '[1/2] Installing backend Python packages...'
pip install --upgrade pip
pip install -r backend/requirements.txt

# 2. Build Frontend Assets
echo '[2/2] Building React + Vite frontend...'
cd frontend
npm install
npm run build
cd ..

echo '=== Build finished successfully! ==='
