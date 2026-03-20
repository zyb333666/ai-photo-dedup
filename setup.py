from setuptools import setup, find_packages

setup(
    name="ai-photo-dedup",
    version="1.0.0",
    description="AI 智能清理重复照片",
    author="zyb333666",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "Pillow>=9.0.0",
        "imagehash>=4.3.1",
        "tqdm>=4.62.0",
        "click>=8.0.0",
        "scikit-learn>=1.0.0",
        "torch>=1.10.0",
        "torchvision>=0.11.0",
        "transformers>=4.20.0",
        "send2trash>=1.8.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "photo-dedup=src.cli:main",
        ],
    },
)
