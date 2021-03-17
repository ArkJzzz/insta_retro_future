#!/usr/bin/python3
__author__ = 'ArkJzzz (arkjzzz@gmail.com)'

# Import
import logging
import os
import random
import glob
import time

from dotenv import load_dotenv
from instabot import Bot
from PIL import Image
from PIL import ImageDraw


# Init
logger = logging.getLogger('insta_retro_future')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_FOLDER = 'images'
USED_FILES_FOLDER = 'used_images'
POSTED_IMAGES = 'posted_images.txt'

BACKGROUND_DIMENTIONS = (600, 600)
BACKGROUND_COLOR = '#1C1C1C'
IMG_MAIN_SIZE = 560

TIMEOUT = 48 * 60 * 60  # pics will be posted every 48 hours



# Funtions

def get_list_files(folder):
    files_from_folder = []
    for root, dirs, files in os.walk(folder):
        for filename in files:
            filename = os.path.join(root, filename)
            files_from_folder.append(filename)

    return files_from_folder


def move_file(file_path, destination):
    try:
        os.mkdir(destination)
    except FileExistsError:
        logger.info('the directory already exists')

    path, filename = os.path.split(file_path)
    os.rename(
        src=file_path,
        dst=os.path.join(destination, filename),
    )


def get_offset(width, height):
    background_width, background_height = BACKGROUND_DIMENTIONS
    offset_x = int((background_height - height) / 2)
    offset_y = int((background_width - width) / 2)

    return offset_y, offset_x


def get_new_size(width, height):
    current_ratio = width / height
    if current_ratio <= 1:
        new_height = IMG_MAIN_SIZE
        new_width  = int(new_height * width / height)
    else:
        new_width = IMG_MAIN_SIZE
        new_height  = int(new_width * height / width)

    return new_width, new_height


def prepare_img_to_post(filename):
    background = Image.new('RGB', BACKGROUND_DIMENTIONS, BACKGROUND_COLOR)
    idraw = ImageDraw.Draw(background)
    
    img = Image.open(filename)
    width, height = img.size
    new_size = get_new_size(width, height)
    new_width, new_height = new_size
    offset = get_offset(new_width, new_height)
    img = img.resize(new_size, Image.ANTIALIAS)

    background.paste(img, offset)
    background.save(filename)


    return filename


def get_posted_img_list():
    posted_img_list = []
    try:
        with open(POSTED_IMAGES, 'r', encoding='utf8') as f:
            posted_img_list = f.read().splitlines()
    except Exception:
        posted_img_list = []

    return posted_img_list



def main():
    # init
    formatter = logging.Formatter(
            fmt='%(asctime)s %(name)s:%(lineno)d - %(message)s',
            datefmt='%Y-%b-%d %H:%M:%S (%Z)',
            style='%',
        )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(f'{__file__}.log')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)

    load_dotenv()

    bot = Bot()
    bot.login(
        username=os.getenv("INSTA_LOGIN"), 
        password=os.getenv("INSTA_PASSWORD"), 
    )

    img_dir = os.path.join(BASE_DIR, IMAGES_FOLDER)
    posted_img_list = get_posted_img_list()
    logger.debug(posted_img_list)

    while True:
        pics = glob.glob(img_dir + "/*.jpg")
        pics = sorted(pics)
        try:
            for pic in pics:
                logger.debug(pic)
                if pic in posted_img_list:
                    continue

                prerared_img = prepare_img_to_post(pic)
                logger.debug(f'prerared_img: {prerared_img}')

                bot.upload_photo(prerared_img)
                
                if bot.api.last_response.status_code != 200:
                    logger.error(bot.api.last_response)
                    break

                if prerared_img not in posted_img_list:
                    posted_img_list.append(prerared_img)
                    with open(POSTED_IMAGES, "a", encoding="utf8") as f:
                        f.write(prerared_img + "\n")

                time.sleep(TIMEOUT)

        except Exception as e:
            logger.error(str(e))
        
        time.sleep(60)


if __name__ == '__main__':
    main()
