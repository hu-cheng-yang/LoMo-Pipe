from transformers import AutoModelForCausalLM, AutoTokenizer
import glob
import tqdm
import os
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
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

system_prompt = """
You will get a concluion of the video. Please provide four choices for the question "What is the video about?".
The answer should be a single sentence. The four choices should be in the form of "A: [answer1] | B: [answer2] | C: [answer3] | D: [answer4]".
The answer A should be the correct answer, and the other three answers should be plausible distractors.
"""

user_prompt = "The concluion is:\n {}"

for sub in tqdm.tqdm(subtitles, desc="Video"):
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

    save_path = os.path.join(args.output_folder, os.path.basename(sub))
    with open(save_path, "w") as f:
        f.write(response)
