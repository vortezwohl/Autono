import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("LICENSE", "r", encoding="utf-8") as fh:
    license_content = fh.read()

setuptools.setup(
    name="ceo-py",
    version='0.12.0-preview',
    author="vortezwohl",
    author_email="vortez.wohl@gmail.com",
    description="An ultra-lightweight agentic AI framework based on the ReAct paradigm.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license=license_content,
    url="https://github.com/vortezwohl/CEO",
    project_urls={
        "Bug Tracker": "https://github.com/vortezwohl/CEO/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    package_dir={"": "."},
    packages=setuptools.find_packages(where="."),
    python_requires=">=3.10",
    install_requires=[
        'langchain>=0.3.14',
        'langchain-core>=0.3.29',
        'langchain-community>=0.3.14',
        'langchain-openai>=0.2.3',
        'openai>=1.59.3',
        'dashscope>=1.20.14'
    ],
    entry_points={},
    include_package_data=False
)
