
import streamlit as st

st.set_page_config(
    page_title="AI Shorts Generator",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 AI Shorts Generator")
st.write("Turn long videos into amazing short videos with AI!")

st.divider()

st.subheader("1. Enter Video URL")

video_url = st.text_input(
    "Paste your video URL",
    placeholder="https://youtube.com/watch?v=..."
)

st.subheader("2. Or Upload Your Video")

video_file = st.file_uploader(
    "Upload your own or authorized video",
    type=["mp4", "mov", "mkv", "webm"]
)

st.subheader("3. AI Settings")

categories = st.multiselect(
    "Select moments to find",
    ["Funny 😂", "Romantic ❤️", "Action ⚔️",
     "Emotional 🥺", "Shocking 😱", "Viral 🔥"],
    default=["Funny 😂", "Action ⚔️", "Emotional 🥺"]
)

duration = st.selectbox(
    "Short video duration",
    ["30 seconds", "45 seconds", "60 seconds"]
)

st.info("Output format: Vertical 9:16")

if st.button("✨ Generate AI Shorts"):
    if video_file is not None:
        st.success("Video uploaded! AI processing will be added next.")
    elif video_url:
        st.warning("URL processing will be added in the next development phase.")
    else:
        st.error("Please enter a URL or upload a video.")

st.divider()
st.caption("AI Shorts Generator | Version 1.0")
