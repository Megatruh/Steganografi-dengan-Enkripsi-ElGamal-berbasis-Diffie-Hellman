#!/bin/bash
# Script untuk clean restart aplikasi Streamlit

echo "Cleaning up Python cache and Streamlit cache..."
echo "=============================================="

# Hapus Python cache
rm -rf __pycache__
rm -rf .streamlit

echo "✓ Python cache cleared"
echo "✓ Streamlit cache cleared"
echo ""
echo "=============================================="
echo "Silakan jalankan: streamlit run app.py"
echo "=============================================="