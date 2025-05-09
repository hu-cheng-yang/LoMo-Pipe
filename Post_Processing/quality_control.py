import os
import json
import random

import argparse

parser = argparse.ArgumentParser(description="Quality Control")
parser.add_argument("--input_json", type=str, help="Path to the input JSON file")
parser.add_argument("--output_json", type=str, help="Path to the output JSON file")
parser.add_argument("--video_num", type=int, default=100, help="Number of videos to sample from each duration range")
args = parser.parse_args()

def listword_in_sentence(words, sentence):
    """
    Check if any of the words in the list are present in the sentence.
    """
    for word in words:
        if word in sentence:
            return True
    return False


stop_words = ["talk", "talked", "talking", "told", "say", "said", "saying", "ask", "asked", "asking", "tell", "tells", "told", "think", "thought", "thinking", "believe", "believed", "believing", "know", "knew", "knowing", "hear", "heard", "hearing", 
              "speak", "spoke", "speaking", "spoken", "subtitle"]


setting_file = json.load(open(args.input_json))
print(len(setting_file))

duration_bound = [
    (1 * 60, 10 * 60),  # 1 min to 10 min
    (10 * 60, 30 * 60),  # 10 min to 30 min
    (30 * 60, 60 * 60),  # 30 min to 1 hour
    (120 * 60, float("inf"))  # more than 2 hours
]

seperate = [[] for _ in range(len(duration_bound))]

count = 0
for s in setting_file:
    questions = s["questions"]
    
    question_line = ""
    
    for q in questions:
        if "question" in q:
            question_line += q["question"]
        if "descriptions" in q:
            question_line += q["descriptions"]
            
            _d = q["descriptions"][1:]
            if _d != _d.lower():
                continue
            
            
    question_line = question_line.lower()
    if listword_in_sentence(stop_words, question_line):
        continue
    
    if "what" not in question_line or "how" not in question_line:
        continue
    
    resolution = s["resolution"]
    
    h, w = resolution.replace("[", "").replace("]", "").split(",")
    h = int(h)
    w = int(w)
    
    if h < 720 or w < 720:
        continue
    
    duration = s["duration"]
    for i, bound in enumerate(duration_bound):
        if bound[0] <= duration < bound[1]:
            seperate[i].append(s)
    
        

final_result = []

for s in seperate:
    if len(s) > 0:
        random.shuffle(s)
        final_result.extend(s[:args.video_num])
        
        
print(len(final_result))

with open(args.output_json, "w") as f:
    json.dump(final_result, f, indent=4)