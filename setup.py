"""
    Setup file for fhirdrill.
    Use setup.cfg to configure your project.

    This file was generated with PyScaffold 4.1.5.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: https://pyscaffold.org/
"""
from setuptools import setup

# import toml


# def get_install_requirements():
#    """_summary_
#
#    Returns:
#        _type_: _description_
#    """
#    try:
#        # read my pipfile
#        with open ('Pipfile', 'r') as fh:
#            pipfile = fh.read()
#        # parse the toml
#        pipfile_toml = toml.loads(pipfile)
#    except FileNotFoundError:
#        return []    # if the package's key isn't there then just return an empty
#    # list
#    try:
#        required_packages = pipfile_toml['packages'].items()
#    except KeyError:
#        return []
#     # If a version/range is specified in the Pipfile honor it
#     # otherwise just list the package
#
#    return [f"{pkg}{ver}" if ver != "*" else pkg for pkg,ver in required_packages]

if __name__ == "__main__":
    try:
        setup(
            install_requires=[
                "fhirpy",
                "requests",
                "pydgraph",
                "pandas",
                "numpy",
                "matplotlib",
                "toml",
                "fhir.resources",
                "authlib",
                "pyjwt",
                "tqdm",
                "python-dotenv[cli]",
                "apache-age-python",
                "psycopg2",
                "prefect",
                "dagster",
                "dagit",
                "click",
                "black",
                "typeguard",
                "pipenv",
                "python-magic",
                "dicomweb-client",
            ],
            #                install_requires = get_install_requirements(),
            #                use_scm_version={
            # https://github.com/pypa/setuptools_scm
            #                    "version_scheme": "python-simplified-semver",
            #                    "local_scheme": "no-local-version"
            #                    }
        )
    except:  # noqa
        print(
            "\n\nAn error occurred while building the project, "
            "please ensure you have the most updated version of setuptools, "
            "setuptools_scm and wheel with:\n"
            "   pip install -U setuptools setuptools_scm wheel\n\n"
        )
        raise