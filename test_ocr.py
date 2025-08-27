#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@auther guxiang
@date 2025-08-27
OCR功能测试脚本
"""

import os
import fitz
import tempfile
import shutil


def test_pdf_info():
    """测试PDF基本信息"""
    pdf_path = "data/NLC511-004031011023755-34557_駢文通義.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ 文件不存在: {pdf_path}")
        return False
    
    try:
        doc = fitz.open(pdf_path)
        print(f"✅ PDF文件: {pdf_path}")
        print(f"📄 页数: {len(doc)}")
        print(f"📊 文件大小: {os.path.getsize(pdf_path) / 1024 / 1024:.2f} MB")
        
        # 检查第一页
        page = doc[0]
        text = page.get_text().strip()
        images = page.get_images()
        
        print(f"🔍 第一页文本长度: {len(text)}")
        print(f"🖼️  第一页图像数量: {len(images)}")
        
        if len(text) < 10 and len(images) > 0:
            print("📋 结论: 这是扫描版PDF，需要OCR处理")
        else:
            print("📋 结论: 这是文字版PDF，已有可编辑文字")
        
        doc.close()
        return True
        
    except Exception as e:
        print(f"❌ 读取PDF失败: {e}")
        return False


def test_tesseract():
    """测试Tesseract OCR"""
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract版本: {version}")
        return True
    except Exception as e:
        print(f"❌ Tesseract未安装或不可用: {e}")
        print("💡 安装命令:")
        print("   macOS: brew install tesseract tesseract-lang")
        print("   Ubuntu: sudo apt-get install tesseract-ocr-chi-sim")
        return False


def test_page_extraction():
    """测试页面提取功能"""
    pdf_path = "data/NLC511-004031011023755-34557_駢文通義.pdf"
    
    if not os.path.exists(pdf_path):
        return False
    
    temp_dir = tempfile.mkdtemp()
    try:
        doc = fitz.open(pdf_path)
        
        # 提取第一页测试
        page = doc[0]
        mat = fitz.Matrix(2.0, 2.0)  # 2x分辨率
        pix = page.get_pixmap(matrix=mat)
        
        img_path = os.path.join(temp_dir, "test_page.png")
        pix.save(img_path)
        
        if os.path.exists(img_path):
            print(f"✅ 页面提取成功: {img_path}")
            print(f"📐 图像尺寸: {pix.width}x{pix.height}")
            return True
        else:
            print("❌ 页面提取失败")
            return False
            
    except Exception as e:
        print(f"❌ 页面提取异常: {e}")
        return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    """主测试函数"""
    print("🔍 PDF OCR转换器测试")
    print("=" * 50)
    
    # 测试1: PDF文件检查
    print("\n1️⃣ 检查PDF文件...")
    pdf_ok = test_pdf_info()
    
    # 测试2: Tesseract检查
    print("\n2️⃣ 检查OCR引擎...")
    tesseract_ok = test_tesseract()
    
    # 测试3: 页面提取
    print("\n3️⃣ 测试页面提取...")
    extraction_ok = test_page_extraction()
    
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")
    print(f"   PDF文件: {'✅' if pdf_ok else '❌'}")
    print(f"   OCR引擎: {'✅' if tesseract_ok else '❌'}")
    print(f"   页面提取: {'✅' if extraction_ok else '❌'}")
    
    if all([pdf_ok, tesseract_ok, extraction_ok]):
        print("\n🎉 所有测试通过！可以运行转换器")
        print("   python3 pdf_ocr_converter.py")
    else:
        print("\n⚠️  部分测试失败，请检查上述问题")


if __name__ == "__main__":
    main()