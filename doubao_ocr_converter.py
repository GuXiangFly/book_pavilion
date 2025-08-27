#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@auther guxiang
@date 2025-08-27
豆包OCR API版PDF转换器
使用豆包大模型API将扫描版PDF转换为可编辑的文字版PDF
"""

import os
import sys
import pymupdf as fitz
import requests
import json
import base64
from PIL import Image
import tempfile
import shutil
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import time


class DoubaoOCRConverter:
    """豆包OCR转换器类"""

    def __init__(self, api_key, endpoint, input_pdf_path, output_pdf_path=None):
        """
        初始化豆包OCR转换器
        
        Args:
            api_key: 豆包API密钥
            endpoint: API端点URL
            input_pdf_path: 输入PDF文件路径
            output_pdf_path: 输出PDF文件路径
        """
        self.api_key = api_key
        self.endpoint = endpoint
        self.input_pdf_path = input_pdf_path
        self.output_pdf_path = output_pdf_path or self._generate_output_path()

        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()

        # 设置请求头
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

    def _generate_output_path(self):
        """生成输出文件路径"""
        base_name = os.path.splitext(os.path.basename(self.input_pdf_path))[0]
        return f"{base_name}_doubao_ocr.pdf"

    def _encode_image_to_base64(self, image_path):
        """将图像编码为base64"""
        with open(image_path, 'rb') as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')

    def _call_doubao_ocr(self, image_base64):
        """调用豆包OCR API"""
        payload = {
            "model": "doubao-ocr",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "请识别这张图片中的所有文字，保持原始格式和段落结构。"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 4000
        }

        try:
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                print(f"API调用失败：{response.status_code} - {response.text}")
                return None

        except Exception as e:
            print(f"API调用异常：{str(e)}")
            return None

    def _call_doubao_ocr_use_sdk(self, image_base64):
        """使用Ark SDK调用豆包OCR API"""
        try:
            # 导入Ark SDK
            from volcenginesdkarkruntime import Ark

            # 使用模型ID（替换为实际的豆包OCR模型ID）
            model = "doubao-1-5-vision-pro-32k-250115"  # 请替换为实际的模型ID

            # 初始化Ark客户端
            client = Ark(
                api_key=self.api_key,
            )

            # 创建对话请求
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "请识别这张图片中的所有文字，保持原始格式和段落结构。"
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=4000
            )
            result = response.choices[0].message.content
            print("OCR结果是：", result)
            return result

        except Exception as e:
            print(f"SDK调用异常：{str(e)}")
            return None

    def _extract_images_from_pdf(self):
        """从PDF中提取图像"""
        doc = fitz.open(self.input_pdf_path)
        image_paths = []

        # 创建pdf_imgs目录
        pdf_imgs_dir = "data/pdf_imgs"
        os.makedirs(pdf_imgs_dir, exist_ok=True)

        # 获取PDF文件名（不含扩展名）作为子目录
        pdf_basename = os.path.splitext(os.path.basename(self.input_pdf_path))[0]
        pdf_img_subdir = os.path.join(pdf_imgs_dir, pdf_basename)
        os.makedirs(pdf_img_subdir, exist_ok=True)

        print(f"正在处理PDF，共{len(doc)}页...")

        for page_num in range(len(doc)):
            page = doc[page_num]

            # 设置高DPI以获得更好的OCR效果
            mat = fitz.Matrix(3.0, 3.0)
            pix = page.get_pixmap(matrix=mat)

            # 保存图像到 data/pdf_imgs/{pdf_name}/ 目录
            img_path = os.path.join(pdf_img_subdir, f"page_{page_num + 1}.png")
            pix.save(img_path)
            image_paths.append(img_path)

            print(f"已提取第{page_num + 1}页图像到: {img_path}")


        doc.close()


        return image_paths

    def _create_text_pdf(self, texts):
        """创建包含识别文字的新PDF"""
        c = canvas.Canvas(self.output_pdf_path, pagesize=A4)
        width, height = A4

        # 设置中文字体
        try:
            pdfmetrics.registerFont(TTFont('SimSun', '/System/Library/Fonts/PingFang.ttc'))
            font_name = 'SimSun'
        except:
            font_name = 'Helvetica'

        for i, text in enumerate(texts):
            if i > 0:
                c.showPage()

            # 设置字体和大小
            c.setFont(font_name, 12)

            # 计算文本位置
            x = 50
            y = height - 50
            line_height = 20
            max_width = width - 100

            # 处理文本
            lines = text.split('\n')

            for line in lines:
                if not line.strip():
                    y -= line_height
                    continue

                # 处理长行换行
                words = list(line)
                current_line = ""

                for char in words:
                    test_line = current_line + char
                    if c.stringWidth(test_line, font_name, 12) < max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            c.drawString(x, y, current_line)
                            y -= line_height
                        current_line = char

                if current_line:
                    c.drawString(x, y, current_line)
                    y -= line_height

                if y < 50:
                    c.showPage()
                    y = height - 50

        c.save()


    def _save_book_data(self, page_data_list):
        """收集书籍数据用于embedding"""
        book_data = []
        pdf_name = os.path.splitext(os.path.basename(self.input_pdf_path))[0]

        # 保存到book_data.json
        book_data_path = os.path.join("data", f"{pdf_name}_book_data.json")
        os.makedirs("data", exist_ok=True)

        with open(book_data_path, 'w', encoding='utf-8') as f:
            json.dump(page_data_list, f, ensure_ascii=False, indent=2)

        print(f"书籍数据已保存到: {book_data_path}")
        return book_data_path

    def _save_book_data_not_with_img(self, page_data_list):
        """收集书籍数据用于embedding"""
        book_data = []
        pdf_name = os.path.splitext(os.path.basename(self.input_pdf_path))[0]


        page_data_no_img_list =[]

        for page_num in range(len(page_data_list)):
            origin_page_data =  page_data_list[page_num]
            origin_page_data[""]

        # 保存到book_data.json
        book_data_path = os.path.join("data", f"{pdf_name}_book_data.json")
        os.makedirs("data", exist_ok=True)

        with open(book_data_path, 'w', encoding='utf-8') as f:
            json.dump(page_data_list, f, ensure_ascii=False, indent=2)

        print(f"书籍数据已保存到: {book_data_path}")
        return book_data_path

    def _collect_book_data(self, image_paths, texts, image_base64_list):
        """收集书籍数据用于embedding"""
        book_data = []
        pdf_name = os.path.splitext(os.path.basename(self.input_pdf_path))[0]

        for i, (img_path, text, image_b64) in enumerate(zip(image_paths, texts, image_base64_list)):
            page_data = {
                "page_index": i + 1,
                "image_path": img_path,
                "image_base64": image_b64,
                "text": text,
                "pdf_name": pdf_name,
                "page_id": f"{pdf_name}_page_{i + 1}"
            }
            book_data.append(page_data)

        # 保存到book_data.json
        book_data_path = os.path.join("data", f"{pdf_name}_book_data.json")
        os.makedirs("data", exist_ok=True)

        with open(book_data_path, 'w', encoding='utf-8') as f:
            json.dump(book_data, f, ensure_ascii=False, indent=2)

        print(f"书籍数据已保存到: {book_data_path}")
        return book_data_path

    def convert(self):
        """执行完整的转换流程"""
        try:
            print("开始豆包OCR转换...")

            pdf_name = os.path.splitext(os.path.basename(self.input_pdf_path))[0]

            # 提取图像
            image_paths = self._extract_images_from_pdf()

            # 执行OCR
            texts = []
            image_base64_list = []

            page_data_list = []

            for i, img_path in enumerate(image_paths):
                try:
                    page_index = i + 1
                    print(f"正在识别第{page_index}页文字...")

                    # 编码图像
                    image_base64 = self._encode_image_to_base64(img_path)
                    image_base64_list.append(image_base64)

                    # 调用API
                    text = self._call_doubao_ocr_use_sdk(image_base64)
                    if text:
                        texts.append(text)
                        print(f"第{i + 1}页识别完成")
                    else:
                        texts.append("[识别失败]")
                        print(f"第{i + 1}页识别失败")

                    page_data = {
                        "page_index": i + 1,
                        "image_path": img_path,
                        "text": text,
                        "pdf_name": pdf_name,
                        "page_id": f"{pdf_name}_page_{i + 1}"
                    }
                    page_data_list.append(page_data)

                    if page_index >=5:
                        break
                except Exception as e:
                    print(e)

                # 避免API限流
                time.sleep(1)

            # 收集书籍数据用于embedding
            self._save_book_data(page_data_list)

            # 创建新PDF
            print("正在生成文字版PDF...")
            self._create_text_pdf(texts)

            print(f"转换完成！输出文件：{self.output_pdf_path}")

        except Exception as e:
            print(f"转换过程中出现错误：{str(e)}")
            raise
        finally:
            # 清理临时文件
            shutil.rmtree(self.temp_dir, ignore_errors=True)


def main():
    """主函数 - 需要用户配置API信息"""
    print("豆包OCR PDF转换器")
    print("=" * 50)

    # 用户需要在这里配置API信息
    API_KEY = "ef9dbfa5-38f9-4f55-86de-7948bec46d5c"
    ENDPOINT = "your_doubao_endpoint_here"

    if API_KEY == "your_doubao_api_key_here":
        print("请先设置您的豆包API密钥和端点")
        print("1. 获取豆包API密钥：访问火山引擎控制台")
        print("2. 设置API_KEY和ENDPOINT变量")
        return

    input_pdf = "data/NLC511-004031011023755-34557_駢文通義.pdf"

    if not os.path.exists(input_pdf):
        print(f"错误：找不到文件 {input_pdf}")
        return

    # 创建转换器并执行转换
    converter = DoubaoOCRConverter(API_KEY, ENDPOINT, input_pdf)
    converter.convert()


if __name__ == "__main__":
    main()
