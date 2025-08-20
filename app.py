from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import json
import tempfile
from werkzeug.utils import secure_filename
from pdf_analyzer import PDFAnalyzer

app = Flask(__name__)
CORS(app)

# 配置
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()  # 使用系统临时目录
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# 确保上传目录存在
try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
except Exception as e:
    print(f"Warning: Could not create upload folder: {e}")
    app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    filepath = None
    try:
        print("开始处理文件上传请求", flush=True)
        
        if 'file' not in request.files:
            return jsonify({'error': '没有选择文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # 使用临时文件确保唯一性
            import uuid
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            print(f"保存文件到: {filepath}", flush=True)
            file.save(filepath)
            
            # 分析PDF
            print("开始分析PDF", flush=True)
            analyzer = PDFAnalyzer()
            results = analyzer.analyze_pdf(filepath)
            
            # 确保结果可以JSON序列化
            try:
                json.dumps(results)
            except (TypeError, ValueError) as json_error:
                print(f"JSON序列化错误: {json_error}", flush=True)
                # 创建安全的结果
                safe_results = {
                    'total_qr_codes': results.get('total_qr_codes', 0),
                    'wechat_articles': [],
                    'other_qr_codes': [],
                    'analysis_time': results.get('analysis_time', ''),
                    'error': 'JSON序列化错误，返回简化结果'
                }
                results = safe_results
            
            print("PDF分析完成", flush=True)
            
            return jsonify({
                'success': True,
                'results': results
            })
        else:
            return jsonify({'error': '不支持的文件格式，请上传PDF文件'}), 400
            
    except Exception as e:
        print(f"处理文件时发生错误: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'处理文件时发生错误: {str(e)}'}), 500
    finally:
        # 清理临时文件
        if filepath and os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"已清理临时文件: {filepath}", flush=True)
            except Exception as cleanup_error:
                print(f"清理临时文件失败: {cleanup_error}", flush=True)

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)