from transformers import AutoModelForCausalLM, AutoTokenizer
import glob
import tqdm
import os
import argparse

parser = argparse.ArgumentParser(description="Generate conclusions from English subtitles")
parser.add_argument("--input_folder", type=str, required=True, help="Path to the folder containing English subtitles")
parser.add_argument("--output_folder", type=str, required=True, help="Path to the folder to save conclusions")

args = parser.parse_args()

subtitles = glob.glob(f"{args.input_folder}/*.txt")
subtitles.sort()

model_name = "./weights/Qwen2.5-7B-Instruct"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

system_prompt = """
You are an information conclusion assistant.

I will provide you with the transcript of a video. Please read the transcript carefully and write a concise summary with vision-centric (visible) information as you have seen in the video but cannot hear the audio.
"""

user_prompt = "The transcript is:\n {}"
for sub in tqdm.tqdm(subtitles, desc="Video"):
    save_path = os.path.join(args.output_folder, os.path.basename(sub))
    if os.path.exists(save_path):
        print(f"File already exists: {save_path}")
        continue
    
    with open(sub, "r") as text_file:
        captions = text_file.read()
        
    textlinenum = len(captions.split("\n"))
    if textlinenum > 2000:
        print(f"Too many lines in {sub}, skipping...")
        remove_path = sub.replace("en_subs", "errors")
        os.system(f"cp {sub} {remove_path}")
        continue

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

   
    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))
        
    with open(save_path, "w") as f:
        f.write(response)
