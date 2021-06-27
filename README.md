# artblog
[![PyPI version](https://badge.fury.io/py/artblog.svg)](https://badge.fury.io/py/artblog)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Static site generator for simple blogs where each article usually includes an image/artwork/photo.

Goals:
- Simplicity (minimal configurability)
- Source data from multiple Git repositories

Limitations:
- No e-commerce features

## Easy To Use
- **Install**: `python -m pip install artblog`
- **Generate config.yml**: artblog
- **Configure**: Edit a `config.yml` file
- **Generate**: `artblog path/to/config.yml`
- **Copy to your web host**: `scp -r output/* hosting_site:~/www/.`

