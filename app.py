
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

st.subheader("📤 Upload Your Video")

video = st.file_uploader(
    "Upload your own or authorized video",
    type=["mp4", "mov", "mkv", "webm"]
)

st.subheader("⚙️ Video Settings")

duration = st.selectbox(
    "Each Short Duration",
    [30, 45, 60],
    index=2
)

max_clips = st.slider(
    "Number of Shorts",
    1, 10, 5
)

st.info("Output: MP4 | 9:16 Vertical | 1080 × 1920")

if st.button("✨ Generate Shorts", use_container_width=True):

    if video is None:
        st.error("Please upload a video first.")

    else:
        with st.spinner("Preparing your video..."):

            workdir = tempfile.mkdtemp()

            input_path = os.path.join(workdir, "input_video")
            with open(input_path, "wb") as f:
                f.write(video.getbuffer())

            cap = cv2.VideoCapture(input_path)

            fps = cap.get(cv2.CAP_PROP_FPS)
            frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

            cap.release()

            if not fps or fps <= 0 or frames <= 0:
                st.error("Could not read this video.")
                st.stop()

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
                remaining = total_seconds - start
                clip_duration = min(duration, remaining)

                if clip_duration <= 0:
                    break

                output_path = os.path.join(
                    workdir, f"short_{i+1}.mp4"
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
                    "-movflags", "+faststart",
                    "-pix_fmt", "yuv420p",
                    output_path
                ]

                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0 and os.path.exists(output_path):
                    results.append(output_path)

                progress.progress((i + 1) / total_clips)

            status.empty()

            if results:
                st.session_state["shorts_results"] = results
                st.success(
                    f"Successfully created {len(results)} Shorts!"
                )
            else:
                st.error("Video processing failed. Please try another video.")

if "shorts_results" in st.session_state:

    st.divider()
    st.header("🎬 Your Generated Shorts")

    for index, path in enumerate(
        st.session_state["shorts_results"]
    ):

        st.subheader(f"Short #{index + 1}")

        st.video(path)

        st.download_button(
            "⬇️ Download MP4",
            data=open(path, "rb").read(),
            file_name=f"ai_short_{index+1}.mp4",
            mime="video/mp4",
            key=f"download_{index}"
        )

        st.markdown("**Social Media Caption**")

        caption = (
            f"Watch this amazing moment! 🔥\n\n"
            f"#Shorts #YouTubeShorts #Reels #Viral"
        )

        st.code(caption)

        st.button(
            "📋 Copy caption",
            key=f"caption_{index}",
            on_click=st.toast,
            args=("Caption: " + caption, "success")
        )

st.divider()
st.caption("AI Shorts Generator | Version 2.0")
