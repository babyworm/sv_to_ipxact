from setuptools import setup, find_packages

setup(
    name="ipxact-tools",
    version="0.2.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "lxml>=4.9.0",
        "pyverilog>=1.3.0",
    ],
    entry_points={
        "console_scripts": [
            "sv-to-ipxact=sv_to_ipxact.main:main",
            "ipxact-converter=ipxact_version_converter.main:main",
            "validate-ipxact=sv_to_ipxact.validator:main",
        ],
    },
    python_requires=">=3.8",
)
