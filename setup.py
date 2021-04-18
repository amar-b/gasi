import setuptools

CONSOLE_SCRIPTS = [
    "gasi-vrp = gasi_vrp.gasi_vrp:main",
    # "gasi-vrp-exp = gasi_vrp_experiments.gasi_vrp_experiments:main"
]

INSTALL_REQUIRES = ['matplotlib']

setuptools.setup(
    name = "gasi_vrp",
    version ="1.0.0",
    description = "Solve an instance of the vehicle routing problem using the genetic algorithm with social iteraction",
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    entry_points={"console_scripts": CONSOLE_SCRIPTS},
)