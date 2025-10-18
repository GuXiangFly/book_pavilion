#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@auther guxiang
@date 2025-08-28
PDF转换器模块
处理文本到PDF的转换功能
"""

import os
from typing import List
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class PDFConverter:
    """PDF转换器类"""
    
    def __init__(self, output_path: str = None):
        """
        初始化PDF转换器
        
        Args:
            output_path: 输出PDF文件路径
        """
        self.output_path = output_path
        self.font_paths = [
            '/System/Library/Fonts/PingFang.ttc',  # macOS
            '/System/Library/Fonts/STHeiti Medium.ttc',  # macOS
            'C:/Windows/Fonts/simhei.ttf',  # Windows
            'C:/Windows/Fonts/simsun.ttc',  # Windows
            '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
            '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf',  # Linux
        ]
    
    def find_chinese_font(self) -> str:
        """
        查找可用的中文字体
        
        Returns:
            字体名称，如果找不到则返回'Helvetica'
        """
        font_name = None
        
        for font_path in self.font_paths:
            if os.path.exists(font_path):
                try:
                    font_name = 'CustomChinese'
                    pdfmetrics.registerFont(TTFont('CustomChinese', font_path))
                    return font_name
                except Exception as e:
                    print(f"字体加载失败 {font_path}: {e}")
                    continue
        
        if not font_name:
            font_name = 'Helvetica'
            print("警告：使用默认字体，中文字符可能显示为乱码")
        
        return font_name
    
    def create_text_pdf(self, texts: List[str], output_path: str = None, 
                       title: str = "OCR结果", author: str = "豆包OCR",
                       subject: str = "OCR处理后的文字版PDF",
                       font_size: int = 14) -> str:
        """
        创建包含识别文字的新PDF
        
        Args:
            texts: 文本内容列表，每个元素为一页的内容
            output_path: 输出PDF文件路径，如果为None则使用初始化时的路径
            title: PDF标题
            author: PDF作者
            subject: PDF主题
            font_size: 字体大小
            
        Returns:
            输出文件路径
        """
        if output_path:
            self.output_path = output_path
        
        if not self.output_path:
            raise ValueError("未设置输出文件路径")
        
        # 创建PDF画布
        c = canvas.Canvas(self.output_path, pagesize=A4)
        width, height = A4
        
        # 设置字体
        font_name = self.find_chinese_font()
        
        # 设置PDF元数据
        c.setTitle(title)
        c.setAuthor(author)
        c.setSubject(subject)
        
        # 页面边距和行高设置
        margin_x = 50
        margin_y = 50
        line_height = 24  # 增加行高提高可读性
        max_width = width - 2 * margin_x
        
        for page_num, text in enumerate(texts):
            if page_num > 0:
                c.showPage()
            
            # 设置字体和大小
            c.setFont(font_name, font_size)
            
            # 计算起始位置
            x = margin_x
            y = height - margin_y
            
            # 处理文本
            processed_text = self._process_text(text)
            lines = processed_text.split('\n')
            
            for line in lines:
                if not line.strip():
                    y -= line_height
                    continue
                
                # 处理长行换行
                y = self._draw_wrapped_text(c, line, x, y, max_width, font_name, font_size, line_height)
                
                if y < margin_y:
                    c.showPage()
                    y = height - margin_y
        
        c.save()
        return self.output_path
    
    def _process_text(self, text: str) -> str:
        """
        处理文本编码问题
        
        Args:
            text: 原始文本
            
        Returns:
            处理后的文本
        """
        try:
            # 确保文本是UTF-8编码
            if not isinstance(text, str):
                text = str(text)
            
            # 替换可能的乱码字符
            processed_text = text.replace('�', '?')
            processed_text = processed_text.encode('utf-8', 'ignore').decode('utf-8')
            
        except Exception as e:
            print(f"文本处理错误: {e}")
            processed_text = str(text)
        
        return processed_text
    
    def _draw_wrapped_text(self, c, text: str, x: float, y: float, 
                          max_width: float, font_name: str, font_size: int, line_height: float) -> float:
        """
        绘制自动换行的文本
        
        Args:
            c: PDF画布
            text: 要绘制的文本
            x: 起始x坐标
            y: 起始y坐标
            max_width: 最大宽度
            font_name: 字体名称
            font_size: 字体大小
            line_height: 行高
            
        Returns:
            绘制完成后的y坐标
        """
        # 先将整行按空格分割，再处理每个词
        words = text.split(' ')
        current_line = ""
        
        for word in words:
            if not word:
                continue
            
            test_line = current_line + word + " "
            if c.stringWidth(test_line, font_name, font_size) < max_width:
                current_line = test_line
            else:
                if current_line.strip():
                    c.drawString(x, y, current_line.strip())
                    y -= line_height
                current_line = word + " "
                
                # 如果单个词太长，按字符分割
                if c.stringWidth(word, font_name, font_size) > max_width:
                    current_line = ""
                    for char in word:
                        test_char = current_line + char
                        if c.stringWidth(test_char, font_name, font_size) < max_width:
                            current_line = test_char
                        else:
                            if current_line:
                                c.drawString(x, y, current_line)
                                y -= line_height
                            current_line = char
        
        if current_line.strip():
            c.drawString(x, y, current_line.strip())
            y -= line_height
        
        return y
    
    def create_pdf_from_dict_list(self, page_data_list: List[dict], 
                                 output_path: str = None, text_field: str = "text",
                                 **kwargs) -> str:
        """
        从字典列表创建PDF
        
        Args:
            page_data_list: 包含文本数据的字典列表
            output_path: 输出PDF文件路径
            text_field: 字典中存储文本的字段名
            **kwargs: 传递给create_text_pdf的其他参数
            
        Returns:
            输出文件路径
        """
        texts = []
        for page_data in page_data_list:
            text = page_data.get(text_field, "")
            texts.append(text)
        
        return self.create_text_pdf(texts, output_path, **kwargs)