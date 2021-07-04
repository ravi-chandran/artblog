# Developer Notes

## Virtual Environment Setup for Development
```bat
cd artblog
python -m venv venv1
venv1\Scripts\activate
venv1\Scripts\python -m pip install --upgrade pip setuptools build twine pycodestyle pytest
```

Packages needed for `artblog` itself:
```bat
venv1\Scripts\python -m pip install --upgrade requests pyyaml
venv1\Scripts\python -m pip install mistune==2.0.0rc1
```

## Development Iterations
- [Work in development mode](https://packaging.python.org/guides/distributing-packages-using-setuptools/#working-in-development-mode):
- Perform two basic tests.

```bat
cd artblog
activate.bat
python -m pip install --editable .
pytest -v
```

## Configure TestPyPI and PyPI Access
- Using steps from this [reference](https://packaging.python.org/tutorials/packaging-projects/):

- Create/edit file `.pypirc` in `%HOME%` (Windows) or `$HOME` (Linux):
```
[testpypi]
  username = __token__
  password = enter the token created on test.pypi.org

[pypi]
  username = __token__
  password = enter the token created on pypi.org
```

## Upload To TestPyPI
- Bump version in `setup.py`
- Build and upload
```bat
cd artblog
activate.bat
python -m build
python -m twine upload --repository testpypi dist/*
```

- Install and try it out in a separate `venv`.

- Note that TestPyPI provides the following install. However, if the dependencies cannot be found at `test.pypi.org`, they will need to be installed manually.
```bat
pip install -i https://test.pypi.org/simple/ artblog
```

## Upload To PyPI
- Bump version in `setup.py`
- Build and upload
```bat
cd artblog
activate.bat
python -m build
python -m twine upload dist/*
```
