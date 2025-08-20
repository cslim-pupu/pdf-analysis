# 部署到 Render 指南

## 准备工作

1. 确保你有一个 [Render](https://render.com) 账户
2. 将项目代码推送到 GitHub 仓库

## 部署步骤

### 1. 创建 GitHub 仓库

1. 在 GitHub 上创建一个新仓库
2. **选择模板**: 选择 **Python** 模板（这会自动添加适合 Python 项目的 .gitignore）
3. 将本地代码推送到仓库：

```bash
git init
git add .
git commit -m "Initial commit: PDF QR Code Analyzer"
git branch -M main
git remote add origin https://github.com/你的用户名/你的仓库名.git
git push -u origin main
```

### 2. 在 Render 上部署

1. 登录 [Render Dashboard](https://dashboard.render.com)
2. 点击 "New +" 按钮
3. 选择 "Web Service"
4. 连接你的 GitHub 仓库
5. 配置部署设置：
   - **Name**: `pdf-qr-analyzer`（或你喜欢的名称）
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: 选择 `Free`（免费套餐）

### 3. 环境变量设置

在 Render 的环境变量设置中添加：
- `FLASK_ENV`: `production`
- `PORT`: `10000`（Render 会自动设置，通常不需要手动添加）

### 4. 部署完成

- Render 会自动构建和部署你的应用
- 部署完成后，你会获得一个类似 `https://your-app-name.onrender.com` 的 URL
- 首次部署可能需要几分钟时间

## 注意事项

### 免费套餐限制
- Render 免费套餐在无活动时会休眠
- 首次访问可能需要等待 30-60 秒唤醒
- 每月有 750 小时的免费使用时间

### 文件上传限制
- 当前设置最大文件大小为 16MB
- 如需处理更大文件，可以修改 `app.py` 中的 `MAX_CONTENT_LENGTH` 配置

### 性能优化
- 免费套餐性能有限，处理大型 PDF 可能较慢
- 如需更好性能，可考虑升级到付费套餐

## 故障排除

### 常见问题

1. **部署失败**：检查 `requirements.txt` 中的依赖是否正确
2. **应用无法启动**：查看 Render 的日志，检查端口配置
3. **文件上传失败**：确认文件大小不超过限制

### 查看日志

在 Render Dashboard 中：
1. 进入你的服务页面
2. 点击 "Logs" 标签
3. 查看实时日志输出

## 更新部署

当你更新代码时：
1. 将更改推送到 GitHub 仓库
2. Render 会自动检测更改并重新部署
3. 也可以在 Render Dashboard 中手动触发部署

## 自定义域名（可选）

如果你有自己的域名：
1. 在 Render Dashboard 中进入服务设置
2. 添加自定义域名
3. 按照说明配置 DNS 记录

---

部署完成后，你的 PDF 二维码分析工具就可以在线使用了！🎉