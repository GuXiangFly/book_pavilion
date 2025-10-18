#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@auther guxiang
@date 2025-08-28
豆包OCR API版PDF转换器 - 优化版V2
使用豆包大模型API将扫描版PDF转换为可编辑的文字版PDF
"""

import os
import sys
import json
import tempfile
import shutil
import pymupdf as fitz
import time
from typing import List, Optional

# 导入新创建的模块
from doubao_api import DoubaoAPIClient
from pdf_converter import PDFConverter


class DoubaoOCRConverter:
    """豆包OCR转换器类 - 优化版"""

    def __init__(self, api_key: str, input_pdf_path: str, endpoint: str = None, output_pdf_path: str = None):
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
        self.output_pdf_path = self._generate_output_path(output_pdf_path)
        self.book_json_data_path = ""
        self.book_json_data = []
        self.base_name = self._generate_base_name()

        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()

        # 初始化API客户端
        self.api_client = DoubaoAPIClient(api_key, endpoint)
        
        # 初始化PDF转换器
        self.pdf_converter = PDFConverter(self.output_pdf_path)

    def _generate_output_path(self, output_path: str = None) -> str:
        """生成输出文件路径"""
        if output_path:
            return output_path
            
        base_name = os.path.splitext(os.path.basename(self.input_pdf_path))[0]
        return f"{base_name}_doubao_ocr.pdf"

    def _generate_base_name(self) -> str:
        """生成基础文件名"""
        base_name = os.path.splitext(os.path.basename(self.input_pdf_path))[0]
        base_name_dir = f"data/{base_name}"
        os.makedirs(base_name_dir, exist_ok=True)
        return base_name

    def _is_loaded_this_page(self, page_index: int) -> Optional[dict]:
        """检查页面是否已经加载处理过"""
        if not self.book_json_data:
            return None

        for page_data in self.book_json_data:
            if page_data['page_index'] == page_index:
                page_data_text = page_data["text"]
                if page_data_text and page_data_text != "<UNK>" and page_data_text != "[识别失败]":
                    return page_data
                else:
                    return None
        return None

    def _extract_images_from_pdf(self) -> List[str]:
        """从PDF中提取图像"""
        doc = fitz.open(self.input_pdf_path)
        image_paths = []

        # 创建pdf_imgs目录
        pdf_imgs_dir = f"data/{self.base_name}/pdf_imgs"
        os.makedirs(pdf_imgs_dir, exist_ok=True)

        # 获取PDF文件名（不含扩展名）作为子目录
        pdf_basename = os.path.splitext(os.path.basename(self.input_pdf_path))[0]
        pdf_img_subdir = os.path.join(pdf_imgs_dir, pdf_basename)
        os.makedirs(pdf_img_subdir, exist_ok=True)

        print(f"正在处理PDF，共{len(doc)}页...")

        for page_num in range(len(doc)):
            page_index = page_num + 1

            # 检查是否已经处理过
            temp_page_data = self._is_loaded_this_page(page_index)
            if temp_page_data is not None:
                print(f"第{page_index}页的PDF已经处理过了")
                image_paths.append(temp_page_data["image_path"])
                continue

            page = doc[page_num]

            # 设置高DPI以获得更好的OCR效果
            mat = fitz.Matrix(3.0, 3.0)
            pix = page.get_pixmap(matrix=mat)

            # 保存图像
            img_path = os.path.join(pdf_img_subdir, f"page_{page_num + 1}.png")
            pix.save(img_path)
            image_paths.append(img_path)

            print(f"已提取第{page_num + 1}页图像到: {img_path}")

        doc.close()
        return image_paths

    def _init_book_data_json_path(self) -> str:
        """初始化书籍数据JSON文件路径"""
        pdf_name = os.path.splitext(os.path.basename(self.input_pdf_path))[0]
        json_dir = f"data/{pdf_name}/json"
        os.makedirs(json_dir, exist_ok=True)
        book_data_path = os.path.join(json_dir, f"{pdf_name}_book_data.json")
        self.book_json_data_path = book_data_path
        return book_data_path

    def _save_book_data(self, page_data_list: List[dict]) -> str:
        """保存书籍数据到JSON文件"""
        book_data_path = self._init_book_data_json_path()
        
        with open(book_data_path, 'w', encoding='utf-8') as f:
            json.dump(page_data_list, f, ensure_ascii=False, indent=2)

        print(f"书籍数据已保存到: {book_data_path}")
        return book_data_path

    def load_book_json_data(self) -> bool:
        """加载book_json_data_path的json文件到self.book_json_data"""
        try:
            if not self.book_json_data_path:
                print("警告: book_json_data_path未设置，正在初始化...")
                self.book_json_data_path = self._init_book_data_json_path()

            if not os.path.exists(self.book_json_data_path):
                print(f"警告: JSON文件不存在: {self.book_json_data_path}")
                self.book_json_data = []
                return False

            with open(self.book_json_data_path, 'r', encoding='utf-8') as f:
                self.book_json_data = json.load(f)

            print(f"成功加载书籍数据，共{len(self.book_json_data)}页数据")
            return True

        except json.JSONDecodeError as e:
            print(f"错误: JSON格式无效 - {e}")
            self.book_json_data = []
            return False
        except Exception as e:
            print(f"错误: 加载JSON文件时发生异常 - {e}")
            self.book_json_data = []
            return False

    def save_book_json_data_with_judge(self, page_data_list: List[dict]):
        """判断并保存书籍数据"""
        self.load_book_json_data()
        
        for page_data in page_data_list:
            page_index = int(page_data["page_index"])
            if self._is_loaded_this_page(page_index) is None:
                print(f"存在有新增的内容，进行存储 page_index:{page_index}")
                self._save_book_data(page_data_list)
                break

    def _collect_book_data(self, image_paths: List[str], texts: List[str]) -> List[dict]:
        """收集书籍数据"""
        book_data = []
        pdf_name = os.path.splitext(os.path.basename(self.input_pdf_path))[0]

        for i, (img_path, text) in enumerate(zip(image_paths, texts)):
            page_data = {
                "page_index": i + 1,
                "image_path": img_path,
                "text": text,
                "pdf_name": pdf_name,
                "page_id": f"{pdf_name}_page_{i + 1}"
            }
            book_data.append(page_data)

        return book_data

    def convert_from_json(self):
        """从已有的JSON数据生成PDF"""
        if not self.load_book_json_data():
            print("没有可用的JSON数据，无法进行转换")
            return False

        texts = [page_data["text"] for page_data in self.book_json_data]
        
        try:
            self.pdf_converter.create_text_pdf(
                texts,
                self.output_pdf_path,
                title=f"{self.base_name} - OCR结果",
                author="豆包OCR",
                subject="OCR处理后的文字版PDF"
            )
            print(f"从JSON数据生成PDF完成！输出文件：{self.output_pdf_path}")
            return True
        except Exception as e:
            print(f"生成PDF时出错：{str(e)}")
            return False

    def convert(self, use_sdk: bool = True, model: str = None):
        """执行完整的转换流程"""
        page_data_list = []
        self.load_book_json_data()
        
        try:
            print("开始豆包OCR转换...")

            pdf_name = os.path.splitext(os.path.basename(self.input_pdf_path))[0]

            # 提取图像
            image_paths = self._extract_images_from_pdf()

            # 执行OCR
            texts = []

            for i, img_path in enumerate(image_paths):
                try:
                    page_index = i + 1
                    print(f"正在识别第{page_index}页文字...")

                    # 检查是否已经处理过
                    temp_page_data = self._is_loaded_this_page(page_index)
                    if temp_page_data is not None:
                        page_data_list.append(temp_page_data)
                        texts.append(temp_page_data["text"])
                        print("=" * 50)
                        print("数据已经加载过，内容如下：")
                        print(temp_page_data["text"][:200] + "..." if len(temp_page_data["text"]) > 200 else temp_page_data["text"])
                        continue

                    # 调用API进行OCR识别
                    text = self.api_client.process_image_file(img_path, use_sdk=use_sdk, model=model)
                    if text:
                        texts.append(text)
                        print(f"第{i + 1}页识别完成")
                    else:
                        texts.append("[识别失败]")
                        print(f"第{i + 1}页识别失败")

                    # 收集数据
                    page_data = {
                        "page_index": i + 1,
                        "image_path": img_path,
                        "text": text,
                        "pdf_name": pdf_name,
                        "page_id": f"{pdf_name}_page_{i + 1}"
                    }
                    page_data_list.append(page_data)
                    
                    # 保存中间结果
                    self.save_book_json_data_with_judge(page_data_list)

                except Exception as e:
                    print(f"处理第{i + 1}页时出错：{e}")
                    texts.append(f"[处理错误: {str(e)}]")

                # 避免API限流
                time.sleep(1)

            # 最终保存数据
            self.save_book_json_data_with_judge(page_data_list)

            # 创建新PDF
            print("正在生成文字版PDF...")
            
            # 更新PDF转换器的输出路径
            self.pdf_converter.output_path = self.output_pdf_path
            
            self.pdf_converter.create_text_pdf(
                texts,
                title=f"{self.base_name} - OCR结果",
                author="豆包OCR",
                subject="OCR处理后的文字版PDF"
            )

            print(f"转换完成！输出文件：{self.output_pdf_path}")
            return True

        except Exception as e:
            print(f"转换过程中出现错误：{str(e)}")
            self.save_book_json_data_with_judge(page_data_list)
            raise
        finally:
            # 清理临时文件
            shutil.rmtree(self.temp_dir, ignore_errors=True)


def main():
    """主函数"""
    print("豆包OCR PDF转换器 - 优化版V2")
    print("=" * 50)

    # 配置信息
    API_KEY = "ef9dbfa5-38f9-4f55-86de-7948bec46d5c"
    ENDPOINT = "your_doubao_endpoint_here"

    if API_KEY == "your_doubao_api_key_here":
        print("请先设置您的豆包API密钥和端点")
        print("1. 获取豆包API密钥：访问火山引擎控制台")
        print("2. 设置API_KEY和ENDPOINT变量")
        return

    input_pdf = "data/叙事的本质.pdf"
    
    if not os.path.exists(input_pdf):
        print(f"错误：找不到文件 {input_pdf}")
        return

    # 创建转换器
    converter = DoubaoOCRConverter(API_KEY, input_pdf, endpoint=ENDPOINT)
    
    # 选择转换模式
    print("选择转换模式：")
    print("1. 完整转换（从PDF开始）")
    print("2. 从已有JSON数据生成PDF")
    
    # 默认使用完整转换模式
    try:
        converter.convert(use_sdk=True)
    except KeyboardInterrupt:
        print("\n转换被用户中断")
    except Exception as e:
        print(f"转换失败：{e}")


if __name__ == "__main__":
    main()