#!/bin/bash

# Start the React frontend development server

echo "🚀 Starting Coding Crew Frontend..."

cd web/frontend

# Clean install with legacy peer deps
echo "📦 Installing dependencies..."
rm -rf node_modules package-lock.json
npm install --legacy-peer-deps

# Start development server
echo "🌐 Starting development server on http://localhost:3000"
npm start