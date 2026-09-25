from pathlib import Path
from setuptools import setup, find_packages

this_directory = Path(__file__).parent
readme_path = this_directory / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

setup(
    name="evalkit",
    version="0.1.0",
    description="Evaluation toolkit for LLMs and AI systems",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(include=["evalkit", "evalkit.*"]),
    python_requires=">=3.10",
    install_requires=[],
)
