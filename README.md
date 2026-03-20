# AI 智能清理重复照片

基于感知哈希算法 (Perceptual Hashing) 和 AI 特征提取，自动检测并清理重复/相似照片。

## ✨ 功能特性

- 🔍 **智能检测** - 使用 pHash 和 dHash 算法检测重复/相似图片
- 🤖 **AI 增强** - 可选使用 CLIP 模型提取语义特征
- 📊 **可视化报告** - 生成 HTML 报告展示重复组
- ⚡ **高性能** - 多线程处理，支持 GPU 加速
- 🛡️ **安全删除** - 支持移动到回收站而非永久删除

## 🚀 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 扫描指定目录
python -m src.cli scan ~/Pictures

# 生成报告并清理
python -m src.cli scan ~/Pictures --action move --output ./duplicates_report.html
```

## 📖 使用方法

### 命令行工具

```bash
# 仅扫描，不执行删除
python -m src.cli scan ./photos

# 扫描并移动重复文件到回收站
python -m src.cli scan ./photos --action move

# 扫描并永久删除（谨慎使用）
python -m src.cli scan ./photos --action delete

# 自定义相似度阈值（0-1，越小越严格）
python -m src.cli scan ./photos --threshold 0.85
```

### Python API

```python
from src.dedup import PhotoDeduplicator

dedup = PhotoDeduplicator(threshold=0.9)
results = dedup.scan_directory("./photos")
dedup.move_duplicates(results, confirm=True)
```

## 🔧 技术原理

1. **感知哈希 (pHash)** - 计算图片的 64-bit 指纹，相似图片指纹相近
2. **差异哈希 (dHash)** - 检测图片渐变特征，对缩放/亮度变化鲁棒
3. **汉明距离** - 比较哈希指纹的相似度
4. **AI 特征 (可选)** - 使用 CLIP 模型提取语义特征

## 📁 项目结构

```
ai-photo-dedup/
├── src/
│   ├── __init__.py
│   ├── cli.py          # 命令行入口
│   ├── dedup.py        # 核心去重逻辑
│   ├── hash_utils.py   # 哈希算法实现
│   ├── ai_features.py  # AI 特征提取
│   └── report.py       # 报告生成
├── tests/
│   └── test_dedup.py
├── docs/
│   └── algorithm.md
├── requirements.txt
├── setup.py
└── README.md
```

## 📝 许可证

MIT License
