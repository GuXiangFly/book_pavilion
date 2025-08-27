# PDF扫描转文字版转换器

## 项目简介
将扫描版PDF文件转换为可编辑的文字版PDF，支持中文识别。

## 两种转换方案

### 方案一：本地OCR（推荐）
使用Tesseract OCR引擎，无需网络连接，完全本地处理。

#### 安装依赖
```bash
# macOS
brew install tesseract tesseract-lang

# Ubuntu/Debian
sudo apt-get install tesseract-ocr-chi-sim

# Windows
# 下载安装Tesseract OCR并添加中文语言包
```

#### 使用方法
```bash
python3 pdf_ocr_converter.py
```

### 方案二：豆包OCR API（高精度）
使用豆包大模型API，识别精度更高，但需要API密钥和网络连接。

#### 配置步骤
1. 注册火山引擎账号
2. 获取豆包API密钥
3. 修改 `doubao_ocr_converter.py` 中的API配置

#### 使用方法
```bash
python3 doubao_ocr_converter.py
```

## 输入文件
- 默认输入：`data/NLC511-004031011023755-34557_駢文通義.pdf`
- 可在脚本中修改输入文件路径

## 输出文件
- 本地OCR：`NLC511-004031011023755-34557_駢文通義_ocr.pdf`
- 豆包OCR：`NLC511-004031011023755-34557_駢文通義_doubao_ocr.pdf`

## 功能特点
- 支持中文简体和英文混合识别
- 自动图像预处理提高识别精度
- 保留原始文档结构
- 支持批量处理多页PDF
- 自动清理临时文件

## 注意事项
- 本地OCR需要安装Tesseract和中文语言包
- 豆包API需要网络连接和有效API密钥
- 大文件处理可能需要较长时间
- 建议对复杂排版的文档进行人工校对

## 技术支持
如遇到问题，请检查：
1. Tesseract是否正确安装
2. 中文语言包是否可用
3. API密钥是否有效
4. 文件路径是否正确