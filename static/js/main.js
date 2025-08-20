// 全局变量
let analysisResults = null;

// DOM元素
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const progressContainer = document.getElementById('progressContainer');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const resultsContainer = document.getElementById('resultsContainer');
const errorContainer = document.getElementById('errorContainer');
const errorMessage = document.getElementById('errorMessage');

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    initializeTooltips();
});

// 初始化事件监听器
function initializeEventListeners() {
    // 文件输入变化
    fileInput.addEventListener('change', handleFileSelect);
    
    // 拖拽事件
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    
    // 点击上传区域
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });
    
    // 阻止默认拖拽行为
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        document.addEventListener(eventName, preventDefaults, false);
    });
}

// 初始化工具提示
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// 阻止默认事件
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// 处理拖拽悬停
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('dragover');
}

// 处理拖拽离开
function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
}

// 处理文件拖拽放置
function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

// 处理文件选择
function handleFileSelect(e) {
    const file = e.target.files[0];
    if (file) {
        handleFile(file);
    }
}

// 处理文件
function handleFile(file) {
    // 验证文件类型
    if (!file.type.includes('pdf')) {
        showError('请选择PDF文件');
        return;
    }
    
    // 验证文件大小 (16MB)
    if (file.size > 16 * 1024 * 1024) {
        showError('文件大小不能超过16MB');
        return;
    }
    
    // 开始上传和分析
    uploadAndAnalyze(file);
}

// 上传和分析文件
function uploadAndAnalyze(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    // 显示进度条
    showProgress();
    hideError();
    hideResults();
    
    // 模拟进度更新
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += Math.random() * 15;
        if (progress > 90) {
            progress = 90;
        }
        updateProgress(progress);
    }, 500);
    
    // 发送请求
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        clearInterval(progressInterval);
        updateProgress(100);
        
        setTimeout(() => {
            hideProgress();
            
            if (data.success) {
                analysisResults = data.results;
                displayResults(data.results);
            } else {
                showError(data.error || '分析失败');
            }
        }, 500);
    })
    .catch(error => {
        clearInterval(progressInterval);
        hideProgress();
        showError('网络错误: ' + error.message);
    });
}

// 显示进度条
function showProgress() {
    progressContainer.classList.remove('d-none');
    updateProgress(0);
}

// 隐藏进度条
function hideProgress() {
    progressContainer.classList.add('d-none');
}

// 更新进度
function updateProgress(percent) {
    progressBar.style.width = percent + '%';
    progressText.textContent = Math.round(percent) + '%';
}

// 显示错误信息
function showError(message) {
    errorMessage.textContent = message;
    errorContainer.classList.remove('d-none');
    errorContainer.scrollIntoView({ behavior: 'smooth' });
}

// 隐藏错误信息
function hideError() {
    errorContainer.classList.add('d-none');
}

// 隐藏结果
function hideResults() {
    resultsContainer.classList.add('d-none');
}

// 显示分析结果
function displayResults(results) {
    // 更新统计信息
    document.getElementById('totalQrCodes').textContent = results.total_qr_codes || 0;
    document.getElementById('wechatArticles').textContent = results.wechat_articles?.length || 0;
    document.getElementById('otherLinks').textContent = results.other_qr_codes?.length || 0;
    
    // 显示微信文章
    displayWechatArticles(results.wechat_articles || []);
    
    // 显示其他二维码
    displayOtherQrCodes(results.other_qr_codes || []);
    
    // 显示结果容器
    resultsContainer.classList.remove('d-none');
    resultsContainer.classList.add('fade-in');
    resultsContainer.scrollIntoView({ behavior: 'smooth' });
}

// 显示微信文章列表
function displayWechatArticles(articles) {
    const container = document.getElementById('articlesList');
    
    if (articles.length === 0) {
        container.innerHTML = '<div class="alert alert-info"><i class="fas fa-info-circle me-2"></i>未发现微信公众号文章</div>';
        return;
    }
    
    container.innerHTML = articles.map((article, index) => {
        return createArticleCard(article, index);
    }).join('');
    
    // 初始化详情切换按钮
    initializeToggleButtons();
}

// 创建文章卡片
function createArticleCard(article, index) {
    const hasError = article.error;
    const title = article.title || '无法获取标题';
    const publishTime = article.publish_time || '未知';
    const accountName = article.account_name || '未知';
    const author = article.author || '未知';
    const articleLink = article.article_link || article.url;
    
    return `
        <div class="article-card">
            <div class="d-flex justify-content-between align-items-start mb-2">
                <a href="${article.url}" target="_blank" class="article-title">
                    ${title}
                </a>
                <span class="badge bg-primary">第${article.page_number || '?'}页</span>
            </div>
            
            ${hasError ? `
                <div class="alert alert-warning mb-2">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    ${article.error}
                </div>
            ` : `
                <div class="article-meta">
                    <div class="row">
                        <div class="col-md-6">
                            <i class="fas fa-calendar"></i>发布时间: ${publishTime}
                        </div>
                        <div class="col-md-6">
                            <i class="fab fa-weixin"></i>公众号: ${accountName}
                        </div>
                    </div>
                    <div class="row mt-1">
                        <div class="col-md-6">
                            <i class="fas fa-user"></i>作者: ${author}
                        </div>
                        <div class="col-md-6">
                            <i class="fas fa-link"></i>页面位置: 第${article.page_number || '?'}页
                        </div>
                    </div>
                    ${articleLink && articleLink !== article.url ? `
                    <div class="row mt-1">
                        <div class="col-12">
                            <i class="fas fa-external-link-alt"></i>文章链接: 
                            <a href="${articleLink}" target="_blank" class="text-break">${truncateText(articleLink, 60)}</a>
                        </div>
                    </div>
                    ` : ''}
                </div>
                
                <button class="btn btn-toggle btn-sm" onclick="toggleDetails(${index})">
                    <i class="fas fa-chevron-down me-1"></i>查看详细信息
                </button>
                
                <div id="details-${index}" class="details-section d-none">
                    ${createDetailsSection(article)}
                </div>
            `}
        </div>
    `;
}

// 创建详情部分
function createDetailsSection(article) {
    let html = '';
    
    // SEO信息
    if (article.seo_info && Object.keys(article.seo_info).length > 0) {
        html += `
            <div class="mb-3">
                <div class="details-title"><i class="fas fa-search me-2"></i>SEO信息</div>
                ${Object.entries(article.seo_info).map(([key, value]) => 
                    `<span class="meta-tag">${key}: ${value}</span>`
                ).join('')}
            </div>
        `;
    }
    
    // Meta标签
    if (article.meta_tags && article.meta_tags.length > 0) {
        html += `
            <div class="mb-3">
                <div class="details-title"><i class="fas fa-tags me-2"></i>Meta标签 (${article.meta_tags.length}个)</div>
                <div class="small text-muted">
                    ${article.meta_tags.slice(0, 5).map(tag => {
                        const tagText = tag.name ? `${tag.name}: ${tag.content || ''}` : 
                                       tag.property ? `${tag.property}: ${tag.content || ''}` : 
                                       JSON.stringify(tag);
                        return `<span class="meta-tag">${tagText}</span>`;
                    }).join('')}
                    ${article.meta_tags.length > 5 ? `<span class="text-muted">...还有${article.meta_tags.length - 5}个</span>` : ''}
                </div>
            </div>
        `;
    }
    
    // 脚本信息
    if (article.scripts && article.scripts.length > 0) {
        html += `
            <div class="mb-3">
                <div class="details-title"><i class="fas fa-code me-2"></i>脚本标签 (${article.scripts.length}个)</div>
                <div class="small text-muted">
                    外部脚本: ${article.scripts.filter(s => s.src).length}个，
                    内联脚本: ${article.scripts.filter(s => s.inline).length}个
                </div>
            </div>
        `;
    }
    
    // 版权信息
    if (article.copyright && typeof article.copyright === 'object') {
        html += `
            <div class="mb-3">
                <div class="details-title"><i class="fas fa-copyright me-2"></i>版权相关信息分析</div>
        `;
        
        // 版权相关属性
        if (article.copyright.copyright_attributes && article.copyright.copyright_attributes.length > 0) {
            html += `
                <div class="mb-2">
                    <strong class="text-primary">版权相关属性:</strong>
                    ${article.copyright.copyright_attributes.map(attr => 
                        `<span class="meta-tag">${attr.tag}[${attr.attribute}]: ${attr.value}</span>`
                    ).join('')}
                </div>
            `;
        }
        
        // 作者相关属性
        if (article.copyright.author_attributes && article.copyright.author_attributes.length > 0) {
            html += `
                <div class="mb-2">
                    <strong class="text-success">作者相关属性:</strong>
                    ${article.copyright.author_attributes.map(attr => 
                        `<span class="meta-tag">${attr.tag}[${attr.attribute}]: ${attr.value}</span>`
                    ).join('')}
                </div>
            `;
        }
        
        // 关键词匹配
        if (article.copyright.keyword_matches && article.copyright.keyword_matches.length > 0) {
            html += `
                <div class="mb-2">
                    <strong class="text-warning">关键词匹配:</strong>
                    ${article.copyright.keyword_matches.map(match => 
                        `<span class="meta-tag">${match.tag}[${match.attribute}]: ${truncateText(match.value, 50)} (匹配: ${match.keyword})</span>`
                    ).join('')}
                </div>
            `;
        }
        
        // 如果没有找到任何版权信息
        if ((!article.copyright.copyright_attributes || article.copyright.copyright_attributes.length === 0) &&
            (!article.copyright.author_attributes || article.copyright.author_attributes.length === 0) &&
            (!article.copyright.keyword_matches || article.copyright.keyword_matches.length === 0)) {
            html += `<div class="text-muted">未找到版权相关信息</div>`;
        }
        
        html += `</div>`;
    } else if (article.copyright && typeof article.copyright === 'string') {
        // 兼容旧版本的字符串格式
        html += `
            <div class="mb-3">
                <div class="details-title"><i class="fas fa-copyright me-2"></i>版权信息</div>
                <span class="meta-tag">${article.copyright}</span>
            </div>
        `;
    }
    
    return html || '<div class="text-muted">暂无详细信息</div>';
}

// 显示其他二维码
function displayOtherQrCodes(qrCodes) {
    const container = document.getElementById('otherQrCodesList');
    
    if (qrCodes.length === 0) {
        container.innerHTML = '<div class="alert alert-info"><i class="fas fa-info-circle me-2"></i>未发现其他二维码链接</div>';
        return;
    }
    
    container.innerHTML = qrCodes.map(qr => `
        <div class="other-qr-item">
            <div class="d-flex justify-content-between align-items-center">
                <div class="flex-grow-1">
                    <a href="${qr.url}" target="_blank">${qr.url}</a>
                </div>
                <span class="badge bg-warning text-dark ms-2">第${qr.page_number}页</span>
            </div>
        </div>
    `).join('');
}

// 初始化切换按钮
function initializeToggleButtons() {
    // 重新初始化工具提示
    initializeTooltips();
}

// 切换详情显示
function toggleDetails(index) {
    const detailsElement = document.getElementById(`details-${index}`);
    const button = detailsElement.previousElementSibling;
    const icon = button.querySelector('i');
    
    if (detailsElement.classList.contains('d-none')) {
        detailsElement.classList.remove('d-none');
        detailsElement.classList.add('fade-in');
        icon.className = 'fas fa-chevron-up me-1';
        button.innerHTML = '<i class="fas fa-chevron-up me-1"></i>隐藏详细信息';
    } else {
        detailsElement.classList.add('d-none');
        icon.className = 'fas fa-chevron-down me-1';
        button.innerHTML = '<i class="fas fa-chevron-down me-1"></i>查看详细信息';
    }
}

// 导出结果
function exportResults() {
    if (!analysisResults) {
        showError('没有可导出的结果');
        return;
    }
    
    const dataStr = JSON.stringify(analysisResults, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `pdf-analysis-${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`;
    link.click();
    
    // 清理URL对象
    URL.revokeObjectURL(link.href);
}

// 工具函数：格式化日期
function formatDate(dateString) {
    if (!dateString) return '未知';
    try {
        const date = new Date(dateString);
        return date.toLocaleString('zh-CN');
    } catch (e) {
        return dateString;
    }
}

// 工具函数：截断文本
function truncateText(text, maxLength = 100) {
    if (!text || text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}