"""
核心去重逻辑模块
"""

import os
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import json
from tqdm import tqdm

from .hash_utils import ImageHasher, hamming_distance
from .ai_features import AIFeatureExtractor


class DuplicateGroup:
    """重复图片组"""
    
    def __init__(self, hash_value: str):
        self.hash_value = hash_value
        self.files: List[str] = []
        self.file_sizes: Dict[str, int] = {}
        self.similarity_scores: Dict[str, float] = {}
    
    def add(self, file_path: str, similarity: float = 1.0):
        """添加文件到组"""
        self.files.append(file_path)
        self.file_sizes[file_path] = os.path.getsize(file_path)
        self.similarity_scores[file_path] = similarity
    
    @property
    def best_quality_file(self) -> str:
        """返回质量最好的文件（文件大小最大通常意味着质量最高）"""
        return max(self.files, key=lambda f: self.file_sizes[f])
    
    @property
    def duplicates(self) -> List[str]:
        """返回重复文件列表（排除最佳质量的）"""
        best = self.best_quality_file
        return [f for f in self.files if f != best]
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'hash': self.hash_value,
            'files': self.files,
            'file_sizes': self.file_sizes,
            'similarity_scores': self.similarity_scores,
            'best_quality': self.best_quality_file,
            'duplicates': self.duplicates,
        }


class PhotoDeduplicator:
    """照片去重器"""
    
    # 支持的图片格式
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif'}
    
    def __init__(
        self,
        threshold: float = 0.9,
        hash_size: int = 8,
        use_ai: bool = False,
        ai_threshold: float = 0.95,
    ):
        """
        初始化去重器
        
        Args:
            threshold: 哈希相似度阈值 (0-1)，越大越严格
            hash_size: 哈希大小
            use_ai: 是否使用 AI 特征辅助判断
            ai_threshold: AI 特征相似度阈值
        """
        self.threshold = threshold
        self.hash_size = hash_size
        self.use_ai = use_ai
        self.ai_threshold = ai_threshold
        
        self.hasher = ImageHasher(hash_size=hash_size)
        self.ai_extractor = AIFeatureExtractor() if use_ai else None
        
        # 计算最大汉明距离
        self.max_hamming_distance = int((1 - threshold) * (hash_size ** 2))
    
    def scan_directory(
        self,
        directory: str,
        recursive: bool = True,
    ) -> List[DuplicateGroup]:
        """
        扫描目录查找重复图片
        
        Args:
            directory: 目标目录
            recursive: 是否递归扫描子目录
            
        Returns:
            重复组列表
        """
        directory = Path(directory)
        if not directory.exists():
            raise ValueError(f"目录不存在: {directory}")
        
        # 收集所有图片文件
        image_files = self._collect_images(directory, recursive)
        print(f"找到 {len(image_files)} 个图片文件")
        
        if len(image_files) < 2:
            return []
        
        # 计算哈希
        print("正在计算图片哈希...")
        hash_dict = self._compute_hashes(image_files)
        
        # 查找重复组
        print("正在查找重复图片...")
        duplicate_groups = self._find_duplicates(hash_dict)
        
        # 如果使用 AI，进行语义相似度验证
        if self.use_ai and self.ai_extractor and self.ai_extractor.available:
            print("正在使用 AI 验证相似度...")
            duplicate_groups = self._ai_verify_duplicates(duplicate_groups)
        
        return duplicate_groups
    
    def _collect_images(self, directory: Path, recursive: bool) -> List[str]:
        """收集图片文件"""
        images = []
        pattern = "**/*" if recursive else "*"
        
        for path in directory.glob(pattern):
            if path.is_file() and path.suffix.lower() in self.SUPPORTED_FORMATS:
                images.append(str(path))
        
        return images
    
    def _compute_hashes(self, image_files: List[str]) -> Dict[str, List[str]]:
        """计算所有图片的哈希，按哈希值分组"""
        hash_dict = defaultdict(list)
        
        for file_path in tqdm(image_files, desc="计算哈希"):
            try:
                phash = self.hasher.phash(file_path)
                hash_dict[str(phash)].append(file_path)
            except Exception as e:
                print(f"跳过文件 {file_path}: {e}")
        
        return hash_dict
    
    def _find_duplicates(self, hash_dict: Dict[str, List[str]]) -> List[DuplicateGroup]:
        """从哈希字典中找出重复组"""
        groups = []
        
        for hash_value, files in hash_dict.items():
            if len(files) > 1:
                group = DuplicateGroup(hash_value)
                for f in files:
                    group.add(f, similarity=1.0)
                groups.append(group)
        
        return groups
    
    def _ai_verify_duplicates(self, groups: List[DuplicateGroup]) -> List[DuplicateGroup]:
        """使用 AI 特征验证重复组"""
        verified_groups = []
        
        for group in tqdm(groups, desc="AI 验证"):
            # 提取组内所有图片的特征
            features = {}
            for file_path in group.files:
                feat = self.ai_extractor.extract(file_path)
                if feat is not None:
                    features[file_path] = feat
            
            # 如果无法提取特征，保留原组
            if len(features) < 2:
                verified_groups.append(group)
                continue
            
            # 基于 AI 相似度重新分组
            ai_groups = self._cluster_by_ai_features(features)
            verified_groups.extend(ai_groups)
        
        return verified_groups
    
    def _cluster_by_ai_features(
        self,
        features: Dict[str, np.ndarray]
    ) -> List[DuplicateGroup]:
        """基于 AI 特征聚类"""
        from sklearn.cluster import DBSCAN
        
        files = list(features.keys())
        feat_matrix = np.array([features[f] for f in files])
        
        # 使用余弦距离聚类
        clustering = DBSCAN(
            eps=1 - self.ai_threshold,
            min_samples=2,
            metric='cosine'
        ).fit(feat_matrix)
        
        # 按聚类标签分组
        clusters = defaultdict(list)
        for idx, label in enumerate(clustering.labels_):
            if label >= 0:  # 排除噪声点 (-1)
                clusters[label].append(files[idx])
        
        groups = []
        for label, cluster_files in clusters.items():
            if len(cluster_files) > 1:
                group = DuplicateGroup(f"ai_cluster_{label}")
                for f in cluster_files:
                    group.add(f)
                groups.append(group)
        
        return groups
    
    def move_duplicates(
        self,
        groups: List[DuplicateGroup],
        destination: Optional[str] = None,
        confirm: bool = True,
    ) -> List[str]:
        """
        移动重复文件
        
        Args:
            groups: 重复组列表
            destination: 目标目录，None 则移动到回收站
            confirm: 是否确认操作
            
        Returns:
            被移动的文件列表
        """
        moved_files = []
        
        for group in groups:
            for dup_file in group.duplicates:
                if confirm:
                    print(f"移动: {dup_file}")
                
                try:
                    if destination:
                        # 移动到指定目录
                        dest_path = Path(destination) / Path(dup_file).name
                        Path(dup_file).rename(dest_path)
                    else:
                        # 移动到回收站
                        from send2trash import send2trash
                        send2trash(dup_file)
                    
                    moved_files.append(dup_file)
                except Exception as e:
                    print(f"移动失败 {dup_file}: {e}")
        
        return moved_files
    
    def delete_duplicates(
        self,
        groups: List[DuplicateGroup],
        confirm: bool = True,
    ) -> List[str]:
        """
        永久删除重复文件（谨慎使用）
        
        Args:
            groups: 重复组列表
            confirm: 是否确认操作
            
        Returns:
            被删除的文件列表
        """
        deleted_files = []
        
        for group in groups:
            for dup_file in group.duplicates:
                if confirm:
                    print(f"删除: {dup_file}")
                
                try:
                    os.remove(dup_file)
                    deleted_files.append(dup_file)
                except Exception as e:
                    print(f"删除失败 {dup_file}: {e}")
        
        return deleted_files
