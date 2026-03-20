"""
AI 特征提取模块 - 使用 CLIP 模型提取语义特征
"""

import torch
import numpy as np
from PIL import Image
from typing import Optional, List


class AIFeatureExtractor:
    """AI 特征提取器"""
    
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32", device: Optional[str] = None):
        """
        初始化 CLIP 特征提取器
        
        Args:
            model_name: CLIP 模型名称
            device: 计算设备 ('cuda', 'cpu', 或 None 自动选择)
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model_name = model_name
        
        try:
            from transformers import CLIPProcessor, CLIPModel
            self.model = CLIPModel.from_pretrained(model_name).to(self.device)
            self.processor = CLIPProcessor.from_pretrained(model_name)
            self.model.eval()
            self.available = True
        except Exception as e:
            print(f"警告: 无法加载 CLIP 模型: {e}")
            self.available = False
    
    def extract(self, image_path: str) -> Optional[np.ndarray]:
        """
        提取图片的语义特征向量
        
        Args:
            image_path: 图片路径
            
        Returns:
            特征向量 (512维)，失败返回 None
        """
        if not self.available:
            return None
        
        try:
            image = Image.open(image_path).convert('RGB')
            inputs = self.processor(images=image, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                image_features = self.model.get_image_features(**inputs)
                # 归一化
                image_features = image_features / image_features.norm(dim=-1, keepdim=True)
            
            return image_features.cpu().numpy().flatten()
        except Exception as e:
            print(f"特征提取失败 {image_path}: {e}")
            return None
    
    def extract_batch(self, image_paths: List[str], batch_size: int = 8) -> List[Optional[np.ndarray]]:
        """
        批量提取特征
        
        Args:
            image_paths: 图片路径列表
            batch_size: 批处理大小
            
        Returns:
            特征向量列表
        """
        if not self.available:
            return [None] * len(image_paths)
        
        results = []
        for i in range(0, len(image_paths), batch_size):
            batch = image_paths[i:i + batch_size]
            batch_results = [self.extract(p) for p in batch]
            results.extend(batch_results)
        
        return results
    
    def cosine_similarity(self, feat1: np.ndarray, feat2: np.ndarray) -> float:
        """
        计算余弦相似度
        
        Args:
            feat1: 特征向量1
            feat2: 特征向量2
            
        Returns:
            相似度 (-1 到 1)
        """
        return float(np.dot(feat1, feat2) / (np.linalg.norm(feat1) * np.linalg.norm(feat2)))
