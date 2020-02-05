import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mysugr_persistence",
    version="0.0.1.devl",
    author="mySugr Medical Research Department",
    author_email="richard.biven@mysugr.com",
    description="mysugr_persistence package will allow connecting to mySugr databases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rbiven",
    license="MIT",
    packages=setuptools.find_packages(),
    # data_files=[('connection', ['persistence/connection.py'])],
    classifiers=[
        'Development Status :: 0 - Alpha',
        'Intended Audience :: mySugr Developers',
        'Topic :: Software Development :: Data Science Database Connection',
        "License :: OSI Approved :: MIT License",
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6, <3.8',
)
