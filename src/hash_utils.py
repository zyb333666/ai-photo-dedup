"""
哈希工具模块 - 实现感知哈希和差异哈希算法
"""

import numpy as np
from PIL import Image
import imagehash


class ImageHasher:
    """图片哈希计算器"""
    
    def __init__(self, hash_size: int = 8):
        """
        初始化哈希计算器
        
        Args:
            hash_size: 哈希大小，默认 8 产生 64-bit 哈希
        """
        self.hash_size = hash_size
    
    def phash(self, image_path: str) -> imagehash.ImageHash:
        """
        计算感知哈希 (pHash)
        
        基于 DCT 变换，对图片缩放、亮度变化、压缩鲁棒
        
        Args:
            image_path: 图片路径
            
        Returns:
            ImageHash 对象
        """
        try:
            with Image.open(image_path) as img:
                # 转换为 RGB，处理各种格式
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                return imagehash.phash(img, hash_size=self.hash_size)
        except Exception as e:
            raise ValueError(f"无法计算 pHash: {image_path} - {e}")
    
    def dhash(self, image_path: str) -> imagehash.ImageHash:
        """
        计算差异哈希 (dHash)
        
        基于相邻像素差异，对渐变变化鲁棒
        
        Args:
            image_path: 图片路径
            
        Returns:
            ImageHash 对象
        """
        try:
            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                return imagehash.dhash(img, hash_size=self.hash_size)
        except Exception as e:
            raise ValueError(f"无法计算 dHash: {image_path} - {e}")
    
    def whash(self, image_path: str) -> imagehash.ImageHash:
        """
        计算小波哈希 (wHash)
        
        基于小波变换，对细节变化更敏感
        
        Args:
            image_path: 图片路径
            
        Returns:
            ImageHash 对象
        """
        try:
            with Image.open(image_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                return imagehash.whash(img, hash_size=self.hash_size)
        except Exception as e:
            raise ValueError(f"无法计算 wHash: {image_path} - {e}")
    
    def compute_all(self, image_path: str) -> dict:
        """
        计算所有类型的哈希
        
        Args:
            image_path: 图片路径
            
        Returns:
            包含各种哈希的字典
        """
        return {
            'phash': str(self.phash(image_path)),
            'dhash': str(self.dhash(image_path)),
            'whash': str(self.whash(image_path)),
        }


def hamming_distance(hash1: imagehash.ImageHash, hash2: imagehash.ImageHash) -> int:
    """
    计算两个哈希之间的汉明距离
    
    Args:
        hash1: 第一个哈希
        hash2: 第二个哈希
        
    Returns:
        汉明距离（不同位的数量）
    """
    return hash1 - hash2


def similarity_score(hash1: imagehash.ImageHash, hash2: imagehash.ImageHash) -> float:
    """
    计算两个哈希的相似度分数
    
    Args:
        hash1: 第一个哈希
        hash2: 第二个哈希
        
    Returns:
        相似度分数 (0-1)，1 表示完全相同
    """
    distance = hamming_distance(hash1, hash2)
    max_distance = len(hash1.hash) ** 2
    return 1 - (distance / max_distance)
