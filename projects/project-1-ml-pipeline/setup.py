"""Setup script for ML Pipeline package."""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="ml-pipeline",
    version="1.0.0",
    author="AI Infrastructure Curriculum",
    author_email="ai-infra-curriculum@joshua-ferguson.com",
    description="Production ML Pipeline for Customer Churn Prediction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ai-infra-curriculum/ai-infra-mlops-solutions",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ml-train=models.train:main",
            "ml-serve=api.server:main",
            "ml-predict=models.predict:main",
        ],
    },
)
