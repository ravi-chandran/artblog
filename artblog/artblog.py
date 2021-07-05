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
import yaml

CMDLINE_APP_NAME = 'ArtBlog - a static site generator'

DATA_HTML_BASE = os.path.join('html', 'base.html')
DATA_HTML_LICENSE = os.path.join('html', 'license.html')
DATA_CSS_STYLE = os.path.join('css', 'style.css')
CONFIG_TEMPLATE = os.path.join('config', 'config.yml')

MARKDOWN_EXTENSIONS = ('.md')

LOGO_LINK = '''
<div class="logo">
    <a href="/">
        <img src="[LOGOFILE]" alt="logo" class="logo-image">
    </a>
</div>
'''.lstrip()

POST_LINK = '''
<div class="row-post">
  <div class="column-image">
    <a href="[HREF]"><img src="[IMAGE]" alt="image" class="post-image"></a>
  </div>
  <div class="column-text">
    <h3 class="post-title"><a href="[HREF]">[TITLE]</a></h3>
    <p class="post-summary">[SUMMARY]</p>
  </div>
</div>

'''.lstrip()

ROBOTS_TXT = '''
User-agent: *
Host: {{base_url}}
Disallow: /cgi-bin/
Disallow: /tmp/
'''.lstrip()

PROPERTY = '''
  <meta property="og:site_name" content="{{base_url}}">
  <meta property="og:title" content="{{page_title}}">
  <meta property="og:url" content="{{canonical}}">
  <meta property="og:description" content="{{title}}">
  <meta property="og:type" content="article">
  <meta property="article:tag" content="{{category}}">
'''.lstrip()

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
    list_post_sources = []
    for directory in config['sources']:
        list_post_sources.append(check_directory(directory))
    config['sources'] = list_post_sources
    config['output'] = check_directory(config['output'], warn=False)

    # Check mainpage folder
    config['mainpage_folder'] = check_directory(config['mainpage_folder'])
    index_md_file = os.path.join(config['mainpage_folder'], 'index.md')
    check_file(index_md_file)

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
        s = LOGO_LINK.replace('[LOGOFILE]', logofile)
        #s = s.replace('[HREF]', config['base_url'])
        #s = f'<div class="logo"><img src="{logofile}" alt="logo"></div>'
        base_html = base_html.replace('{{logo}}', s)
        dstfile = os.path.join(outpath, os.path.basename(config['logo']))
        shutil.copyfile(config['logo'], dstfile)

    return base_html


def markdown_to_html(filepath, metadata=True):
    """Convert markdown to HTML."""
    with open(filepath, 'rt', encoding='utf-8') as f:
        txt = f.read()

    meta = None
    if metadata:
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
    else:
        md_txt = txt

    # Convert markdown to html
    html = mistune.html(md_txt)

    return html, meta


def generate_menu_folders(config):
    """Generate folders to hold menu html pages."""
    menu_folder = os.path.join(config['output'], 'menu')
    os.mkdir(menu_folder)

    if 'Other' not in config['menu']:
        config['menu'].append('Other')

    cat2slug = OrderedDict()
    for category in config['menu']:
        s = category.strip().lower().replace(' ','')
        folder = os.path.join(menu_folder, s)
        os.mkdir(folder)
        cat2slug[category] = f'menu/{s}/'

    return cat2slug


def generate_navbar_html(cat2slug, active_category=None):
    """Generate the navigation bar."""
    # Template for each menu line item
    MENU_LINE = '<li><a class="active" ' \
                'href="[HREF]">[VISIBLE]</a></li>'

    navbar_html = ''
    for category, slug in cat2slug.items():
        s = f'      {MENU_LINE}\n'
        s = s.replace('[VISIBLE]', category)
        s = s.replace('[HREF]', '/' + slug)
        if category != active_category:
            s = s.replace(' class="active"', '')
        navbar_html += s

    navbar_html = navbar_html.strip()
    return navbar_html


def generate_mainpage(config, base_html, cat2slug):
    """Generate main landing page of blog in output folder."""
    shutil.copytree(
            config['mainpage_folder'],
            config['output'],
            dirs_exist_ok=True)

    # Update base_html with navigation bar
    navbar_html = generate_navbar_html(cat2slug)
    base_html = base_html.replace('{{nav_line_items}}', navbar_html)

    # Generate html and update fields
    filepath = os.path.join(config['output'], 'index.md')
    html, _ = markdown_to_html(filepath, metadata=False)
    os.remove(filepath)  # Remove source markdown from output
    html = base_html.replace('{{content}}', html)
    s = 'Main' + config['page_title_postfix']
    html = html.replace('{{page_title}}', s)
    html = html.replace('{{property}}', '')

    # Update canonical link, slug provides root-relative URL
    mainpage_html = os.path.splitext(filepath)[0] + '.html'
    slug = '/'
    canonical = config['base_url'] + slug
    html = html.replace('{{canonical}}', canonical)

    # Write to output HTML files
    with open(mainpage_html, 'wt', encoding='utf-8') as f:
        f.write(html)


def generate_posts(config, base_html, cat2slug):
    """Copy posts to output folder as HTML."""
    # Copy post .md files to output
    output_posts = os.path.join(config['output'], 'posts')
    for posts_folder in config['sources']:
        shutil.copytree(
                posts_folder,
                output_posts,
                dirs_exist_ok=True)

    dct_html = OrderedDict()

    glob_path = os.path.join(output_posts, '**/*')
    for filepath in glob.glob(glob_path, recursive=True):
        if not filepath.endswith(MARKDOWN_EXTENSIONS):
            continue

        # Generate html and update fields
        html, meta = markdown_to_html(filepath)
        os.remove(filepath)  # Delete post .md file
        html = base_html.replace('{{content}}', html)
        html = html.replace('{{property}}', PROPERTY)
        s = meta["title"] + config['page_title_postfix']
        html = html.replace('{{page_title}}', s)

        # Update canonical link, slug provides root-relative URL
        post_folder = os.path.split(filepath)[0]
        post_folder = os.path.split(post_folder)[1]
        meta['slug'] = 'posts/' + post_folder + '/'
        if 'canonical' not in meta:
            meta['canonical'] = config['base_url'] + '/' + meta['slug']
        html = html.replace('{{canonical}}', meta['canonical'])

        # Generate navigation bar with category highlighted
        navbar_html = generate_navbar_html(
            cat2slug, active_category=meta['category'])
        html = html.replace('{{nav_line_items}}', navbar_html)

        # Add remaining property info
        html = html.replace('{{base_url}}', config['base_url'])
        html = html.replace('{{title}}', meta["title"])
        html = html.replace('{{category}}', meta["category"])
        

        # Write HTML to file
        dst_folder = os.path.join(config['output'], meta['slug'].strip('/'))
        outfile = os.path.join(dst_folder, 'index.html')
        if not os.path.isdir(dst_folder):
            os.mkdir(dst_folder)

        with open(outfile, 'wt', encoding='utf-8') as f:
            f.write(html)
        meta['outfile'] = outfile
        # meta['html'] = html  # debug only
        meta['page'] = False
        dct_html[meta['slug']] = meta

    return dct_html


def generate_category_pages(config, base_html, dct_html, cat2slug):
    """Generate html pages for each category."""
    # Prepare html content (list of posts) for each category
    content = OrderedDict()
    for category in cat2slug:
        content[category] = f'<h2>{category.title()}</h2>\n'

    # Find posts for current category
    for slug, meta in dct_html.items():
        s = POST_LINK
        s = s.replace('[HREF]', '/' + meta['slug'])
        s = s.replace('[TITLE]', meta['title'])
        if 'summary' in meta:
            s = s.replace('[SUMMARY]', meta['summary'])
        else:
            s = s.replace('[SUMMARY]', '')

        if 'image' in meta:
            s = s.replace('[IMAGE]', '/' + meta['slug'] + meta['image'])
        else:
            s = s.replace('[IMAGE]', '')

        category = None
        if 'category' in meta:
            category = meta['category']

        if category in content:
            content[category] += s
        else:
            content['Other'] += s

    # Create HTML content for each page
    for category, slug in cat2slug.items():
        # Generate navigation bar with category highlighted
        navbar_html = generate_navbar_html(cat2slug, active_category=category)
        html = base_html.replace('{{nav_line_items}}', navbar_html)

        # Update content with list of posts
        html = html.replace('{{content}}', content[category])

        s = f'{meta["title"]}' + config['page_title_postfix']
        html = html.replace('{{page_title}}', s)

        # Update canonical link, slug provides root-relative URL
        html = html.replace('{{canonical}}', slug)

        html = html.replace('{{property}}', '')

        # Write to output HTML files
        filepath = os.path.join(config['output'], slug, 'index.html')
        with open(filepath, 'wt', encoding='utf-8') as f:
            f.write(html)


def generate_robots_txt(config):
    """Create an empty robots.txt file."""
    filepath = os.path.join(config['output'], 'robots.txt')
    s = ROBOTS_TXT.replace('{{base_url}}', config['base_url'])
    with open(filepath, 'wt') as f:
        f.write(s)


def main():
    config, preserve_output = get_user_inputs()

    # Regenerate output folder
    if not preserve_output:
        remove_directory_contents(config['output'])

    # Prepare html templates
    base_html, license_html, style_css = read_package_data_files()
    base_html = generate_base_html(config, base_html, license_html)
    generate_style_css(config, style_css)

    cat2slug = generate_menu_folders(config)
    generate_mainpage(config, base_html, cat2slug)
    dct_html = generate_posts(config, base_html, cat2slug)

    generate_category_pages(config, base_html, dct_html, cat2slug)

    generate_robots_txt(config)

    print(f'Site generated at: {config["output"]}')


if __name__ == "__main__":
    main()
