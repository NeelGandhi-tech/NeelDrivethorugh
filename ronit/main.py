import os
import moviepy.editor as mp
import speech_recognition as sr
import openai

#Use your own gpt api key
OPENAI_API_KEY = "Open_AI_Key"
openai.api_key = OPENAI_API_KEY


def transcribe_video(video_path):
    try:
        video = mp.VideoFileClip(video_path)
        audio_path = "temp_audio.wav"
        video.audio.write_audiofile(audio_path)
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio_data = recognizer.record(source)
            transcription = recognizer.recognize_google(audio_data)

        os.remove(audio_path)
        return transcription

    except Exception as e:
        print(f"Error processing {video_path}: {e}")
        return None

def analyze_transcription(transcription):
    try:
        prompt = f"""
        Please analyze the following drive-through interaction and provide a review of the customer experience.
        Focus on tone, clarity, and helpfulness of the staff, and whether the customer had a positive or negative experience.

        Transcript:
        {transcription}
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        analysis = response.choices[0].message['content']
        return analysis

    except Exception as e:
        print(f"Error analyzing transcription: {e}")
        return "Analysis failed."


def process_videos(input_dir, output_file):
    if not os.path.exists(input_dir):
        print(f"Input directory {input_dir} does not exist.")
        return

    results = []
    for file_name in os.listdir(input_dir):
        if file_name.endswith((".mp4", ".mkv", ".avi", ".mov")):  # Add other formats if needed
            video_path = os.path.join(input_dir, file_name)
            print(f"Processing video: {video_path}")
            transcription = transcribe_video(video_path)
            if not transcription:
                print(f"Skipping analysis for {video_path}.")
                continue

            analysis = analyze_transcription(transcription)
            results.append((file_name, transcription, analysis))

    with open(output_file, "w", encoding="utf-8") as f:
        for video_name, transcription, analysis in results:
            f.write(f"Video: {video_name}\n")
            f.write(f"Transcription:\n{transcription}\n")
            f.write(f"Analysis:\n{analysis}\n")
            f.write("-" * 50 + "\n")
    
    print(f"All results saved to {output_file}")

if __name__ == "__main__":
    input_directory = "ronit/videos"  #This is the folder/directory where the videos are
    output_file = "ronit/driveThroughAnalysis.txt"  #This is for the file where the transcriptions are saved
    
    process_videos(input_directory, output_file)
