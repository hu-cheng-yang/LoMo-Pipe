from transformers import AutoModelForCausalLM, AutoTokenizer
import glob
import tqdm
import os
import random
import argparse

parser = argparse.ArgumentParser(description="Generate quiz from English subtitles")
parser.add_argument("--input_folder", type=str, required=True, help="Path to the folder containing English subtitles")
parser.add_argument("--output_folder", type=str, required=True, help="Path to the folder to save quiz")
args = parser.parse_args()


subtitles = glob.glob(f"{args.input_folder}/*.txt")
subtitles.sort()

model_name = "./weights/Qwen2.5-7B-Instruct"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto",
    use_cache=True,
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

system_prompt = """
Process multiple lines video subtitles formatted as `TEXT [Start/End]` (timestamps as floats). Rules:  

1. **Validation**  
   - Valid only if the text describes:  
     - Fine the best valid **one** line and ignore the others
     - A **complete visual event** with clear start/end  
     - Observable physical actions/phenomena  
     - No contextual dependencies  
    

2. **Output**  
     - Ask the question like you are watching the video instead of reading the subtitles
     - Preserve original subtitle text exactly  
     - Extract timestamps  
     - Generate components **in English only**  
     - Print the most meaningful line with **one** question-answer pair


**Strict Output Format**  
```  
* SUBTITLE: [Original text with timestamps]  
* START: [float]  
* END: [float]  
* CONCLUSION: [Neutral summary]  
* QUESTION: [Visual-centric question]  
* ANSWER: [Single correct fact]  
* WRONG_1: [Plausible distractor]  
* WRONG_2: [Plausible distractor]  
* WRONG_3: [Plausible distractor]  
```  

---

**Example Input**  
The girl. [0.0/1.0]
A droplet falls into a still pond, creating concentric ripples [8.4/9.6]
Oh no! The water is boiling [9.6/10.0]
Haha, is that a fish? [10.0/10.5]

**Example Output**  
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

maxquestion = 1  # number of questions to generate
max_line = 30    # max number of lines to read from the subtitles

user_prompt = "The subtitles is:\n {}"

for sub in tqdm.tqdm(subtitles, desc="Video"):
    count = 0
    with open(sub, "r") as text_file:
        captions = text_file.read()
        
    _captions = captions.split("\n")
    
    save_path = os.path.join(args.output_folder, os.path.basename(sub))
    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))
    
    ratio = 0.4
    start = int(len(_captions) * ratio)
    reserve = len(_captions) - start
    if reserve > max_line:
        start = random.randint(start, len(_captions) - max_line)
    else:
        if len(_captions) >= max_line:
            start = random.randint(0, len(_captions) - max_line)
        else:
            start = 0
    
    with open(save_path, "w") as f:

            c = "\n".join(_captions[start:start + max_line])
            
            prompt = user_prompt.format(c.strip())
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
            text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

            generated_ids = model.generate(
                **model_inputs,
                max_new_tokens=32768,
            )
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]

            response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            f.write(response + "\n===\n")
