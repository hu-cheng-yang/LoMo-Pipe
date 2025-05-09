import os
import json
import glob
import csv
from tqdm import tqdm
import random
import re
import argparse

video_questions = [  
    "Explain the main topic of the video.",  
    "Summarize the video’s core message.",  
    "Describe the central theme of the video.",  
    "Break down the key points discussed in the video.",  
    "Identify the purpose of the video.",  
    "Outline the subjects covered in the video.",  
    "Highlight the most important takeaways from the video.",  
    "Discuss the problems explored in the video.",  
    "Share the primary argument presented in the video.",  
    "Analyze the narrative structure of the video.",  
    "Explore the lessons taught in the video.",  
    "Define the target audience of the video.",  
    "Clarify the inspiration behind the video.",  
    "List the techniques demonstrated in the video.",  
    "Detail the research findings mentioned in the video.",  
    "Examine the cultural references in the video.",  
    "Review the case studies analyzed in the video.",  
    "Interpret the emotional tone of the video.",  
    "Unpack the ethical questions raised in the video.",  
    "Compare the ideas showcased in the video.",  
    "Evaluate the practical advice given in the video.",  
    "Mention the data or statistics cited in the video.",  
    "Depict the storytelling approach used in the video.",  
    "Emphasize the call-to-action included in the video.",  
    "Debate the controversies addressed in the video.",  
    "Reveal the historical context provided in the video.",  
    "Pinpoint the artistic elements featured in the video.",  
    "State the goals the video aims to accomplish.",  
    "Illustrate the symbolic meanings within the video.",  
    "Critique the solutions proposed in the video.",  
    "Report the updates or news shared in the video.",  
    "Question the assumptions challenged in the video.",  
    "Link the video’s content to current trends.",  
    "Probe the motivations driving the video’s creation.",  
    "Categorize the type of information the video provides.",  
    "Reflect on the societal impacts discussed in the video.",  
    "Dissect the step-by-step process outlined in the video.",  
    "Assess the educational value of the video.",  
    "Address the myths debunked in the video.",  
    "Characterize the humor or satire employed in the video.",  
    "Trace the evolution of ideas presented in the video.",  
    "Justify the significance of the video’s conclusions.",  
    "Map the relationships between topics in the video.",  
    "Rank the importance of issues tackled in the video.",  
    "Predict the long-term implications suggested by the video.",  
    "Validate the credibility of sources referenced in the video.",  
    "Challenge the perspectives offered in the video.",  
    "Synthesize the interdisciplinary themes in the video.",  
    "Contextualize the experimental results shown in the video.",  
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

parser = argparse.ArgumentParser(description="Generate quiz from English subtitles")
parser.add_argument("--input_folder", type=str, required=True, help="Path to the folder containing English subtitles")
parser.add_argument("--output_folder", type=str, required=True, help="Path to the folder to save quiz")
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
    
    question = random.choice(video_questions)
    
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
        "question": question,
        "options": answers,
        "answer": correct,
    })
    
    QAs.append(qa)
    
    
    
with open(os.path.join(args.output_folder, "GVS.json"), "w") as json_f:
    json.dump(QAs, json_f, indent=4)
    
print(f"Total QAs: {len(QAs)}")