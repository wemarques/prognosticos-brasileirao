"""
Setup file para garantir que os módulos sejam importados corretamente
"""
from setuptools import setup, find_packages

setup(
    name="prognosticos-brasileirao",
    version="1.0.0",
    packages=find_packages(),
    python_requires=">=3.9",
)
