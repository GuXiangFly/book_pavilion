#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@auther guxiang
@date 2025-08-27
PDF扫描转文字版转换器
将扫描版PDF转换为可编辑的文字版PDF
"""

import os
import sys
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import cv2
import numpy as np
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import tempfile
import shutil


class PDFOCRConverter:
    """PDF OCR转换器类"""
    
    def __init__(self, input_pdf_path, output_pdf_path=None, lang='chi_sim+eng'):
        """
        初始化转换器
        
        Args:
            input_pdf_path: 输入PDF文件路径
            output_pdf_path: 输出PDF文件路径，如果为None则自动生成
            lang: OCR语言，中文简体+英文
        """
        self.input_pdf_path = input_pdf_path
        self.output_pdf_path = output_pdf_path or self._generate_output_path()
        self.lang = lang
        
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        
    def _generate_output_path(self):
        """生成输出文件路径"""
        base_name = os.path.splitext(os.path.basename(self.input_pdf_path))[0]
        return f"{base_name}_ocr.pdf"
    
    def _preprocess_image(self, image_path):
        """预处理图像以提高OCR准确性"""
        # 读取图像
        img = cv2.imread(image_path)
        
        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 应用高斯模糊去噪
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 自适应阈值二值化
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
        
        # 保存预处理后的图像
        temp_path = os.path.join(self.temp_dir, f"preprocessed_{os.path.basename(image_path)}")
        cv2.imwrite(temp_path, thresh)
        
        return temp_path
    
    def _extract_images_from_pdf(self):
        """从PDF中提取图像"""
        doc = fitz.open(self.input_pdf_path)
        image_paths = []
        
        print(f"正在处理PDF，共{len(doc)}页...")
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # 设置DPI为300以获得更好的OCR效果
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)
            
            # 保存图像
            img_path = os.path.join(self.temp_dir, f"page_{page_num + 1}.png")
            pix.save(img_path)
            image_paths.append(img_path)
            
            print(f"已提取第{page_num + 1}页图像")
        
        doc.close()
        return image_paths
    
    def _perform_ocr(self, image_path):
        """对图像执行OCR识别"""
        # 预处理图像
        preprocessed_path = self._preprocess_image(image_path)
        
        # 执行OCR
        image = Image.open(preprocessed_path)
        text = pytesseract.image_to_string(
            image, 
            lang=self.lang,
            config='--psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz，。：、；！？""''（）【】《》〈〉""''·—…¥£€'
        )
        
        return text.strip()
    
    def _create_text_pdf(self, texts, image_paths):
        """创建包含识别文字的新PDF"""
        c = canvas.Canvas(self.output_pdf_path, pagesize=A4)
        width, height = A4
        
        # 设置中文字体（使用系统默认字体）
        try:
            pdfmetrics.registerFont(TTFont('SimSun', '/System/Library/Fonts/PingFang.ttc'))
            font_name = 'SimSun'
        except:
            font_name = 'Helvetica'
        
        for i, (text, img_path) in enumerate(zip(texts, image_paths)):
            if i > 0:
                c.showPage()
            
            # 设置字体和大小
            c.setFont(font_name, 12)
            
            # 计算文本位置
            x = 50
            y = height - 50
            line_height = 20
            max_width = width - 100
            
            # 分割文本为多行
            lines = text.split('\n')
            
            for line in lines:
                if not line.strip():
                    y -= line_height
                    continue
                
                # 处理长行
                words = line.split()
                current_line = ""
                
                for word in words:
                    test_line = current_line + " " + word if current_line else word
                    if c.stringWidth(test_line, font_name, 12) < max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            c.drawString(x, y, current_line)
                            y -= line_height
                        current_line = word
                
                if current_line:
                    c.drawString(x, y, current_line)
                    y -= line_height
                
                if y < 50:
                    c.showPage()
                    y = height - 50
        
        c.save()
    
    def convert(self):
        """执行完整的转换流程"""
        try:
            print("开始PDF OCR转换...")
            
            # 提取图像
            image_paths = self._extract_images_from_pdf()
            
            # 执行OCR
            texts = []
            for i, img_path in enumerate(image_paths):
                print(f"正在识别第{i + 1}页文字...")
                text = self._perform_ocr(img_path)
                texts.append(text)
                print(f"第{i + 1}页识别完成，共{len(text)}个字符")
            
            # 创建新PDF
            print("正在生成文字版PDF...")
            self._create_text_pdf(texts, image_paths)
            
            print(f"转换完成！输出文件：{self.output_pdf_path}")
            
        except Exception as e:
            print(f"转换过程中出现错误：{str(e)}")
            raise
        finally:
            # 清理临时文件
            shutil.rmtree(self.temp_dir, ignore_errors=True)


def main():
    """主函数"""
    input_pdf = "data/NLC511-004031011023755-34557_駢文通義.pdf"
    
    if not os.path.exists(input_pdf):
        print(f"错误：找不到文件 {input_pdf}")
        sys.exit(1)
    
    # 检查tesseract是否已安装
    try:
        pytesseract.get_tesseract_version()
    except Exception as e:
        print("错误：未检测到Tesseract OCR引擎")
        print("请安装Tesseract：")
        print("- macOS: brew install tesseract")
        print("- Ubuntu: sudo apt-get install tesseract-ocr-chi-sim")
        sys.exit(1)
    
    # 创建转换器并执行转换
    converter = PDFOCRConverter(input_pdf, lang='chi_sim+eng')
    converter.convert()


if __name__ == "__main__":
    main()