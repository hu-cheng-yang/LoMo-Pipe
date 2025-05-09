import os
import sys
from tqdm import tqdm
import time
import re
from hf_hub_ctranslate2 import MultiLingualTranslatorCT2fromHfHub
from transformers import AutoTokenizer
import argparse
import logging


def translate(model, sub_path, sub_path_en):
    f_read = open(sub_path, 'r')
    sub_name = sub_path.split('/')[-1]
    batchsize = 8
    lines = []
    timestamps = []

    with open(f'{sub_path_en}/{sub_name}', 'w') as f:
            for line in f_read.read().splitlines():
                if len(lines) < batchsize:
                    timestamp = re.search(r'\[\d+(\.\d+)?\/\d+(\.\d+)?\]', line)
                    timestamp = timestamp.group() if timestamp else ""
                    if timestamp == "":
                        continue
                    line = line.replace(timestamp, '').strip()
                    lines.append(line)
                    timestamps.append(timestamp)
                    continue
                outputs = model.generate(lines, src_lang=["zh" for i in range(len(lines))], tgt_lang=["en" for i in range(len(lines))])
                for line, timestamp in zip(outputs, timestamps):
                    f.write(line + " " + timestamp + '\n')
                lines = []
                timestamps = []
            if len(lines) > 0:
                outputs = model.generate(lines, src_lang=["zh" for i in range(len(lines))], tgt_lang=["en" for i in range(len(lines))])
                for line, timestamp in zip(outputs, timestamps):
                    f.write(line + " " + timestamp + '\n')
    f_read.close()

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Translate Chinese subtitles to English")
    parser.add_argument("--input_folder", type=str, required=True, help="Path to the folder containing Chinese subtitles")
    parser.add_argument("--output_folder", type=str, required=True, help="Path to the folder to save English subtitles")

    args = parser.parse_args()

    mt = MultiLingualTranslatorCT2fromHfHub(
        model_name_or_path="michaelfeil/ct2fast-m2m100_1.2B", device="cuda", compute_type="int8_float16",
        tokenizer=AutoTokenizer.from_pretrained(f"facebook/m2m100_1.2B")
    )



    all_files = set(os.listdir(args.input_folder))

    process_bar = tqdm(all_files, desc="Processing subs", unit="sub")
    for file_name in process_bar:
        process_bar.set_description(f"Processing {file_name}")
        file_path = os.path.join(args.input_folder, file_name)
        translate(mt, file_path, args.output_folder)