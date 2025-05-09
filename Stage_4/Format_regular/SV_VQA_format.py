import os
import json

import glob
import csv
from tqdm import tqdm

import random

import re
import argparse
import logging

parser = argparse.ArgumentParser(description="Generate quiz from English subtitles")
parser.add_argument("--input_folder", type=str, required=True, help="Path to the folder containing English subtitles")
parser.add_argument("--output_folder", type=str, required=True, help="Path to the folder to save quiz")
parser.add_argument("--meta_file", type=str, required=True, help="Path to the metadata file")
args = parser.parse_args()

example = """
```  
* SUBTITLE: A droplet falls into a still pond, creating concentric ripples [8.4/9.6]  
* START: 8.4  
* END: 9.6  
* CONCLUSION: A water droplet impacts a calm pond surface and generates circular wave patterns.  
* QUESTION: What visual phenomenon directly results from the droplet entering the water?  
* ANSWER: Formation of concentric ripple waves  
* WRONG_1: Sudden freezing of the pond surface  
* WRONG_2: Vertical water spout eruption  
* WRONG_3: Disappearance of all surface waves  
```  
"""


def find_closest_matches(text, t1, t2):
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
Vague_QAs = []

for subs in subtitles:
    
    with open(subs, "r") as text_file:
        captions = text_file.read()
        
    try:
        SUBTITLE = find_closest_matches(captions, "SUBTITLE:", "\n")[0].strip()
        START = find_closest_matches(captions, "START:", "\n")[0].strip()
        END = find_closest_matches(captions, "END:", "\n")[0].strip()
        START = float(START)
        END = float(END)
        CONCLUSION = find_closest_matches(captions, "CONCLUSION:", "\n")[0].strip()
        QUESTION = find_closest_matches(captions, "QUESTION:", "\n")[0].strip()
        ANSWER = find_closest_matches(captions, "ANSWER:", "\n")[0].strip()
        WRONG_1 = find_closest_matches(captions, "WRONG_1:", "\n")[0].strip()
        WRONG_2 = find_closest_matches(captions, "WRONG_2:", "\n")[0].strip()
        WRONG_3 = find_closest_matches(captions, "WRONG_3:", "\n")[0].strip()
    except Exception as e:
        print(f"Error processing file {subs}: {e}")
        continue
    
    video_id = os.path.basename(subs).replace(".txt", ".mp4")
    
    duration = name_dict[video_id]["duration"]
    
    question = f"From {START} seconds to {END} seconds in the video, {QUESTION[0].lower()}{QUESTION[1:]}"
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
        "window": [START, END],
        "question": question,
        "options": answers,
        "answer": correct,
    })
    
    QAs.append(qa)
    
    qa_vague = {
        "video_id": video_id,
        "duration": duration,
        "resolution": name_dict[video_id]["resolution"],
        "questions": []
    }
    
    qa_vague["questions"].append({
        "question_id": video_id.replace(".mp4", "") + "_01",
        "window": [START, END],
        "question": vauge_question,
        "options": answers,
        "answer": correct,
    })
    
    Vague_QAs.append(qa_vague)
    
    
with open(args.output_folder + "/SVQA.json", "w") as json_f:
    json.dump(QAs, json_f, indent=4)
    
with open(args.output_folder + "/VVQA.json", "w") as json_f:
    json.dump(Vague_QAs, json_f, indent=4)
    
assert len(QAs) == len(Vague_QAs), "The number of QAs and Vague QAs should be the same"
print(f"Total QAs: {len(QAs)}")