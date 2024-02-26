# Copyright 2018-2022 Streamlit Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import subprocess

import speech_recognition as sr
import streamlit as st
import whisper
from googletrans import Translator
from gtts import gTTS
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)
global global_file_name
global extracted_text
global extracted_text_translate
global synthesized_audio_path

# Define language mapping
language_mapping = {
    'English': 'en',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Italian': 'it',
    'Portuguese': 'pt',
    'Polish': 'pl',
    'Turkish': 'tr',
    'Russian': 'ru',
    'Dutch': 'nl',
    'Czech': 'cs',
    'Malayalam': 'ml',
    'Hindi': 'hi',
    'Arabic': 'ar',
    'Chinese (Simplified)': 'zh-cn'
}

def upload_video():
    uploaded_file = st.file_uploader("Upload Video", type=["mp4"])
    if uploaded_file is not None:
        with open("uploaded_video.mp4", "wb") as f:
            f.write(uploaded_file.getvalue())
        return "uploaded_video.mp4"
    return None

def resize_video(filename):
    print("resize_video: "+str(filename))
    # Extracting file extension
    file_name, file_extension = os.path.splitext(filename)
    output_filename = f"resized_{file_name}{file_extension}"

    # Execute ffmpeg command to resize video
    cmd = f"ffmpeg -i {filename} -vf scale=-1:720 -y {output_filename}"
    subprocess.run(cmd, shell=True)

    # Check if output file exists
    if os.path.exists(output_filename):
        return output_filename
    else:
        print("Error: Resized file was not generated.")
        return None

def extract_text(extract_video_path):
    print("extract_text:"+extract_video_path)
    # Ensure video_path variable exists
    if extract_video_path is not None and os.path.exists(extract_video_path):
        extract_video_path = os.path.abspath(extract_video_path)
        # Specify the full path for the output audio file
        output_audio_path = os.path.join(os.path.dirname(extract_video_path), "output_audio.wav")
        ffmpeg_command = f'ffmpeg -i "{extract_video_path}" -acodec pcm_s24le -ar 48000 -q:a 0 -map a -y "{output_audio_path}"'
        print("command:"+ffmpeg_command)
        subprocess.run(ffmpeg_command, shell=True)
        print("command ran successfully")
        if os.path.exists(output_audio_path):
            st.audio(output_audio_path, format='audio/wav')
            st.markdown("[Download Extracted Audio](output_audio.wav)")
            
            model = whisper.load_model("base")
            result = model.transcribe(output_audio_path)
            whisper_text = result["text"]
            whisper_language = result['language']
    
            print("Audio text:", whisper_text)
            return whisper_text
        else:
            print("Error: Audio extraction failed.")
    else:
        print("No video uploaded. Please upload a video first.")

def translate_text(text, target_language_code):
    translator = Translator()
    translated_text = translator.translate(text, dest=target_language_code).text
    return translated_text

def synthesize_audio(text, language):
    tts = gTTS(text=text, lang=language, slow=False)
    tts.save("output_synth.mp3")
    return "output_synth.mp3"

def download_audio_video(audio_path, video_path):
    st.audio(audio_path, format='audio/mp3')
    st.warning("Downloading video and audio...")
    with open(video_path, "rb") as video_file:
        video_bytes = video_file.read()
    with open(audio_path, "rb") as audio_file:
        audio_bytes = audio_file.read()
    st.download_button(label="Download Video", data=video_bytes, file_name="output_video.mp4")
    st.download_button(label="Download Audio", data=audio_bytes, file_name="output_audio.mp3")

def download_audio(audio_path):
    st.audio(audio_path, format='audio/mp3')
    st.warning("Downloading audio...")
    with open(audio_path, "rb") as audio_file:
        audio_bytes = audio_file.read()
    st.download_button(label="Download Audio", data=audio_bytes, file_name="output_audio.mp3")

def run():
    st.title("Video to Audio Conversion and Translation App")
    target_language = st.radio("Select target language", list(language_mapping.keys()))

    # Upload Video
    st.header("Step 1: Upload Video")
    video_path = upload_video()
    global_file_name = video_path

    if video_path:
        st.success("Video uploaded successfully.")
    else:
        st.warning("Please upload a video to proceed.")

    # Resize Video (Optional)
    resize_to_720p = st.checkbox("Resize to 720p (better results)")
    if resize_to_720p and global_file_name and st.button("Resize Video"):
        st.info("Resizing '" +global_file_name+"' to 720p...")
        resized_file_name = resize_video(global_file_name)
        global_file_name = resized_file_name
        st.info("Resized to 720p: " + resized_file_name)

    # Extract Audio Text From Video - Placeholder
    if st.button("Extract Audio Text"):
        if video_path:
            extracted_text = extract_text(str(video_path))
            st.success("Audio text extracted successfully.")
            st.text("Audio Text:")
            st.write(extracted_text)
            if extracted_text and target_language:            
                extracted_text_translate = translate_text(extracted_text, language_mapping[target_language])
                st.success("Text translated successfully.")
                st.text("Translated Text:")
                st.write(extracted_text_translate)
                if extracted_text_translate:
                    synthesized_audio_path = synthesize_audio(extracted_text_translate, language_mapping[target_language])
                    st.success("Audio synthesized successfully.")
                    st.audio(synthesized_audio_path, format='audio/mp3')
                    st.success("Audio played successfully.")
                    if synthesized_audio_path:
                        download_audio(synthesized_audio_path)
                    else:
                        st.warning("Please synthesize audio first.")
                else:
                    st.warning("Please translate text first.")
            else:
                st.warning("Please extract audio text first.")
        else:
            st.warning("Please upload a video first.")

    # Translation
    st.header("Step 3: Translation")
    print("Translation:"+target_language)
    if st.button("Translate Text") and target_language:
        print("Translation Started")        
        print("Translation Text:"+str(extracted_text))        
        print("Translate to :"+target_language)
        if extracted_text and target_language:            
            extracted_text_translate = translate_text(extracted_text, language_mapping[target_language])
            st.success("Text translated successfully.")
            st.text("Translated Text:")
            st.write(extracted_text_translate)
        else:
            st.warning("Please extract audio text first.")

    # Voice Synthesis
    st.header("Step 4: Voice Synthesis")
    if st.button("Synthesize Audio"):
        if extracted_text_translate:
            synthesized_audio_path = synthesize_audio(extracted_text_translate, language_mapping[target_language])
            st.success("Audio synthesized successfully.")
            st.audio(synthesized_audio_path, format='audio/mp3')
            st.success("Audio played successfully.")
        else:
            st.warning("Please translate text first.")
    
    # Download Audio
    st.header("Step 5: Download Audio")
    if st.button("Download Audio"):
        if synthesized_audio_path:
            download_audio(synthesized_audio_path)
        else:
            st.warning("Please synthesize audio first.")
    
    # Download Audio and Video
    st.header("Step 6: Download Audio and Video")
    if st.button("Download Audio and Video"):
        if synthesized_audio_path and global_file_name:
            download_audio_video(synthesized_audio_path, global_file_name)
        else:
            st.warning("Please synthesize audio and upload video first.")

if __name__ == "__main__":
    run()
