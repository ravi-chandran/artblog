# artblog
[![PyPI version](https://badge.fury.io/py/artblog.svg)](https://badge.fury.io/py/artblog)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Static site generator for art blogs written with markdown and lots of images.

Goals:
- Simplicity (minimal configurability)
- Posts source data from multiple directories (e.g. multiple Git repositories)

Limitations:
- No e-commerce features

## Easy To Use
1. **Install**: `python -m pip install artblog`
2. **Generate config.yml template**: `artblog path/to/config.yml`
3. **Configure**: Edit the `path/to/config.yml` file
4. **Generate**: `artblog path/to/config.yml`
5. **Copy to your web host**: `scp -r output/* hosting_site:~/www/.`

The `config.yml` file is where you specify the information about your site's URL, locations of your content, etc. In step 2 above, you specify where you want to create the template for `config.yml`. After that, you edit this file.

Steps 4 and 5 are repeated as you add articles over time.

