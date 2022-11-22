import setuptools

setuptools.setup(
    name="pyroi",
    install_requires=["numpy", "matplotlib", "scikit-image", "uvicorn", "fastapi"],
    packages=["pyroi", "pyroi.backend"],
    package_data={"pyroi": ["templates/*", "static/*"]},
)
