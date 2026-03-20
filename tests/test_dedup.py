"""
单元测试模块
"""

import unittest
import tempfile
import os
from pathlib import Path
from PIL import Image
import numpy as np

from src.hash_utils import ImageHasher, hamming_distance, similarity_score
from src.dedup import PhotoDeduplicator, DuplicateGroup


class TestImageHasher(unittest.TestCase):
    """测试哈希工具"""
    
    def setUp(self):
        self.hasher = ImageHasher(hash_size=8)
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_test_image(self, filename, size=(100, 100), color=(255, 0, 0)):
        """创建测试图片"""
        img = Image.new('RGB', size, color)
        path = Path(self.temp_dir) / filename
        img.save(path)
        return str(path)
    
    def test_phash_consistency(self):
        """测试 pHash 一致性"""
        img_path = self._create_test_image('test1.jpg', color=(255, 0, 0))
        
        hash1 = self.hasher.phash(img_path)
        hash2 = self.hasher.phash(img_path)
        
        self.assertEqual(hash1, hash2)
    
    def test_similar_images(self):
        """测试相似图片的哈希"""
        img1 = self._create_test_image('test1.jpg', color=(255, 0, 0))
        img2 = self._create_test_image('test2.jpg', color=(255, 1, 0))  # 非常相似
        
        hash1 = self.hasher.phash(img1)
        hash2 = self.hasher.phash(img2)
        
        distance = hamming_distance(hash1, hash2)
        self.assertLess(distance, 10)  # 相似图片汉明距离应较小


class TestDuplicateGroup(unittest.TestCase):
    """测试重复组"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_best_quality_selection(self):
        """测试最佳质量文件选择"""
        group = DuplicateGroup('test_hash')
        
        # 创建模拟文件
        files = ['small.jpg', 'medium.jpg', 'large.jpg']
        sizes = [1000, 5000, 10000]
        
        for f, s in zip(files, sizes):
            path = Path(self.temp_dir) / f
            path.write_text('x' * s)
            group.add(str(path))
        
        best = group.best_quality_file
        self.assertIn('large.jpg', best)


class TestPhotoDeduplicator(unittest.TestCase):
    """测试去重器"""
    
    def setUp(self):
        self.dedup = PhotoDeduplicator(threshold=0.9)
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def _create_test_image(self, filename, size=(100, 100), color=(255, 0, 0)):
        """创建测试图片"""
        img = Image.new('RGB', size, color)
        path = Path(self.temp_dir) / filename
        img.save(path)
        return str(path)
    
    def test_scan_empty_directory(self):
        """测试空目录扫描"""
        groups = self.dedup.scan_directory(self.temp_dir)
        self.assertEqual(len(groups), 0)


if __name__ == '__main__':
    unittest.main()
