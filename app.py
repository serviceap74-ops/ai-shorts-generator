
import streamlit as st
import cv2
import os
import subprocess
import tempfile
import imageio_ffmpeg
import math

st.set_page_config(
    page_title="AI Shorts Generator",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 AI Shorts Generator")
st.write("Turn long videos into vertical Shorts automatically!")

st.divider()

# VIDEO URL
st.subheader("🔗 YouTube Video URL")

video_url = st.text_input(
    "Paste your YouTube video URL",
    placeholder="https://www.youtube.com/watch?v=..."
)

st.caption(
    "URL import is not connected yet. "
    "Use your own or authorized video files for now."
)

st.divider()

# VIDEO UPLOAD
st.subheader("📤 Upload Your Video")

video = st.file_uploader(
    "Choose a video file",
    type=["mp4", "mov", "mkv", "webm"]
)

# SETTINGS
st.divider()
st.subheader("⚙️ AI Shorts Settings")

duration = st.selectbox(
    "Short Video Duration",
    [30, 45, 60],
    index=2
)

max_clips = st.slider(
    "Maximum Number of Shorts",
    1, 10, 5
)

categories = st.multiselect(
    "Select Moments",
    [
        "Funny 😂",
        "Romantic ❤️",
        "Action ⚔️",
        "Emotional 🥺",
        "Shocking 😱",
        "Viral 🔥"
    ],
    default=[
        "Funny 😂",
        "Action ⚔️",
        "Emotional 🥺"
    ]
)

st.info("Output Format: 9:16 Vertical | MP4")

# GENERATE BUTTON
if st.button(
    "✨ Generate AI Shorts",
    use_container_width=True
):

    if video is None:

        if video_url.strip():
            st.warning(
                "YouTube URL import is not connected yet. "
                "Please upload an authorized video file."
            )
        else:
            st.error(
                "Please enter a video URL or upload a video."
            )

    else:

        workdir = tempfile.mkdtemp()

        input_path = os.path.join(
            workdir, "input_video"
        )

        with open(input_path, "wb") as f:
            f.write(video.getbuffer())

        st.info("Checking video...")

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
                    f"Creating Short {i+1} of {total_clips}"
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
                    results.append(output_path)

                progress.progress(
                    (i + 1) / total_clips
                )

            status.empty()

            if results:

                st.session_state["shorts_results"] = results

                st.success(
                    f"Created {len(results)} Shorts successfully!"
                )

            else:

                st.error(
                    "Video processing failed. Try another video."
                )

# RESULTS
if "shorts_results" in st.session_state:

    st.divider()
    st.header("🎬 Your Shorts")

    for index, path in enumerate(
        st.session_state["shorts_results"]
    ):

        st.subheader(f"Short #{index + 1}")

        st.video(path)

        with open(path, "rb") as f:
            video_data = f.read()

        st.download_button(
            "⬇️ Download MP4",
            data=video_data,
            file_name=f"ai_short_{index+1}.mp4",
            mime="video/mp4",
            key=f"download_{index}"
        )

        caption = (
            "Watch this amazing moment! 🔥\n\n"
            "#Shorts #YouTubeShorts #Reels #Viral"
        )

        st.markdown("**Social Media Caption**")
        st.code(caption)

        st.button(
            "📋 Copy Caption",
            key=f"copy_{index}",
            on_click=st.toast,
            args=("Caption ready!",)
        )

st.divider()

st.caption(
    "AI Shorts Generator | Version 3.0"
)
