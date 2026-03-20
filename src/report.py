"""
报告生成模块
"""

import json
from pathlib import Path
from typing import List
from datetime import datetime

from .dedup import DuplicateGroup


class ReportGenerator:
    """报告生成器"""
    
    def __init__(self, groups: List[DuplicateGroup]):
        self.groups = groups
    
    def generate_html(self, output_path: str) -> str:
        """生成 HTML 报告"""
        html = self._build_html()
        Path(output_path).write_text(html, encoding='utf-8')
        return output_path
    
    def generate_json(self, output_path: str) -> str:
        """生成 JSON 报告"""
        data = {
            'generated_at': datetime.now().isoformat(),
            'total_groups': len(self.groups),
            'total_duplicates': sum(len(g.duplicates) for g in self.groups),
            'groups': [g.to_dict() for g in self.groups],
        }
        Path(output_path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
        return output_path
    
    def _build_html(self) -> str:
        """构建 HTML 内容"""
        total_duplicates = sum(len(g.duplicates) for g in self.groups)
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 照片去重报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            color: #333;
            font-size: 28px;
            margin-bottom: 10px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }}
        .stat-card .number {{
            font-size: 36px;
            font-weight: bold;
        }}
        .stat-card .label {{
            font-size: 14px;
            opacity: 0.9;
            margin-top: 5px;
        }}
        .group {{
            background: white;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }}
        .group-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #f0f0f0;
        }}
        .group-title {{
            font-size: 16px;
            color: #333;
            font-weight: 600;
        }}
        .group-hash {{
            font-family: monospace;
            font-size: 12px;
            color: #666;
            background: #f5f5f5;
            padding: 4px 8px;
            border-radius: 4px;
        }}
        .file-list {{
            display: grid;
            gap: 10px;
        }}
        .file-item {{
            display: flex;
            align-items: center;
            padding: 12px;
            background: #f8f9fa;
            border-radius: 8px;
            transition: all 0.2s;
        }}
        .file-item:hover {{
            background: #e9ecef;
        }}
        .file-item.best {{
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border: 2px solid #28a745;
        }}
        .file-item.duplicate {{
            background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
            border: 2px solid #dc3545;
        }}
        .file-icon {{
            width: 40px;
            height: 40px;
            background: #dee2e6;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 12px;
            font-size: 20px;
        }}
        .file-info {{
            flex: 1;
        }}
        .file-path {{
            font-size: 14px;
            color: #333;
            word-break: break-all;
        }}
        .file-meta {{
            font-size: 12px;
            color: #666;
            margin-top: 4px;
        }}
        .file-badge {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        .badge-best {{
            background: #28a745;
            color: white;
        }}
        .badge-duplicate {{
            background: #dc3545;
            color: white;
        }}
        .footer {{
            text-align: center;
            color: rgba(255,255,255,0.8);
            margin-top: 30px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🖼️ AI 照片去重报告</h1>
            <p style="color: #666;">生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <div class="stats">
                <div class="stat-card">
                    <div class="number">{len(self.groups)}</div>
                    <div class="label">重复组</div>
                </div>
                <div class="stat-card">
                    <div class="number">{total_duplicates}</div>
                    <div class="label">重复文件</div>
                </div>
                <div class="stat-card">
                    <div class="number">{sum(sum(g.file_sizes.values()) for g in self.groups) / 1024 / 1024:.1f}</div>
                    <div class="label">总大小 (MB)</div>
                </div>
            </div>
        </div>
"""
        
        for i, group in enumerate(self.groups, 1):
            html += self._build_group_html(i, group)
        
        html += """
        <div class="footer">
            <p>由 AI Photo Deduplicator 生成</p>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def _build_group_html(self, index: int, group: DuplicateGroup) -> str:
        """构建单个组的 HTML"""
        html = f"""
        <div class="group">
            <div class="group-header">
                <span class="group-title">📁 重复组 #{index}</span>
                <span class="group-hash">{group.hash_value[:16]}...</span>
            </div>
            <div class="file-list">
"""
        
        best = group.best_quality_file
        for file_path in group.files:
            is_best = file_path == best
            size_mb = group.file_sizes[file_path] / 1024 / 1024
            css_class = "best" if is_best else "duplicate"
            badge_class = "badge-best" if is_best else "badge-duplicate"
            badge_text = "✓ 保留" if is_best else "✗ 重复"
            
            html += f"""
                <div class="file-item {css_class}">
                    <div class="file-icon">🖼️</div>
                    <div class="file-info">
                        <div class="file-path">{file_path}</div>
                        <div class="file-meta">{size_mb:.2f} MB</div>
                    </div>
                    <span class="file-badge {badge_class}">{badge_text}</span>
                </div>
"""
        
        html += """
            </div>
        </div>
"""
        return html
