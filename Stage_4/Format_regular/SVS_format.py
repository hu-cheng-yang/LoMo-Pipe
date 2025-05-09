import os
import json
import glob
import csv
from tqdm import tqdm
import random
import re
import argparse

similar_questions = [
    "What events unfold between [start] and [end] seconds in the video?",
    "Summarize the actions captured from [start] to [end] seconds.",
    "Detail the visual content between [start] seconds and [end] seconds.",
    "Explain the sequence of events from [start] to [end] seconds.",
    "What changes are visible between [start] seconds and [end] seconds?",
    "Describe the scene starting at [start] seconds and ending at [end] seconds.",
    "What interactions occur from [start] to [end] seconds in the footage?",
    "Outline the key moments between [start] and [end] seconds.",
    "What is depicted in the video from [start] seconds to [end] seconds?",
    "Highlight the main activities between [start] and [end] seconds.",
    "What transitions happen between [start] seconds and [end] seconds?",
    "Break down the footage between [start] and [end] seconds.",
    "What narrative develops from [start] to [end] seconds in the clip?",
    "Identify significant events between [start] seconds and [end] seconds.",
    "What motion occurs from [start] to [end] seconds in the recording?",
    "Explain the visual progression between [start] and [end] seconds.",
    "What behaviors are shown between [start] seconds and [end] seconds?",
    "Describe the timeframe spanning [start] to [end] seconds.",
    "What story elements appear from [start] seconds to [end] seconds?",
    "Analyze the segment starting at [start] seconds and ending at [end] seconds.",
    "What visual developments occur between [start] and [end] seconds?",
    "Outline the progression shown from [start] to [end] seconds.",
    "What does the video show during the [start]-second to [end]-second interval?",
    "Explain the content within the [start]-[end] second timeframe.",
    "What activities are recorded between [start] and [end] seconds?",
    "Describe the actions visible from [start] seconds to [end] seconds.",
    "What happens in the video during the [start]-[end] second window?",
    "Break down the events between [start] and [end] seconds.",
    "What is featured in the clip from [start] to [end] seconds?",
    "Summarize the footage between [start] seconds and [end] seconds.",
    "What movements are captured between [start] and [end] seconds?",
    "Explain the visual changes from [start] to [end] seconds.",
    "What occurs in the video's [start]-[end] second segment?",
    "Detail the timeline between [start] seconds and [end] seconds.",
    "What is presented between [start] and [end] seconds of the video?",
    "Describe the key frames from [start] to [end] seconds.",
    "What transformations take place between [start] and [end] seconds?",
    "Analyze the video portion starting at [start] and ending at [end] seconds.",
    "What scenario unfolds between [start] seconds and [end] seconds?",
    "Explain the flow of events from [start] to [end] seconds.",
    "What is documented in the video from [start] to [end] seconds?",
    "Highlight the visual elements between [start] and [end] seconds.",
    "What processes are shown between [start] seconds and [end] seconds?",
    "Describe the excerpt spanning [start] to [end] seconds.",
    "What dynamics are visible from [start] to [end] seconds?",
    "Outline the sequence between [start] seconds and [end] seconds.",
    "What interactions are recorded between [start] and [end] seconds?",
    "Explain the scene transition from [start] to [end] seconds.",
    "What actions are demonstrated between [start] and [end] seconds?",
    "Break down the visual narrative from [start] to [end] seconds.",
    "What events are chronicled between [start] and [end] seconds?",
    "Describe the movement captured from [start] to [end] seconds.",
    "What is illustrated in the video between [start] and [end] seconds?",
    "Summarize the visual data between [start] seconds and [end] seconds.",
    "What occurs during the [start]-second to [end]-second period?",
    "Explain the content shown from [start] to [end] seconds.",
    "What behaviors are captured between [start] and [end] seconds?",
    "Detail the activity within the [start]-[end] second range.",
    "What is portrayed in the footage between [start] and [end] seconds?",
    "Analyze the events unfolding from [start] to [end] seconds.",
    "What visual information is conveyed between [start] and [end] seconds?",
    "Outline the key actions from [start] to [end] seconds.",
    "What developments are observed between [start] and [end] seconds?",
    "Describe the video's content during [start]-[end] seconds.",
    "What shifts happen between [start] seconds and [end] seconds?",
    "Explain the progression observed from [start] to [end] seconds.",
    "What is captured in the video between [start] and [end] seconds?",
    "Break down the timeline from [start] seconds to [end] seconds.",
    "What scenes are included between [start] and [end] seconds?",
    "Highlight the transitions from [start] to [end] seconds.",
    "What activity is evident between [start] seconds and [end] seconds?",
    "Detail the visual sequence between [start] and [end] seconds.",
    "What occurs within the [start]-[end] second interval?",
    "Explain the footage's content from [start] to [end] seconds.",
    "What actions unfold between [start] and [end] seconds?",
    "Describe the events documented from [start] to [end] seconds.",
    "What is displayed between [start] seconds and [end] seconds?",
    "Analyze the visual changes from [start] to [end] seconds.",
    "What happens in the specified [start]-[end] second timeframe?",
    "Summarize the video segment between [start] and [end] seconds.",
    "What movements are recorded between [start] and [end] seconds?",
    "Explain the events taking place from [start] to [end] seconds.",
    "What is revealed in the video between [start] and [end] seconds?",
    "Detail the actions that occur between [start] and [end] seconds.",
    "What narrative is shown from [start] seconds to [end] seconds?",
    "Outline the visual content between [start] and [end] seconds.",
    "What interactions are visible between [start] and [end] seconds?",
    "Describe the progression of events from [start] to [end] seconds.",
    "What transformations are evident between [start] and [end] seconds?",
    "Break down the recorded activity from [start] to [end] seconds.",
    "What scenario is captured between [start] and [end] seconds?",
    "Explain the key developments from [start] to [end] seconds.",
    "What processes unfold between [start] seconds and [end] seconds?",
    "Highlight the main events between [start] and [end] seconds.",
    "What changes take place from [start] to [end] seconds?",
    "Analyze the visual elements between [start] and [end] seconds.",
]

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

parser = argparse.ArgumentParser(description="Generate SVS format QAs")
parser.add_argument("--input_folder", type=str, required=True, help="Path to the folder containing English subtitles")
parser.add_argument("--output_folder", type=str, required=True, help="Path to the folder to save QAs")
parser.add_argument("--meta_file", type=str, required=True, help="Path to the metadata file")
args = parser.parse_args()


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

for subs in tqdm(subtitles):
    
    subs_time = subs.replace("one_sentence_qa", "fine_quiz_1")
    
    with open(subs_time, "r") as text_file:
        captions = text_file.read()
        
    try:
        START = find_closest_matches(captions, "START:", "\n")[0].strip()
        END = find_closest_matches(captions, "END:", "\n")[0].strip()
        START = float(START)
        END = float(END)
    except Exception as e:
        print(f"Error processing file {subs}: {e}")
        continue
    
    with open(subs, "r") as text_file:
        captions = text_file.read()
        
    captions += "\n"
    try:
        A_answer = find_closest_matches(captions, "A:", "|")[0].replace("|", "").strip()
        B_answer = find_closest_matches(captions, "B:", "|")[0].replace("|", "").strip()
        C_answer = find_closest_matches(captions, "C:", "|")[0].replace("|", "").strip()
        D_answer = find_closest_matches(captions, "D:", "\n")[0].replace("|", "").strip()
        
    except Exception as e:
        print(f"Error processing file {subs}: {e}")
        continue
    
    video_id = os.path.basename(subs).replace(".txt", ".mp4")
    
    duration = name_dict[video_id]["duration"]
    
    question = random.choice(similar_questions).replace("[start]", str(START)).replace("[end]", str(END))
    
    qa = {
        "video_id": video_id,
        "duration": duration,
        "resolution": name_dict[video_id]["resolution"],
        "questions": []
    }
    
    
    choice = ["A", "B", "C", "D"]
    random.shuffle(choice)
    
    correct = choice[0]
    
    answers = [choice[0] + ": " + A_answer,
               choice[1] + ": " + B_answer,
               choice[2] + ": " + C_answer,
               choice[3] + ": " + D_answer]
    
    answers = sorted(answers, key=lambda x: x[0])
    
    qa["questions"].append({
        "question_id": video_id.replace(".mp4", "") + "_01",
        "window": [START, END],
        "question": question,
        "options": answers,
        "answer": correct,
    })
    
    QAs.append(qa)
    
    
    
with open(os.path.join(args.output_folder, "SVS_format.json"), "w") as json_f:
    json.dump(QAs, json_f, indent=4)
    
print(f"Total QAs: {len(QAs)}")