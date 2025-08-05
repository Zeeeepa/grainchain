#!/bin/bash

echo "🚀 STARTING REAL GRAINCHAIN DASHBOARD..."
echo "=========================================="

cd "$(dirname "$0")"

echo "✅ Loading comprehensive dashboard with all features..."
echo "🔥 Features: Dashboard, Providers, Terminal, Files, Snapshots, Settings"
echo "🏗️ Architecture: 25+ state properties, SQLite DB, Fernet encryption"
echo ""

echo "🌐 Starting Reflex server..."
echo "   Frontend: http://localhost:3000"
echo "   Backend: http://localhost:8000"
echo ""

# Start the Reflex development server
reflex run

echo "🎯 REAL COMPREHENSIVE DASHBOARD READY!"
