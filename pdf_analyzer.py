import PyPDF2
import cv2
import numpy as np
from PIL import Image
import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
import re
import json
from urllib.parse import urlparse, parse_qs
import time
from datetime import datetime
import io
import os
import tempfile

class PDFAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def analyze_pdf(self, pdf_path):
        """分析PDF文件，提取二维码并分析微信文章"""
        import sys
        print(f"开始分析PDF文件: {pdf_path}", flush=True)
        sys.stdout.flush()
        
        results = {
            'total_qr_codes': 0,
            'wechat_articles': [],
            'other_qr_codes': [],
            'analysis_time': datetime.now().isoformat()
        }
        
        try:
            # 使用PyMuPDF打开PDF文件
            print("正在打开PDF文件...", flush=True)
            pdf_document = fitz.open(pdf_path)
            print(f"PDF打开成功，共 {len(pdf_document)} 页", flush=True)
            
            for page_num in range(len(pdf_document)):
                print(f"正在处理第 {page_num + 1} 页...", flush=True)
                
                # 获取页面
                page = pdf_document.load_page(page_num)
                
                # 将页面转换为图像
                mat = fitz.Matrix(2.0, 2.0)  # 2倍缩放以提高分辨率
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("ppm")
                
                # 转换为PIL Image
                image = Image.open(io.BytesIO(img_data))
                
                # 检测二维码
                qr_codes = self.detect_qr_codes(image)
                
                for qr_data in qr_codes:
                    results['total_qr_codes'] += 1
                    print(f"处理二维码: {qr_data}", flush=True)
                    
                    if self.is_wechat_article_url(qr_data):
                        try:
                            # 分析微信文章
                            article_info = self.analyze_wechat_article(qr_data)
                            if article_info and 'error' not in article_info:
                                article_info['page_number'] = page_num + 1  # 转换为1基索引
                                article_info['qr_url'] = qr_data
                                results['wechat_articles'].append(article_info)
                                print(f"成功分析微信文章: {article_info.get('title', '未知标题')}", flush=True)
                            else:
                                print(f"微信文章分析失败: {qr_data}", flush=True)
                                results['other_qr_codes'].append({
                                    'url': qr_data,
                                    'page_number': page_num + 1,
                                    'error': article_info.get('error', '分析失败') if article_info else '无响应'
                                })
                        except Exception as e:
                            print(f"微信文章分析异常: {qr_data}, 错误: {str(e)}", flush=True)
                            results['other_qr_codes'].append({
                                'url': qr_data,
                                'page_number': page_num + 1,
                                'error': f'分析异常: {str(e)}'
                            })
                    else:
                        results['other_qr_codes'].append({
                            'url': qr_data,
                            'page_number': page_num + 1  # 转换为1基索引
                        })
            
            # 关闭PDF文档
            pdf_document.close()
            
        except Exception as e:
            results['error'] = f'PDF分析错误: {str(e)}'
        
        return results
    
    def detect_qr_codes(self, image):
        """
        检测图像中的二维码
        """
        import sys
        try:
            print(f"开始检测二维码，图像类型: {type(image)}", flush=True)
            sys.stdout.flush()
            
            # 转换PIL Image为OpenCV格式
            if isinstance(image, Image.Image):
                print(f"PIL图像尺寸: {image.size}", flush=True)
                opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            else:
                opencv_image = image
            
            print(f"OpenCV图像形状: {opencv_image.shape}", flush=True)
            
            # 初始化QR码检测器
            qr_detector = cv2.QRCodeDetector()
            
            # 检测和解码二维码
            data, bbox, rectified_image = qr_detector.detectAndDecode(opencv_image)
            
            results = []
            if data:
                print(f"检测到二维码: {data}", flush=True)
                results.append(data)
            else:
                print("单个二维码检测未找到结果", flush=True)
            
            # 尝试检测多个二维码
            try:
                retval, decoded_info, points, straight_qrcode = qr_detector.detectAndDecodeMulti(opencv_image)
                print(f"多二维码检测结果: retval={retval}", flush=True)
                if retval:
                    print(f"检测到 {len(decoded_info)} 个二维码", flush=True)
                    for i, info in enumerate(decoded_info):
                        print(f"二维码 {i+1}: {info}", flush=True)
                        if info and info not in results:
                            results.append(info)
                else:
                    print("多二维码检测未找到结果", flush=True)
            except Exception as multi_e:
                print(f"多二维码检测异常: {multi_e}", flush=True)
            
            print(f"最终检测结果: {len(results)} 个二维码", flush=True)
            sys.stdout.flush()
            return results
        except Exception as e:
            print(f"二维码检测错误: {e}", flush=True)
            import traceback
            traceback.print_exc()
            sys.stdout.flush()
            return []
    
    def is_wechat_article_url(self, url):
        """判断是否为微信公众号文章链接"""
        wechat_patterns = [
            r'mp\.weixin\.qq\.com',
            r'weixin\.qq\.com.*article',
            r'mp\.weixin\.qq\.com/s\?',
        ]
        
        for pattern in wechat_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        return False
    
    def analyze_wechat_article(self, url):
        """分析微信公众号文章"""
        try:
            # 减少延时以避免超时，仅在必要时添加短暂延时
            time.sleep(0.2)
            
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            article_info = {
                'url': url,
                'title': self.extract_title(soup),
                'publish_time': self.extract_publish_time(soup),
                'account_name': self.extract_account_name(soup),
                'author': self.extract_author(soup),
                'article_link': self.extract_article_link(soup),
                'copyright': self.extract_copyright(soup),
                'meta_tags': self.extract_meta_tags(soup),
                'scripts': self.extract_scripts(soup),
                'labels': self.extract_labels(soup),
                'seo_info': self.extract_seo_info(soup)
            }
            
            return article_info
            
        except Exception as e:
            return {
                'url': url,
                'error': f'文章分析错误: {str(e)}'
            }
    
    def extract_title(self, soup):
        """提取文章标题"""
        # 首先尝试从JavaScript变量中提取
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # 查找 var msg_title = '标题'.html(false);
                title_match = re.search(r"var\s+msg_title\s*=\s*['\"]([^'\"]*)['\"](?:\.html\(false\))?", script.string)
                if title_match:
                    return title_match.group(1).strip()
        
        # 备用方案：从HTML元素中提取
        selectors = [
            'h1.rich_media_title',
            'h2.rich_media_title', 
            '.rich_media_title',
            'h1',
            'title'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        
        return None
    
    def extract_publish_time(self, soup):
        """提取发布时间"""
        # 首先尝试从JavaScript变量中提取
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # 查找 var createTime = '2023-07-10 18:35';
                time_match = re.search(r"var\s+createTime\s*=\s*['\"]([^'\"]*)['\"];", script.string)
                if time_match:
                    return time_match.group(1).strip()
        
        # 备用方案：从HTML元素中提取
        selectors = [
            'em.rich_media_meta_text',
            '.rich_media_meta_text',
            '[id*="publish_time"]',
            '.publish_time'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text().strip()
                # 尝试提取时间信息
                time_pattern = r'\d{4}[-年]\d{1,2}[-月]\d{1,2}[日]?'
                match = re.search(time_pattern, text)
                if match:
                    return match.group()
                return text
        
        return None
    
    def extract_account_name(self, soup):
        """提取公众号名称"""
        # 首先尝试从用户指定的HTML结构中提取
        # <div class="wx_follow_info"><div class="wx_follow_nickname">公众号名称</div></div>
        wx_follow_nickname = soup.select_one('.wx_follow_info .wx_follow_nickname')
        if wx_follow_nickname:
            return wx_follow_nickname.get_text().strip()
        
        # 备用方案：从其他可能的选择器中提取
        selectors = [
            'a.rich_media_meta_link',
            '.rich_media_meta_link',
            '[id*="account"]',
            '.account_name',
            '#js_wx_follow_nickname'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text().strip()
        
        return None
    
    def extract_author(self, soup):
        """提取作者信息"""
        author_meta = soup.find('meta', attrs={'name': 'author'})
        if author_meta:
            return author_meta.get('content')
        return None
    
    def extract_copyright(self, soup):
        """提取版权信息 - 分析自定义属性"""
        copyright_info = {
            'copyright_attributes': [],
            'author_attributes': [],
            'keyword_matches': []
        }
        
        # 版权相关属性
        copyright_attrs = ['copyright', 'data-copyright', 'powered-by', 'data-powered-by']
        # 作者相关属性
        author_attrs = ['name', 'author', 'label', 'data-author', 'data-name']
        # 关键词
        keywords = ['版权', 'copyright', '©']
        
        # 查找所有元素的属性
        all_elements = soup.find_all()
        
        for element in all_elements:
            # 检查版权相关属性
            for attr in copyright_attrs:
                if element.has_attr(attr):
                    value = element.get(attr)
                    if value:
                        copyright_info['copyright_attributes'].append({
                            'attribute': attr,
                            'value': value,
                            'tag': element.name
                        })
            
            # 检查作者相关属性
            for attr in author_attrs:
                if element.has_attr(attr):
                    value = element.get(attr)
                    if value:
                        copyright_info['author_attributes'].append({
                            'attribute': attr,
                            'value': value,
                            'tag': element.name
                        })
            
            # 检查属性值中的关键词
            for attr_name, attr_value in element.attrs.items():
                if isinstance(attr_value, str):
                    for keyword in keywords:
                        if keyword.lower() in attr_value.lower():
                            copyright_info['keyword_matches'].append({
                                'attribute': attr_name,
                                'value': attr_value,
                                'keyword': keyword,
                                'tag': element.name
                            })
        
        # 检查meta标签
        copyright_meta = soup.find('meta', attrs={'name': 'copyright'})
        if copyright_meta:
            copyright_info['copyright_attributes'].append({
                'attribute': 'meta[name="copyright"]',
                'value': copyright_meta.get('content', ''),
                'tag': 'meta'
            })
        
        # 查找版权相关的文本内容
        copyright_selectors = [
            '[class*="copyright"]',
            '[id*="copyright"]',
            'footer',
            '.footer'
        ]
        
        for selector in copyright_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text().strip()
                if text and ('©' in text or 'copyright' in text.lower() or '版权' in text):
                    copyright_info['keyword_matches'].append({
                        'attribute': 'text_content',
                        'value': text,
                        'keyword': '版权相关文本',
                        'tag': element.name
                    })
        
        return copyright_info
    
    def extract_article_link(self, soup):
        """提取文章链接"""
        # 首先尝试从JavaScript变量中提取
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string:
                # 查找 var msg_link = "https://mp.weixin.qq.com/s/lkH9tCtBykTbHgD8eRETWA";
                link_match = re.search(r"var\s+msg_link\s*=\s*['\"]([^'\"]*)['\"];", script.string)
                if link_match:
                    return link_match.group(1).strip()
        
        # 备用方案：从当前URL或canonical链接中提取
        canonical = soup.find('link', {'rel': 'canonical'})
        if canonical and canonical.get('href'):
            return canonical.get('href')
        
        return None
    
    def extract_meta_tags(self, soup):
        """提取所有Meta标签"""
        meta_tags = []
        for meta in soup.find_all('meta'):
            tag_info = {}
            for attr in ['name', 'content', 'property', 'http-equiv']:
                if meta.get(attr):
                    tag_info[attr] = meta.get(attr)
            if tag_info:
                meta_tags.append(tag_info)
        return meta_tags
    
    def extract_scripts(self, soup):
        """提取脚本标签信息"""
        scripts = []
        for script in soup.find_all('script'):
            script_info = {}
            if script.get('src'):
                script_info['src'] = script.get('src')
            if script.string:
                script_info['inline'] = True
                script_info['length'] = len(script.string)
            scripts.append(script_info)
        return scripts
    
    def extract_labels(self, soup):
        """提取Label标签"""
        labels = []
        for label in soup.find_all('label'):
            label_info = {
                'text': label.get_text().strip(),
                'for': label.get('for')
            }
            labels.append(label_info)
        return labels
    
    def extract_seo_info(self, soup):
        """提取SEO信息"""
        seo_info = {}
        
        # Description
        desc_meta = soup.find('meta', attrs={'name': 'description'})
        if desc_meta:
            seo_info['description'] = desc_meta.get('content')
        
        # Keywords
        keywords_meta = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_meta:
            seo_info['keywords'] = keywords_meta.get('content')
        
        # Viewport
        viewport_meta = soup.find('meta', attrs={'name': 'viewport'})
        if viewport_meta:
            seo_info['viewport'] = viewport_meta.get('content')
        
        return seo_info