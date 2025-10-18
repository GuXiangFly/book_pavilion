#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@auther guxiang
@date 2025-08-28
豆包API调用模块
封装豆包OCR API的相关调用功能
"""

import base64
import requests
import json
from typing import Optional


class DoubaoAPIClient:
    """豆包API客户端类"""
    
    def __init__(self, api_key: str, endpoint: str = None):
        """
        初始化豆包API客户端
        
        Args:
            api_key: 豆包API密钥
            endpoint: API端点URL，可选
        """
        self.api_key = api_key
        self.endpoint = endpoint
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """
        将图像编码为base64字符串
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            base64编码的图像字符串
        """
        with open(image_path, 'rb') as img_file:
            return base64.b64encode(img_file.read()).decode('utf-8')
    
    def call_doubao_ocr(self, image_base64: str, timeout: int = 60) -> Optional[str]:
        """
        调用豆包OCR API（HTTP请求方式）
        
        Args:
            image_base64: base64编码的图像字符串
            timeout: 请求超时时间（秒）
            
        Returns:
            识别到的文本内容，失败返回None
        """
        if not self.endpoint:
            print("错误：未设置API端点")
            return None
            
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
                timeout=timeout
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
    
    def call_doubao_ocr_use_sdk(self, image_base64: str, model: str = None, timeout: float = 20.0) -> Optional[str]:
        """
        使用Ark SDK调用豆包OCR API
        
        Args:
            image_base64: base64编码的图像字符串
            model: 模型ID，默认为"doubao-1-5-vision-pro-32k-250115"
            timeout: 请求超时时间（秒）
            
        Returns:
            识别到的文本内容，失败返回None
        """
        try:
            # 导入Ark SDK
            from volcenginesdkarkruntime import Ark

            # 使用模型ID
            if not model:
                model = "doubao-1-5-vision-pro-32k-250115"  # 默认模型ID

            # 初始化Ark客户端
            client = Ark(api_key=self.api_key)

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
                max_tokens=4000,
                timeout=timeout
            )
            result = response.choices[0].message.content
            print("OCR结果是：\n", result)
            return result

        except Exception as e:
            print(f"SDK调用异常：{str(e)}")
            return None
    
    def process_image_file(self, image_path: str, use_sdk: bool = True, model: str = None) -> Optional[str]:
        """
        处理单个图像文件的OCR识别
        
        Args:
            image_path: 图像文件路径
            use_sdk: 是否使用SDK方式调用，默认为True
            model: 模型ID，仅在使用SDK时有效
            
        Returns:
            识别到的文本内容，失败返回None
        """
        try:
            image_base64 = self.encode_image_to_base64(image_path)
            
            if use_sdk:
                return self.call_doubao_ocr_use_sdk(image_base64, model)
            else:
                return self.call_doubao_ocr(image_base64)
                
        except Exception as e:
            print(f"处理图像文件异常：{str(e)}")
            return None