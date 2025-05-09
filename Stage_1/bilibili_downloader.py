

import subprocess
import os
import glob
import logging
import shlex
import re
import argparse

parser = argparse.ArgumentParser(description="Download videos from Bilibili")
parser.add_argument('--bvid', type=str, help='Path to the CSV file containing video URLs')
parser.add_argument('--output', type=str, help='Output directory for downloaded videos')
parser.add_argument('--resolution', type=str, default='1080P', help='Resolution for the video download')
args = parser.parse_args()

SESSDATA = "Put Your SESSDATA of Bilibili here"

video_output_dir = args.output

logging.basicConfig(format='%(asctime)s -  %(levelname)s: %(message)s',
                    level=logging.DEBUG,
                    filename='download.log',
                    filemode='a')
logger = logging.getLogger('download')

warning_confirm = input("Warning: This code is for scientific research only, please do not use this tool to vandalize other people's video copyrights. Do you accept the terms? (y/n): ")

if warning_confirm.lower() != 'y':
    print("You must accept the terms to proceed.")
    exit(1)


url = f"https://www.bilibili.com/video/{video['bvid']}"
title = args.bvid

try:
    subprocess.run(['bilix', 'v', url, '--cookie', SESSDATA, '-q', args.resolution],check=True)

    # Remane video
    video_files = sorted(glob.glob(os.path.join(video_output_dir, '*')),key=os.path.getmtime,reverse=True)
    if video_files:
        downloaded_file = video_files[0]
        file_title = os.path.splitext(downloaded_file)[0]
        if file_title[9:] != title:
            logger.error(f"Title not matching: {idx}, {url}, {file_title}, {title}")
            subprocess.run(
                    ["find", video_output_dir, "-type", "f", "-name", f"{title}*", "-exec", "rm", "-f", "{}", "+"],
                    check=True
                )
        else:
                file_extension = os.path.splitext(downloaded_file)[1]
                new_name = os.path.join(video_output_dir, f"{idx_aid_bvid}{file_extension}")
                os.rename(downloaded_file, new_name)
    else:
        logger.error(f"Video not found: {idx}, {url}")

except Exception as e:
    logger.error(f"{idx}, {url}, {e}")