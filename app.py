
import streamlit as st
import cv2
import os
import subprocess
import tempfile
import imageio_ffmpeg
import math
from urllib.parse import urlparse

st.set_page_config(
    page_title="AI Shorts Generator",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 AI Shorts Generator")
st.write("Turn long videos into vertical Shorts!")

st.divider()

# YOUTUBE URL
st.header("🔗 YouTube Video Import")

video_url = st.text_input(
    "Paste YouTube Video URL",
    placeholder="https://www.youtube.com/watch?v=..."
)

def valid_youtube_url(url):
    try:
        parsed = urlparse(url.strip())
        host = parsed.netloc.lower().split(":")[0]

        return (
            parsed.scheme in ["http", "https"]
            and host in [
                "youtube.com",
                "www.youtube.com",
                "m.youtube.com",
                "youtu.be",
                "www.youtube-nocookie.com"
            ]
        )
    except Exception:
        return False

if video_url.strip():

    if valid_youtube_url(video_url):

        st.success("Valid YouTube link!")

        st.subheader("YouTube Video Preview")

        st.video(video_url)

        st.info(
            "Preview only. To create Shorts, upload the "
            "authorized original video file below."
        )

    else:
        st.error("Please enter a valid YouTube URL.")

st.divider()

# VIDEO UPLOAD
st.header("📤 Upload Authorized Video")

video = st.file_uploader(
    "Choose your video file",
    type=["mp4", "mov", "mkv", "webm"]
)

if video:
    st.success("Video uploaded: " + video.name)

st.divider()

# SETTINGS
st.header("⚙️ Shorts Settings")

duration = st.selectbox(
    "Short Duration",
    [30, 45, 60],
    index=2
)

max_clips = st.slider(
    "Maximum Shorts",
    1, 10, 5
)

categories = st.multiselect(
    "Preferred Moments",
    [
        "Funny 😂",
        "Romantic ❤️",
        "Action ⚔️",
        "Emotional 🥺",
        "Shocking 😱",
        "Viral 🔥"
    ],
    default=["Funny 😂", "Action ⚔️"]
)

st.info("Video Format: 9:16 | MP4 | 1080 × 1920")

# PROCESS VIDEO
if st.button(
    "✨ Generate Shorts",
    use_container_width=True
):

    if video is None:

        if video_url.strip() and valid_youtube_url(video_url):
            st.warning(
                "YouTube preview is available, but direct "
                "video importing is not enabled. Please upload "
                "your authorized video file."
            )
        else:
            st.error(
                "Please enter a valid YouTube URL or upload a video."
            )

    else:

        with st.spinner("Preparing your video..."):

            workdir = tempfile.mkdtemp()

            input_path = os.path.join(
                workdir, "input_video"
            )

            with open(input_path, "wb") as f:
                f.write(video.getbuffer())

            cap = cv2.VideoCapture(input_path)

            fps = cap.get(cv2.CAP_PROP_FPS)
            frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

            cap.release()

            if not fps or fps <= 0 or frames <= 0:

                st.error("Unable to read this video.")

            else:

                total_seconds = frames / fps

                total_clips = min(
                    max_clips,
                    math.ceil(total_seconds / duration)
                )

                ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

                progress = st.progress(0)
                status = st.empty()

                results = []

                for i in range(total_clips):

                    start = i * duration

                    clip_duration = min(
                        duration,
                        total_seconds - start
                    )

                    if clip_duration <= 0:
                        break

                    output_path = os.path.join(
                        workdir,
                        f"short_{i+1}.mp4"
                    )

                    status.write(
                        f"Creating Short {i+1} of {total_clips}..."
                    )

                    command = [
                        ffmpeg,
                        "-y",
                        "-ss", str(start),
                        "-i", input_path,
                        "-t", str(clip_duration),
                        "-vf",
                        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
                        "-c:v", "libx264",
                        "-preset", "ultrafast",
                        "-crf", "23",
                        "-c:a", "aac",
                        "-b:a", "128k",
                        "-pix_fmt", "yuv420p",
                        "-movflags", "+faststart",
                        output_path
                    ]

                    result = subprocess.run(
                        command,
                        capture_output=True,
                        text=True
                    )

                    if (
                        result.returncode == 0
                        and os.path.exists(output_path)
                    ):
                        with open(output_path, "rb") as f:
                            results.append(f.read())

                    progress.progress(
                        (i + 1) / total_clips
                    )

                status.empty()

                if results:

                    st.session_state["shorts_results"] = results

                    st.success(
                        f"Successfully created {len(results)} Shorts!"
                    )

                else:
                    st.error(
                        "Video processing failed. Try another video."
                    )

# SHOW RESULTS
if st.session_state.get("shorts_results"):

    st.divider()
    st.header("🎬 Your Generated Shorts")

    for index, data in enumerate(
        st.session_state["shorts_results"]
    ):

        st.subheader(f"Short #{index + 1}")

        st.video(data)

        st.download_button(
            "⬇️ Download MP4",
            data=data,
            file_name=f"ai_short_{index+1}.mp4",
            mime="video/mp4",
            key=f"download_{index}"
        )

        caption = (
            f"Amazing moment from the video! 🔥\n\n"
            f"#Shorts #YouTubeShorts #InstagramReels "
            f"#Viral #Trending"
        )

        st.markdown("**Social Media Caption**")

        st.code(caption)

st.divider()

st.caption("AI Shorts Generator | Version 4.0")
