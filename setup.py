from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")


setup(
    name="pytri",
    version="2.0.0",
    description="Pytri, redux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aplbrain/pytri",
    author="Jordan Matelsky",
    author_email="jordan [DOT] matelsky [AT] jhuapl.edu",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="sample, setuptools, development",
    package_dir={"": "."},
    packages=["pytri"],
    python_requires=">=3.6, <4",
    install_requires=["numpy", "networkx", "trimesh", "pythreejs>=2.2.1"],
    project_urls={
        "Source": "https://github.com/aplbrain/pytri",
    },
)
