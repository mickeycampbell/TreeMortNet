from setuptools import setup, find_packages
import os

# Read version
_version_path = os.path.join(os.path.dirname(__file__), "treemortnet", "version.py")
_version_ns = {}
with open(_version_path) as f:
    exec(f.read(), _version_ns)

# Read requirements
with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="treemortnet",
    version=_version_ns["__version__"],
    description="Prediction of individual tree mortality from NAIP imagery and lidar-delineated crowns",
    author="Mickey Campbell",
    author_email="mickey.campbell@ess.utah.edu",
    packages=find_packages(where="."),  # optional, explicit
    install_requires=requirements,
    python_requires=">=3.11",
    include_package_data=True,  # ensures MANIFEST.in is respected
    zip_safe=False,  # recommended when including non-Python files
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
