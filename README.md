# PDF二维码分析工具

一个强大的PDF分析工具，能够自动识别PDF文件中的二维码，特别是微信公众号文章链接，并提取详细的文章信息和元数据。

## 功能特性

### 🔍 核心功能
- **PDF文件解析**: 支持上传和解析PDF文件
- **二维码识别**: 自动检测PDF中的所有二维码
- **微信文章分析**: 专门识别和分析微信公众号文章链接
- **数据提取**: 提取文章的详细信息和元数据

### 📊 数据分析
重点识别和提取以下信息：

#### 1. 微信文章信息 (优先级最高)
- 📝 **文章标题**: `<h1 class="rich_media_title">` 或 `<h2 class="rich_media_title">`
- 📅 **发布时间**: `<em class="rich_media_meta_text">` 中的时间信息
- 📱 **公众号名称**: `<a class="rich_media_meta_link">` 中的账号信息
- 🔗 **原文链接**: 页面URL和相关链接信息

#### 2. 开发信息识别
- 👨‍💻 **作者信息**: `<meta name="author">` 标签
- ©️ **版权声明**: `<meta name="copyright">` 标签
- 🏢 **开发者信息**: 各类开发相关的meta标签

#### 3. Meta标签分析
- 🏷️ **所有Meta标签**: name、content、property等属性
- 📱 **移动端适配**: viewport、mobile相关配置
- 🔍 **SEO信息**: description、keywords等

#### 4. 脚本和标签统计
- 📜 **Script标签**: JavaScript文件和内联脚本
- 🏷️ **Label标签**: 表单标签和用户界面元素
- ©️ **版权属性**: HTML元素中的copyright相关属性

## 技术栈

- **后端**: Python Flask
- **PDF处理**: PyMuPDF (fitz)
- **二维码识别**: OpenCV + pyzbar
- **网页抓取**: requests + BeautifulSoup4
- **前端**: HTML5 + Bootstrap 5 + JavaScript
- **图像处理**: Pillow + NumPy

## 安装和运行

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行应用
```bash
python app.py
```

### 3. 访问应用
打开浏览器访问: `http://localhost:5000`

## 使用方法

1. **上传PDF文件**: 点击选择文件或直接拖拽PDF文件到上传区域
2. **自动分析**: 系统会自动识别PDF中的二维码并分析微信文章
3. **查看结果**: 查看分析结果，包括文章信息、元数据等
4. **导出数据**: 可以将分析结果导出为JSON格式

## 项目结构

```
pdf-analysis/
├── app.py                 # Flask主应用
├── pdf_analyzer.py        # PDF分析核心模块
├── requirements.txt       # Python依赖
├── README.md             # 项目说明
├── templates/            # HTML模板
│   └── index.html
├── static/               # 静态资源
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
└── uploads/              # 临时上传目录
```

## 支持的文件格式

- **输入**: PDF文件 (最大16MB)
- **输出**: JSON格式的分析结果

## 注意事项

1. **文件大小限制**: 单个PDF文件不超过16MB
2. **网络访问**: 需要网络连接来访问微信文章链接
3. **隐私保护**: 上传的PDF文件在分析完成后会自动删除
4. **浏览器兼容**: 建议使用现代浏览器 (Chrome, Firefox, Safari, Edge)

## 部署说明

### 部署到 Render 平台

本项目已配置好 Render 平台部署，详细步骤请参考 [DEPLOY.md](DEPLOY.md)

#### 快速部署步骤：

1. **创建 GitHub 仓库**（选择 Python 模板）
2. **推送代码到 GitHub**
3. **在 Render 创建 Web Service**
4. **连接 GitHub 仓库**
5. **配置部署设置**：
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Environment: `Python 3`

#### 部署文件说明：
- `Procfile`: Render 部署配置
- `render.yaml`: 服务配置文件
- `.gitignore`: Git 忽略文件配置

### 环境变量
- `FLASK_ENV`: 设置为 `production` 用于生产环境
- `PORT`: 服务端口（Render 自动设置）

## 开发说明

### 核心模块

- `PDFAnalyzer`: 主要的分析类，负责PDF解析和二维码识别
- `analyze_pdf()`: 分析PDF文件的主要方法
- `detect_qr_codes()`: 二维码检测方法
- `analyze_wechat_article()`: 微信文章分析方法

### API接口

- `POST /upload`: 上传和分析PDF文件
- `GET /health`: 健康检查接口

## 许可证

本项目采用MIT许可证。