import whisper
from faster_whisper import WhisperModel, BatchedInferencePipeline
import os
from moviepy import VideoFileClip
import sys
from tqdm import tqdm
from contextlib import redirect_stdout, redirect_stderr
import csv
import uuid
import argparse

#extract the audio from video
def mp4_to_wav(mp4_file, wav_file):
    video = VideoFileClip(mp4_file)
    video.audio.write_audiofile(wav_file)
    video.close()

#transcribe the extracted audio
def transcribe_audio(model, video, audio_path, sub_path):
    segments, info = model.transcribe(
        word_timestamps=True,
        audio=audio_path,
        language="zh",
        initial_prompt="以下是普通话的句子。",
        beam_size=5,
        vad_filter=True,
        chunk_length=5,
        batch_size=16,
    )
    video_name = video.split('/')[-1].split('.')[0]
    with open(f'{sub_path}/{video_name}.txt', "w") as f:
        for segment in segments:
            f.write(f"{segment.text} [{segment.start}/{segment.end}]\n")
    pass


def main(video_path, sub_path, audio_path, log_path, tmp_id):
    model_size = "large-v2"
    model = WhisperModel(model_size, device="cuda", compute_type="float16") #using the large model
    batched_model = BatchedInferencePipeline(model=model)

    videos = video_path
    print(f"=====> {len(videos)} videos to process")

    log_f = open(log_path, "w")

    video_bar = tqdm(videos, desc="Processing videos", unit="video")
    for video in video_bar:
            video_bar.set_description(f"Processing {video}")
            # uncomment the following if some audio files already extracted
            '''
            if f'{video[:-4]}.wav' in os.listdir(audio_path):
                try:
                    with redirect_stdout(devnull), redirect_stderr(devnull):
                        transcribe_audio(model, video, f'{audio_path}/{video[:-4]}.wav', sub_path)
                except Exception as e:
                    print(f"Error processing video {video}: {e}", file=sys.stderr)
            else:
            '''
            video_name = video.split('/')[-1].split('.')[0]
            if os.path.exists(f'{sub_path}/{video_name}.txt'):
                print(f"=====> {video_name} already processed, skipping")
                continue
            try:
                mp4_to_wav(f'{video}', f'{log_path.rsplit("/", 1)[0]}/{tmp_id}.wav')
                transcribe_audio(batched_model, video, f'{log_path.rsplit("/", 1)[0]}/{tmp_id}.wav', sub_path)
            except Exception as e:
                print(f"Error processing video {video}: {e}")
                log_f.write(video + "\n")
                
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe audio from video files")
    parser.add_argument('--video_path', type=str, required=True, help='Path to the video file or directory')
    parser.add_argument('--sub_path', type=str, required=True, help='Path to save the transcriptions')
    parser.add_argument('--audio_path', type=str, required=True, help='Path to save the audio files')
    parser.add_argument('--log_path', type=str, required=True, help='Path to save the log file')


    video_list = open(args.video_path, 'r').read.splitlines()
    video_list = [video.strip() for video in video_list if video.strip()]

    main(video_path=video_list, sub_path=args.sub_path, audio_path=args.audio_path, log_path=args.log_path, tmp_id=str(uuid.uuid4()))