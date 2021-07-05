#!/usr/bin/env python3
# Standard libraries
import os
import random
import shutil

# Installed packages
import lorem
from PIL import Image, ImageDraw, ImageFont
import slugify

BASE_FOLDER = '~/Documents/exampledata'
BASE_FOLDER = BASE_FOLDER.replace('~', os.path.expanduser('~'))

# For 1st set of data
RANDOM_SEED_1 = 1
FIRST_ARTICLE_1 = 0
NUM_ARTICLES_1 = 101
CONTENT_FOLDER_1 = os.path.join(BASE_FOLDER, 'content1')

# For 2nd set of data
RANDOM_SEED_2 = 99
FIRST_ARTICLE_2 = 200
NUM_ARTICLES_2 = 39
CONTENT_FOLDER_2 = os.path.join(BASE_FOLDER, 'content2')

# Don't edit below this

HEAD = '''
---
title: {{TITLE}}
category: {{CATEGORY}}
tags: blogging, artblog, static site generation
summary: {{SUMMARY}}
image: {{FILENAME}}
---

'''.lstrip()

MD_IMG_INSERT = '''
![]({{FILENAME}})

'''.lstrip()


def get_complementary_color(color):
    """Given RGB color tuple, return complementary color tuple."""
    red = 255 - color[0]
    green = 255 - color[1]
    blue = 255 - color[2]
    return (red, green, blue)


def gen_image(filepath, rgb_color, width_height_pixels=(640,400)):
    """Generate color block with filename as text inside the color block."""
    # Generate rectangular color block
    img = Image.new('RGB', width_height_pixels, color=rgb_color)
    d = ImageDraw.Draw(img)

    # Insert filename text of complementary color inside the color block
    filename = os.path.basename(filepath)
    font = ImageFont.truetype("arial.ttf", 60)
    complementary_color = get_complementary_color(rgb_color)
    d.text((10,10), filename, font=font, fill=complementary_color)

    # Save file
    img.save(filepath)


def generate_data(random_seed, content_folder, first_article, num_articles):
    # Fix the seed so that the random data is reproducible
    random.seed(random_seed)

    # Create content folder
    shutil.rmtree(content_folder, ignore_errors=True)
    os.makedirs(content_folder)

    # Create articles
    for n in range(first_article, first_article + num_articles):
        # Create folder
        folder = os.path.join(content_folder, 'article%04d' % n)
        os.mkdir(folder)

        # Generate image for article
        rgb_color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        width = random.randint(400, 1600)
        height = random.randint(400, 1600)
        imgfilename = f'image{n}.jpg'
        imgfilepath = os.path.join(folder, imgfilename)
        gen_image(imgfilepath, rgb_color, width_height_pixels=(width, height))

        # Generate text for article
        title = lorem.get_sentence(count=1, sep=' ', comma=(0, 2), word_range=(2, 8))
        txt = HEAD.replace('{{TITLE}}', title)

        summary = lorem.get_sentence(count=1, sep=' ', comma=(0, 2), word_range=(9, 20))
        txt = txt.replace('{{SUMMARY}}', summary)

        txt = txt.replace('{{CATEGORY}}', f'Category {rgb_color[0] % 4}')

        txt = txt.replace('{{FILENAME}}', imgfilename)

        txt += MD_IMG_INSERT.replace('{{FILENAME}}', imgfilename)
        txt += summary + '\n\n'

        txt += lorem.get_paragraph(
                count=random.randint(1,20),
                sep=os.linesep,
                comma=(0, 2),
                word_range=(4, 8),
                sentence_range=(5, 10))

        # Write to markdown file
        mdfilename = slugify.slugify(title, stopwords=['the', 'a']) + '.md'
        mdfilepath = os.path.join(folder, mdfilename)
        with open(mdfilepath, 'wt', encoding='utf-8') as f:
            f.write(txt)

    print(f'{num_articles} generated in {content_folder}')

def main():
    generate_data(RANDOM_SEED_1, CONTENT_FOLDER_1, FIRST_ARTICLE_1, NUM_ARTICLES_1)
    generate_data(RANDOM_SEED_2, CONTENT_FOLDER_2, FIRST_ARTICLE_2, NUM_ARTICLES_2)

    shutil.copytree('favicon', os.path.join(BASE_FOLDER, 'favicon'), dirs_exist_ok=True)
    shutil.copytree('logo', os.path.join(BASE_FOLDER, 'logo'), dirs_exist_ok=True)
    shutil.copytree('pages', os.path.join(BASE_FOLDER, 'pages'), dirs_exist_ok=True)

if __name__ == "__main__":
    main()
