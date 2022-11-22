import setuptools

setuptools.setup(
    name="roi_boy",
    install_requires=["numpy", "matplotlib", "scikit-image", "uvicorn", "fastapi"],
    packages=["roi_boy", "roi_boy.backend"],
    package_data={"roi_boy": ["templates/*", "static/*"]},
)
