import glob
import os
import json
import argparse

parser = argparse.ArgumentParser(description="Aggregate tasks from multiple JSON files")
parser.add_argument("--input_folder", type=str, required=True, help="Path to the folder containing JSON files")
parser.add_argument("--output_file", type=str, required=True, help="Path to the output JSON file")
args = parser.parse_args()

json_files = glob.glob(f"{args.input_folder}/*.json")

all_task = {}
metas = {}

for json_file in json_files:
    
    task = {}
    with open(json_file, "r") as f:
        contain_tasks = json.load(f)
        
    for t in contain_tasks:
        video_id = t["video_id"]
        duration = t["duration"]
        resolution = t["resolution"]
        
        if video_id not in metas:
            metas[video_id] = {
                "video_id": video_id,
                "duration": duration,
                "resolution": resolution
            }
            
        if "questions" in t:
            for question in t["questions"]:
                task[video_id] = question
                
        if "relevant_windows" in t:
            for window in t["relevant_windows"]:
                task[video_id] = window
                
    task_type = json_file.split("/")[-1].replace(".json", "")
    all_task[task_type] = task
    

all_contains_id = None

for key, value in all_task.items():
    if all_contains_id is None:
        all_contains_id = set(value.keys())
    else:
        all_contains_id = all_contains_id.intersection(set(value.keys()))
        
        
print(len(all_contains_id))

result = []

for video_id in all_contains_id:
    meta = metas[video_id]
    questions = []
    for key, value in all_task.items():
        task = key
        question = value[video_id]
        question["task"] = task
        questions.append(question)
        
    meta["questions"] = questions
    
    result.append(meta)
    
with open(args.output_file, "w") as json_f:
    json.dump(result, json_f, indent=4)