from distutils.core import setup

setup(
    name="pytermimg",
    version="0.1.0b3",
    python_requires='>3.6',
    packages=["termimg", "termimg.printers"],
    license="MIT",
    long_description="See https://github.com/gyf304/pytermimg",
    author="Yifan Gu",
    author_email="dev@yifangu.com",
    install_requires=["pillow>=8.3.1"]
)
