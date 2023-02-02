import streamlit as st #open-source framework to build quick webapps
import whisper #open-source sota neural net for asr
from pytube import YouTube #library for downloading YouTube Videos
from transformers import pipeline #the holy grail of all pre-trained LLMs
import os #provides a portable way of using operating system dependent functionality
import re #provides regular expression matching operations

#runs the function and stores the Whisper model in a local cache
@st.cache(allow_output_mutation=True)
def load_whisper():
    whisper_model = whisper.load_model("base")
    return whisper_model

#runs the function and stores the Transformer model in a local cache
@st.cache(allow_output_mutation=True)
def load_summarizer():
    model = pipeline("summarization")
    return model

#takes the video url as input and returns thumbnail & title of video
def get_video_metadata(url): #gets the video metadata from url
    yt = YouTube(url)
    thumbnail = yt.thumbnail_url
    title = yt.title
    return thumbnail, title

#function that extracts audio file using pytube
def get_audio(url: object) -> object: 
    yt = YouTube(url)
    video = yt.streams.filter(only_audio=True).first() #chooses the first audio stream available
    out_file=video.download(output_path=".")
    base, ext = os.path.splitext(out_file)
    new_file = base+'.mp3' #saves as mp3 file
    os.rename(out_file, new_file)
    a = new_file
    return a

#Whisper model returns the transcript with audio as input obtained from above function
def get_text(url, model): 
    if url != '': output_text_transcribe = ''
    result = model.transcribe(get_audio(url))
    return result['text'].strip()

#breaks down large text blob into chunks so LLMs have limited processing capability
def generate_text_chunks(text):
    res = []
    num_iters = int(len(text)/1000)
    for i in range(0, num_iters + 1):
        start = 0
        start = i * 1000
        end = (i + 1) * 1000
        res.append(text[start:end])
    return res

#execution starts from here-
st.markdown("<h1 style='text-align: center; color: white;'>Youtube Video Summarizer</h1><br>", unsafe_allow_html=True)
st.info("View a summary of any Youtube video using its url.")

st.caption("Note: The longer the video, longer will be the time to generate summary. It's advisable to use 5-10 min videos for quick results.")

#user input of video url is stored
video_url = st.text_input("Enter YouTube video URL", "https://www.youtube.com/watch?v=yxsoE3jO8HM")

#flag to toggle 'Summary' button based on validity of url
summ_flag = False

#check if video url is valid and matches the pattern using regex
url_regex = r"^(http(s)?:\/\/)?((w){3}.)?youtu(be|.be)?(\.com)?\/.+"
url_check = re.search(url_regex,video_url)
if url_check == None:
    st.error('Please provide a valid YouTube url!', icon="🚨")
    summ_flag = True

#invokes the task to generate summary
button = st.button("Summarize", disabled=summ_flag)

#loads the whisper model
a2t = load_whisper()

#loads the transformer pipeline model
summarizer = load_summarizer()

#displays spinner as a feedback to user by the time summary is being generated
with st.spinner("Generating Summary.."):
    if button and video_url:
        thumbnail, title = get_video_metadata(video_url)
        st.image(thumbnail)
        st.header(title)
        video_transcript = get_text(video_url, a2t)
        text_chunks = generate_text_chunks(video_transcript)
        res = summarizer(text_chunks)
        video_summary = ' '.join([summ['summary_text'] for summ in res]) #summaries of all the chunks are put together
        st.write(video_summary) #displays final summary
