import os
import json
import glob
import csv
from tqdm import tqdm
import random
import re

import argparse

example = """
```   
* CONCLUSION: [The video transcript describes a horror movie titled "Crying Cup," which focuses on a virus outbreak in Taiwan and its violent consequences.]
* QUESTION: [What key visual element appears on the balcony in the horror movie "Crying Cup"?]
* ANSWER: [A strange monkey with a bloody chest.]
* WRONG_1: [A beautiful butterfly with colorful wings.]
* WRONG_2: [A group of smiling children playing.]
* WRONG_3: [A peaceful landscape with trees.]
```  
"""

parser = argparse.ArgumentParser(description="Generate quiz from English subtitles")
parser.add_argument("--input_folder", type=str, required=True, help="Path to the folder containing English subtitles")
parser.add_argument("--output_folder", type=str, required=True, help="Path to the folder to save quiz")
parser.add_argument("--meta_file", type=str, required=True, help="Path to the metadata file")
args = parser.parse_args()


def find_closest_matches(text, t1, t2):
    # 转义特殊字符并构建正则表达式
    pattern = re.compile(f"{re.escape(t1)}(.*?){re.escape(t2)}", re.DOTALL)
    return pattern.findall(text)

with open(args.meta_file, "r") as f:
    reader = csv.reader(f)
    data = list(reader)[1:]
    
name_dict = {}
for i in data:
    name_dict[i[0]] = dict(duration=float(i[1]), resolution=i[2])
    

subtitles = glob.glob(f"{args.input_folder}/*.txt")


QAs = []

for subs in tqdm(subtitles):
    with open(subs, "r") as text_file:
        captions = text_file.read()
        
    try:
        CONCLUSION = find_closest_matches(captions, "CONCLUSION:", "\n")[0].replace("[", "").replace("]", "").strip()
        QUESTION = find_closest_matches(captions, "QUESTION:", "\n")[0].replace("[", "").replace("]", "").strip()
        ANSWER = find_closest_matches(captions, "ANSWER:", "\n")[0].replace("[", "").replace("]", "").strip()
        WRONG_1 = find_closest_matches(captions, "WRONG_1:", "\n")[0].replace("[", "").replace("]", "").strip()
        WRONG_2 = find_closest_matches(captions, "WRONG_2:", "\n")[0].replace("[", "").replace("]", "").strip()
        WRONG_3 = find_closest_matches(captions, "WRONG_3:", "\n")[0].replace("[", "").replace("]", "").strip()
    except Exception as e:
        print(f"Error processing file {subs}: {e}")
        continue
    
    video_id = os.path.basename(subs).replace(".txt", ".mp4")
    
    duration = name_dict[video_id]["duration"]
    
    question = QUESTION
    vauge_question = QUESTION
    
    qa = {
        "video_id": video_id,
        "duration": duration,
        "resolution": name_dict[video_id]["resolution"],
        "questions": []
    }
    
    choice = ["A", "B", "C", "D"]
    random.shuffle(choice)
    
    correct = choice[0]
    
    answers = [choice[0] + ": " + ANSWER,
               choice[1] + ": " + WRONG_1,
               choice[2] + ": " + WRONG_2,
               choice[3] + ": " + WRONG_3]
    
    answers = sorted(answers, key=lambda x: x[0])
    
    qa["questions"].append({
        "question_id": video_id.replace(".mp4", "") + "_01",
        "question": question,
        "options": answers,
        "answer": correct,
    })
    
    QAs.append(qa)
    
    
    
with open(os.path.join(args.output_folder, "GVQA.json"), "w") as json_f:
    json.dump(QAs, json_f, indent=4)
    
print(f"Total QAs: {len(QAs)}")