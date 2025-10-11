from setuptools import setup, find_packages

setup(
    name="sv_to_ipxact",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "lxml>=4.9.0",
        "pyverilog>=1.3.0",
    ],
    entry_points={
        "console_scripts": [
            "sv_to_ipxact=sv_to_ipxact.main:main",
        ],
    },
    python_requires=">=3.8",
)
