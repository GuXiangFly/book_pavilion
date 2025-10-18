#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将字符串列表存储到txt文件的函数
@author guxiang
@date 2025-10-18
"""

def save_texts_to_file(texts, filename, encoding='utf-8'):
    """
    将字符串列表保存到txt文件中

    Args:
        texts (list): 字符串列表，每个元素是一个字符串
        filename (str): 输出的txt文件名
        encoding (str): 文件编码，默认为utf-8

    Returns:
        bool: 保存成功返回True，失败返回False
    """
    try:
        with open(filename, 'w', encoding=encoding) as file:
            for text in texts:
                # 确保每个字符串后面都有换行符
                if not text.endswith('\n'):
                    text += '\n'
                file.write(text)
        print(f"成功保存 {len(texts)} 个文本到文件: {filename}")
        return True
    except Exception as e:
        print(f"保存文件时出错: {e}")
        return False

def save_texts_to_file_with_separator(texts, filename, separator='\n', encoding='utf-8'):
    """
    将字符串列表保存到txt文件中，可自定义分隔符

    Args:
        texts (list): 字符串列表，每个元素是一个字符串
        filename (str): 输出的txt文件名
        separator (str): 文本之间的分隔符，默认为换行符
        encoding (str): 文件编码，默认为utf-8

    Returns:
        bool: 保存成功返回True，失败返回False
    """
    try:
        with open(filename, 'w', encoding=encoding) as file:
            # 使用指定的分隔符连接所有文本
            content = separator.join(texts)
            file.write(content)
        print(f"成功保存 {len(texts)} 个文本到文件: {filename}")
        return True
    except Exception as e:
        print(f"保存文件时出错: {e}")
        return False

if __name__ == "__main__":
    # 测试函数
    test_texts = [
        "这是第一行文本",
        "这是第二行文本",
        "这是第三行文本",
        "这是最后一行文本"
    ]

    # 测试基本函数
    save_texts_to_file(test_texts, "output.txt")

    # 测试带分隔符的函数
    save_texts_to_file_with_separator(test_texts, "output_with_separator.txt", separator=' | ')