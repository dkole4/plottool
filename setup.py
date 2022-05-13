from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

with open("requirements.txt", "r", encoding="utf-8") as file:
    requirements = file.read()

setup(
    name="plotting_tool",
    version="0.0.1",
    author="Denis Kole",
    author_email="denis.kole4@gmail.com",
    license="MIT",
    description="A tool for tracking and plotting cryptocurrency prices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dkole4/plotting_tool",
    py_modules=["plotting_tool"],
    packages=find_packages(),
    install_requires=[requirements],
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    entry_points="""
        [console_scripts]
        plottool=plotting_tool:main
    """
)
