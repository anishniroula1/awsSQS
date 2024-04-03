from setuptools import setup, find_packages

# Read requirements.txt for install_requires
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="ocr_file",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    description="A package for processing files with OCR.",
    author="Your Name",
    author_email="your.email@example.com",
    license="MIT",
    python_requires=">=3.9",
)
