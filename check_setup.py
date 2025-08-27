#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@auther guxiang
@date 2025-08-27
环境检查脚本
"""

import os
import subprocess
import sys


def check_file():
    """检查PDF文件"""
    pdf_path = "data/NLC511-004031011023755-34557_駢文通義.pdf"
    if os.path.exists(pdf_path):
        size = os.path.getsize(pdf_path)
        print(f"✅ PDF文件存在: {pdf_path}")
        print(f"📊 文件大小: {size / 1024 / 1024:.2f} MB")
        return True
    else:
        print(f"❌ PDF文件不存在: {pdf_path}")
        return False


def check_dependencies():
    """检查依赖安装状态"""
    deps = [
        'fitz',
        'pytesseract',
        'PIL',
        'reportlab',
        'cv2'
    ]
    
    results = {}
    for dep in deps:
        try:
            __import__(dep)
            results[dep] = True
            print(f"✅ {dep}")
        except ImportError:
            results[dep] = False
            print(f"❌ {dep}")
    
    return all(results.values())


def check_tesseract():
    """检查Tesseract安装"""
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✅ Tesseract: {version}")
            return True
        else:
            print("❌ Tesseract未安装")
            return False
    except FileNotFoundError:
        print("❌ Tesseract未找到")
        print("💡 安装命令:")
        print("   macOS: brew install tesseract tesseract-lang")
        print("   Ubuntu: sudo apt-get install tesseract-ocr-chi-sim")
        return False


def main():
    print("🔍 环境检查")
    print("=" * 30)
    
    print("\n1️⃣ 文件检查:")
    file_ok = check_file()
    
    print("\n2️⃣ Python依赖:")
    deps_ok = check_dependencies()
    
    print("\n3️⃣ OCR引擎:")
    tesseract_ok = check_tesseract()
    
    print("\n" + "=" * 30)
    print("📊 检查结果:")
    print(f"   PDF文件: {'✅' if file_ok else '❌'}")
    print(f"   Python依赖: {'✅' if deps_ok else '❌'}")
    print(f"   OCR引擎: {'✅' if tesseract_ok else '❌'}")
    
    if all([file_ok, deps_ok, tesseract_ok]):
        print("\n🎉 环境就绪！可以开始转换")
    else:
        print("\n⚠️  需要解决上述问题")


if __name__ == "__main__":
    main()