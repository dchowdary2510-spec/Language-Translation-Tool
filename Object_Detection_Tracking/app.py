import streamlit as st
import cv2
import tempfile
import pandas as pd
import plotly.express as px
from detector import detect_and_track
from utils import (
    count_objects,
    update_total_counts,
    save_detection_history,
    create_dataframe,
    ensure_output_folder
)

st.set_page_config(
    page_title="Smart Object Detection & Tracking",
    page_icon="🎯",
    layout="wide"
)

ensure_output_folder()

st.title("🎯 Smart Object Detection & Tracking System")

st.markdown("""
Upload a video or use your webcam to detect and track objects in real time.
""")

# Sidebar
st.sidebar.header("⚙️ Settings")

confidence = st.sidebar.slider(
    "Confidence Threshold",
    min_value=0.1,
    max_value=1.0,
    value=0.3,
    step=0.05
)
from detector import model

available_classes = list(model.names.values())

selected_classes = st.sidebar.multiselect(
    "Select Classes",
    available_classes,
    default=[
        "person",
        "cell phone",
        "book",
        "mouse",
        "laptop"
    ]
)
mode = st.sidebar.radio(
    "Choose Input",
    ["Upload Video", "Webcam"]
)

total_counts = {}

# ==========================
# VIDEO UPLOAD MODE
# ==========================

if mode == "Upload Video":

    uploaded_file = st.file_uploader(
        "Upload Video",
        type=["mp4", "avi", "mov"]
    )

    if uploaded_file is not None:

        temp_file = tempfile.NamedTemporaryFile(
            delete=False
        )

        temp_file.write(
            uploaded_file.read()
        )

        cap = cv2.VideoCapture(
            temp_file.name
        )

        fps = cap.get(
            cv2.CAP_PROP_FPS
        )

        output_path = (
            "outputs/processed_video.mp4"
        )

        fourcc = cv2.VideoWriter_fourcc(
            *"mp4v"
        )

        # Output size matches resized frames
        out = cv2.VideoWriter(
            output_path,
            fourcc,
            fps,
            (640, 480)
        )

        frame_placeholder = st.empty()

        progress_bar = st.progress(0)

        total_frames = int(
            cap.get(
                cv2.CAP_PROP_FRAME_COUNT
            )
        )

        frame_number = 0

        while cap.isOpened():

            success, frame = cap.read()

            if not success:
                break

            frame_number += 1

            # Process every 3rd frame
            if frame_number % 3 != 0:
                continue

            # Resize for faster detection
            frame = cv2.resize(
                frame,
                (640, 480)
            )

            annotated_frame, results = detect_and_track(
                frame,
                confidence,
                selected_classes
            )

            current_counts = count_objects(
                results
            )

            total_counts = update_total_counts(
                current_counts,
                total_counts
            )

            frame_rgb = cv2.cvtColor(
                annotated_frame,
                cv2.COLOR_BGR2RGB
            )

            frame_placeholder.image(
                frame_rgb,
                channels="RGB"
            )

            out.write(
                annotated_frame
            )

            progress_bar.progress(
                min(
                    frame_number /
                    total_frames,
                    1.0
                )
            )

        cap.release()
        out.release()

        st.success(
            "✅ Video Processing Complete"
        )

        # Analytics

        if total_counts:

            st.subheader(
                "📊 Detection Statistics"
            )

            df = create_dataframe(
                total_counts
            )

            st.dataframe(df)

            fig = px.bar(
                df,
                x="Object",
                y="Count",
                title="Detected Objects"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            save_detection_history(
                total_counts
            )

            with open(
                output_path,
                "rb"
            ) as video_file:

                st.download_button(
                    label="📥 Download Processed Video",
                    data=video_file,
                    file_name="processed_video.mp4",
                    mime="video/mp4"
                )

# ==========================
# WEBCAM MODE
# ==========================

elif mode == "Webcam":

    run = st.checkbox(
        "Start Webcam"
    )

    frame_placeholder = st.empty()

    cap = cv2.VideoCapture(0)

    while run:

        success, frame = cap.read()

        if not success:
            st.error(
                "Unable to access webcam."
            )
            break

        annotated_frame, results = detect_and_track(
            frame,
            confidence,
            selected_classes
        )

        current_counts = count_objects(
            results
        )

        total_counts = update_total_counts(
            current_counts,
            total_counts
        )

        frame_rgb = cv2.cvtColor(
            annotated_frame,
            cv2.COLOR_BGR2RGB
        )

        frame_placeholder.image(
            frame_rgb,
            channels="RGB"
        )

    cap.release()

    if total_counts:

        st.subheader(
            "📊 Live Detection Statistics"
        )

        df = create_dataframe(
            total_counts
        )

        st.dataframe(df)

        fig = px.bar(
            df,
            x="Object",
            y="Count",
            title="Detected Objects"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        save_detection_history(
            total_counts
        )

st.markdown("---")
st.markdown(
    "Built with ❤️ using Streamlit, OpenCV and YOLOv8"
)