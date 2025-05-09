from transformers import AutoModelForCausalLM, AutoTokenizer
import glob
import json
import tqdm
import os
import argparse

parser = argparse.ArgumentParser(description="Generate quiz from English subtitles")
parser.add_argument("--input_folder", type=str, required=True, help="Path to the folder containing English subtitles")
parser.add_argument("--output_folder", type=str, required=True, help="Path to the folder to save quiz")
parser.add_argument("--VTG_json", type=str, required=True)


datas = json.load(open(args.VTG_json, "r"))


model_name = "./weights/Qwen2.5-7B-Instruct"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

system_prompt = """
You will get a sentence description of the video. Please provide four choices for the question "What is the video about?".
The answer should be a single sentence. The four choices should be in the form of "A: [answer1] | B: [answer2] | C: [answer3] | D: [answer4]".
The answer A should be the correct answer, and the other three answers should be plausible distractors.
"""

user_prompt = "The sentence description is:\n {}"

for sub in tqdm.tqdm(datas, desc="Video"):
    
    video_id = sub["video_id"]
    captions = sub["relevant_windows"][0]["descriptions"]

    prompt = user_prompt.format(captions)

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

    save_path = os.path.join(args.output_folder, f"{video_id.replace('.mp4', '.txt')}")
    with open(save_path, "w") as f:
        f.write(response)
