# Example data for `artblog` static site generator

## Developer Notes

### Installation & Setup
- Keep this virtual environment separate from the one used for `artblog`

- Install Python 3 from `python.org`

- Then install Python packages in a virtual environment:
```bat
:: Windows example
cd REPOSITORY_PATH
python -m venv venv2
activate.bat
venv2\Scripts\python -m pip install --upgrade pip setuptools wheel
venv2\Scripts\python -m pip install --upgrade python-lorem
venv2\Scripts\python -m pip install --upgrade Pillow
venv2\Scripts\python -m pip install --upgrade python-slugify
```

### Generate Data
- **IMPORTANT**: Ensure the folder paths in `genexampledata.py` at the top are correct.

- Generate data:

```bat
cd /path/to/artblog/exampledata/
activate.bat
python genexampledata.py
```