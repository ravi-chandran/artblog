#!/usr/bin/env python3
# Standard libraries
import argparse
from collections import OrderedDict
from datetime import datetime
import glob
import os
from pprint import pprint
import shutil
import sys
import urllib

# Installed packages
import mistune
import requests
import slugify
import yaml

CMDLINE_APP_NAME = 'ArtBlog - a static site generator'

DATA_HTML_BASE = os.path.join('html', 'base.html')
DATA_HTML_LICENSE = os.path.join('html', 'license.html')
DATA_CSS_STYLE = os.path.join('css', 'style.css')
CONFIG_TEMPLATE = os.path.join('config', 'config.yml')

MARKDOWN_EXTENSIONS = ('.md', '.mkd', '.mkdn', '.mdown', '.markdown')


def get_user_inputs():
    '''Get user arguments.'''
    parser = argparse.ArgumentParser(
        description=CMDLINE_APP_NAME,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('config_yml', help='YAML configuration file')
    parser.add_argument('--preserve_output', '-p',
                        action='store_true',
                        help='if set, current output folder will be preserved')
    args = parser.parse_args()

    if not os.path.isfile(args.config_yml):
        print(f'Generating template file: {args.config_yml}')

        with open(package_data_file(CONFIG_TEMPLATE),
                'rt', encoding='utf-8') as f:
            config_yml_txt = f.read()

        with open(args.config_yml, 'wt', encoding='utf-8') as f:
            f.write(config_yml_txt)
        sys.exit(0)

    with open(args.config_yml) as f:
        # yaml.BaseLoader loads everything as string
        # yaml.FullLoader interprets as int, etc
        config = yaml.load(f, Loader=yaml.BaseLoader)

    # Check and update directory paths
    list_sources = []
    for directory in config['sources']:
        list_sources.append(check_directory(directory))
    config['sources'] = list_sources
    config['output'] = check_directory(config['output'], warn=False)

    # Check and update page source file paths
    config['pages_folder'] = check_directory(config['pages_folder'])
    list_pages = []
    for page_filename in config['pages_order']:
        page_filepath = os.path.join(config['pages_folder'], page_filename)
        list_pages.append(check_file(page_filepath))

    # Check logo and favicon if present
    if 'logo' in config:
        config['logo'] = check_file(config['logo'])
    if 'favicon' in config:
        config['favicon'] = check_file(config['favicon'])

    # Clean up and check the URL
    config['base_url'] = config['base_url'].strip('/')
    check_url(config['base_url'])

    # Determine page title postfix
    config['page_title_postfix'] = ''
    if 'site_name' in config:
        config['page_title_postfix'] = f" | {config['site_name']}"

    return config, args.preserve_output


def check_url(url):
    """
    Return True if the URL is valid.
    """
    result_ok = False
    try:
        result = urllib.parse.urlparse(url)
        result_ok = all([result.scheme, result.netloc])
    except ValueError:
        result_ok = False

    if not result_ok:
        print(f'WARN: {url} is NOT valid')

    return result_ok


def check_directory(path, warn=True):
    """Check directory and update to a useable path"""
    if path.startswith('~/'):
        path = path.replace('~', os.path.expanduser('~'))
    if warn and not os.path.exists(path):
        print(f'ERROR: Folder not found: {path}')
        sys.exit(1)
    return path


def check_file(path, warn=True):
    """Check file and update to a useable path"""
    if path.startswith('~/'):
        path = path.replace('~', os.path.expanduser('~'))
    if warn and not os.path.isfile(path):
        print(f'ERROR: File not found: {path}')
        sys.exit(1)
    return path


def package_data_file(filepath):
    """Get file relative to package."""
    # https://stackoverflow.com/a/1219406
    filepath = os.path.join(os.path.split(__file__)[0], filepath)
    return filepath


def read_package_data_files():
    """Read package data files and return the text."""
    with open(package_data_file(DATA_HTML_BASE),
                'rt', encoding='utf-8') as f:
        base_html = f.read()

    with open(package_data_file(DATA_HTML_LICENSE),
                'rt', encoding='utf-8') as f:
        license_html = f.read()

    with open(package_data_file(DATA_CSS_STYLE),
                'rt', encoding='utf-8') as f:
        style_css = f.read()

    return base_html, license_html, style_css


def remove_directory_contents(path_to_folder):
    """Remove contents of directory without deleting the directory."""
    for root, dirs, files in os.walk(path_to_folder):
        for f in files:
            os.remove(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))


def generate_style_css(config, style_css):
    """Generate style.css in output folder."""
    outpath = os.path.join(config['output'], 'css')
    if not os.path.exists(outpath):
        os.mkdir(outpath)
    outfile = os.path.join(config['output'], DATA_CSS_STYLE)
    with open(outfile, 'wt', encoding='utf-8') as f:
        f.write(style_css)


def generate_base_html(config, base_html, license_html):
    """Generate the base HTML template."""
    KEYS_TO_REPLACE = ['author', 'base_url', 'copyright_year']
    if 'copyright_year' not in config:
        config['copyright_year'] = str(datetime.now().year)
    for k in KEYS_TO_REPLACE:
        tag = '{{' + k + '}}'
        s = config[k]
        if k=='base_url':
            s += '/'
        base_html = base_html.replace(tag, s)

    base_html = base_html.replace('{{license}}', license_html)

    outpath = os.path.join(config['output'], 'site_images')
    if not os.path.exists(outpath):
        os.mkdir(outpath)

    if 'favicon' not in config:
        base_html = base_html.replace('{{favicon}}', '')
    else:
        faviconfile = '/site_images/' + os.path.basename(config['favicon'])
        s = f'<link rel="icon" href="{faviconfile}">'
        base_html = base_html.replace('{{favicon}}', s)
        dstfile = os.path.join(outpath, os.path.basename(config['favicon']))
        shutil.copyfile(config['favicon'], dstfile)

    if 'logo' not in config:
        base_html = base_html.replace('{{logo}}', '')
    else:
        logofile = '/site_images/' + os.path.basename(config['logo'])
        s = f'<div class="logo"><img src="{logofile}" alt="logo"></div>'
        base_html = base_html.replace('{{logo}}', s)
        dstfile = os.path.join(outpath, os.path.basename(config['logo']))
        shutil.copyfile(config['logo'], dstfile)

    return base_html


def markdown_to_html(filepath):
    """Convert markdown to HTML."""
    with open(filepath, 'rt', encoding='utf-8') as f:
        txt = f.read()

    # Separate metadata from markdown text
    loc = txt.find('---', 3)  # Find 2nd occurrence of "---"
    if loc < 0:
        print(f'ERROR: Cannot find metadata in {filepath}')
        sys.exit(1)

    meta_txt = txt[:loc]
    md_txt = txt[loc+3:]  # skip over 2nd occurrence of "---"

    # Extract metadata
    meta = yaml.load(meta_txt, Loader=yaml.BaseLoader)

    # Add title to markdown
    md_txt = f'# {meta["title"]}\n---\n' + md_txt

    # Convert markdown to html
    html = mistune.html(md_txt)

    return html, meta


def get_title_slug(meta, filepath):
    """Create a slug from the title."""
    bad_title = True
    if 'title' in meta:
        bad_title = False
        if len(meta['title']) < 1:
            bad_title = True

    if bad_title:
        print(f'ERROR: bad title metadata in {filepath}')
        sys.exit(1)

    slug = slugify.slugify(meta['title'], stopwords=['the', 'a'])
    return slug


def generate_navbar_html(title2slug, current_slug=None):
    """Generate the navigation bar."""
    # template for each menu line item
    MENU_LINE = '<li><a class="active" class="right" ' \
                'href="[HREF]">[VISIBLE]</a></li>'

    count = 0
    navbar_html = ''
    for title, slug in title2slug.items():
        count += 1
        s = f'      {MENU_LINE}\n'
        s = s.replace('[VISIBLE]', title)
        s = s.replace('[HREF]', slug)
        if slug != current_slug:
            s = s.replace(' class="active"', '')
        if count < len(title2slug):
            s = s.replace(' class="right"', '')
        navbar_html += s

    navbar_html = navbar_html.strip()
    return navbar_html


def generate_pages(config, base_html):
    """Generate pages in output folder."""
    # Copy files except page source .md files to output
    output_pages = os.path.join(config['output'], 'pages')
    shutil.copytree(
            config['pages_folder'],
            output_pages,
            dirs_exist_ok=True)

    # Create HTML content for each page
    dct_html = OrderedDict()
    title2slug = OrderedDict()
    for page_file in config['pages_order']:
        filepath = os.path.join(config['output'], page_file)
        page_file = os.path.basename(filepath)

        # Generate html and update fields
        html, meta = markdown_to_html(filepath)
        if page_file == 'index.md':
            html = base_html
        else:
            html = base_html.replace('{{content}}', html)
        s = f'{meta["title"]}' + config['page_title_postfix']
        html = html.replace('{{page_title}}', s)

        # Remove source markdown from output
        os.remove(filepath)

        # Update canonical link, slug provides root-relative URL
        page_file_html = os.path.splitext(page_file)[0] + '.html'
        meta['slug'] = '/'
        if page_file != 'index.md':
            meta['slug'] += page_file_html
        meta['canonical'] = config['base_url'] + meta['slug']
        html = html.replace('{{canonical}}', meta['canonical'])

        meta['outfile'] = os.path.join(config['output'], page_file_html)
        meta['html'] = html
        meta['page'] = True
        dct_html[meta['slug']] = meta
        title2slug[meta["title"]] = meta['slug']

    # Create unique navigation bar for each page
    for current_slug in dct_html:
        navbar_html = generate_navbar_html(title2slug, current_slug=current_slug)
        html = dct_html[current_slug]['html'].replace('{{nav_line_items}}', navbar_html)
        dct_html[current_slug]['html'] = html

    # Write to output HTML files
    for _, meta in dct_html.items():
        with open(meta['outfile'], 'wt', encoding='utf-8') as f:
            f.write(meta['html'])

    return dct_html, title2slug


def generate_articles(config, dct_html, base_html):
    """Copy articles to output folder as HTML."""
    skip_page_files = []
    for page_file in config['pages']:
        skip_page_files.append(os.path.join(config['articles'], page_file))

    glob_path = os.path.join(config['articles'], '**/*')
    for filepath in glob.glob(glob_path, recursive=True):
        if not filepath.endswith(MARKDOWN_EXTENSIONS) or filepath in skip_page_files:
            continue

        # Generate html and update fields
        html, meta = markdown_to_html(filepath)
        html = base_html.replace('{{content}}', html)
        s = f'{meta["title"]}' + config['page_title_postfix']
        html = html.replace('{{page_title}}', s)

        # Update canonical link, slug provides root-relative URL
        meta['slug'] = '/' + get_title_slug(meta, filepath) + '/'
        if 'canonical' not in meta:
            meta['canonical'] = config['base_url'] + meta['slug']
        html = html.replace('{{canonical}}', meta['canonical'])

        # Write HTML to file
        dst_folder = os.path.join(config['output'], meta['slug'].strip('/'))
        outfile = os.path.join(dst_folder, 'index.html')
        if not os.path.isdir(dst_folder):
            os.mkdir(dst_folder)

        with open(outfile, 'wt', encoding='utf-8') as f:
            f.write(html)
        meta['outfile'] = outfile
        meta['html'] = html
        meta['page'] = False
        dct_html[meta['slug']] = meta

        # Copy other non-markdown files in article folder
        article_path, _ = os.path.split(filepath)
        for src_file in glob.glob(os.path.join(article_path, '*')):
            if not os.path.isfile(src_file):
                continue
            if src_file.endswith(MARKDOWN_EXTENSIONS):
                continue
            dst_file = os.path.join(dst_folder, os.path.basename(src_file))
            shutil.copyfile(src_file, dst_file)

    return dct_html


def get_categories(dct_html):
    """Generate the index page with links to articles."""
    dct = OrderedDict()
    for slug, meta in dct_html.items():
        if meta['page']:
            continue
        if 'category' in meta:
            if meta['category'] not in dct:
                dct[meta['category']] = []
            d = OrderedDict()
            d['title'] = meta['title']
            d['href'] = meta['slug']
            dct[meta['category']].append(d.copy())

    return dct


def generate_index_html(dct_html):
    """Generate the index.html given the categorized information."""
    dct_categories = get_categories(dct_html)

    html = ''
    for category, list_articles in dct_categories.items():
        html += f'<h2>{category.title()}</h2>\n'
        html += '<ul class="categorized-articles">\n'
        for d in list_articles:
            s = '<a href="[HREF]">[TITLE]</a>'
            # s = s.replace('[HREF]', d['href'] + '/index.html')
            s = s.replace('[HREF]', d['href'])
            s = s.replace('[TITLE]', d['title'])
            html += f'<li>{s}</li>\n'
        html += '</ul>\n'

    dct_html['/']['html'] = dct_html['/']['html'].replace('{{content}}', html)

    with open(dct_html['/']['outfile'], 'wt', encoding='utf-8') as f:
        f.write(dct_html['/']['html'])

    return dct_categories


def main():
    config, preserve_output = get_user_inputs()

    # Regenerate output folder
    if not preserve_output:
        remove_directory_contents(config['output'])

    base_html, license_html, style_css = read_package_data_files()
    base_html = generate_base_html(config, base_html, license_html)
    generate_style_css(config, style_css)

    # Generate page HTML files
    dct_html, title2slug = generate_pages(config, base_html)

    # Update base_html with navigation bar
    navbar_html = generate_navbar_html(title2slug)
    base_html = base_html.replace('{{nav_line_items}}', navbar_html)

    #TODO: continue work from here

    # Generate article HTML files
    dct_html = generate_articles(config, dct_html, base_html)

    # Generate the Home page content (index.html)
    dct_categories = generate_index_html(dct_html)

    print('Done.')


if __name__ == "__main__":
    main()
