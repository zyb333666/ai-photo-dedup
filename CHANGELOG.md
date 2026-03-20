# 更新日志

## [1.0.0] - 2026-03-21

### ✨ 新增功能
- 初始版本发布
- pHash/dHash/wHash 感知哈希算法
- CLIP AI 特征提取支持
- HTML/JSON 双格式报告
- 完整的命令行工具

### 🔧 技术栈
- Python 3.8+
- Pillow + imagehash
- PyTorch + Transformers (可选)
- Click CLI 框架

### 📖 使用方法
```bash
# 安装
pip install -r requirements.txt

# 扫描
python -m src.cli scan ./photos --action move
```
