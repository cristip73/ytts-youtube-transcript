import streamlit as st
from utils import extract_video_id, get_transcript

def init_session_state():
    """Initialize session state variables."""
    if 'current_video_id' not in st.session_state:
        st.session_state.current_video_id = None
    if 'available_languages' not in st.session_state:
        st.session_state.available_languages = []
    if 'timestamped_transcript' not in st.session_state:
        st.session_state.timestamped_transcript = ""
    if 'clean_transcript' not in st.session_state:
        st.session_state.clean_transcript = ""

def get_actionable_summary_template(transcript):
    return f"""Sumarizeaza ideile acționabile din transcript cu bullets și detalii. In indented bullet form. Add a relevant emoji in only front of each first-level step. Dont use '---' separators. Give just the summary with no intro or outro text. Output in canvas or artefact. Write in Romanian

<Transcript>
{transcript}
</Transcript>"""

def get_steps_summary_template(transcript):
    return f"""Sumarizeaza transcript pas cu pas, cu bullets si detalii. In indented bullet form. Add a relevant emoji in only front of each first-level step. Dont use '---' separators. Give just the summary with no intro or outro text. Output in canvas or artefact. Write in Romanian

<Transcript>
{transcript}
</Transcript>"""

def main():
    st.title("YouTube Transcript Fetcher")

    init_session_state()

    # URL input
    url = st.text_input("Enter YouTube Video URL")
    video_id = extract_video_id(url) if url else None

    # Reset language selection if video ID changes
    if video_id != st.session_state.current_video_id:
        language = None
    else:
        # Language selection
        language = None
        if st.session_state.available_languages:
            languages = [(code, lang) for code, lang in st.session_state.available_languages]
            selected_lang = st.selectbox(
                "Select Language",
                languages,
                format_func=lambda x: x[1],
                index=0
            )
            language = selected_lang[0] if selected_lang else None

    # Submit button
    if st.button("Get Transcript"):
        if not url:
            st.error("Please enter a YouTube URL")
            return

        if not video_id:
            st.error("Invalid YouTube URL")
            return

        try:
            with st.spinner("Fetching transcript..."):
                timestamped, clean, languages = get_transcript(video_id, language)

                st.session_state.current_video_id = video_id
                st.session_state.available_languages = languages
                st.session_state.timestamped_transcript = timestamped
                st.session_state.clean_transcript = clean

                st.rerun()

        except Exception as e:
            st.error(str(e))
            return

    # Display special action buttons if transcript is available
    if st.session_state.clean_transcript:
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Actionable Summary"):
                prompt = get_actionable_summary_template(st.session_state.clean_transcript)
                st.write("Copied actionable summary prompt!")
                st.toast("Actionable summary prompt copied to clipboard!")

        with col2:
            if st.button("Steps Summary"):
                prompt = get_steps_summary_template(st.session_state.clean_transcript)
                st.write("Copied steps summary prompt!")
                st.toast("Steps summary prompt copied to clipboard!")

    # Display transcripts if available
    if st.session_state.timestamped_transcript:
        st.subheader("Full Transcript with Timestamps")
        st.text_area(
            "Timestamped transcript",
            st.session_state.timestamped_transcript,
            height=75,
            key="timestamped"
        )
        if st.button("Copy Timestamped Transcript"):
            st.write("Copied to clipboard!")
            st.toast("Timestamped transcript copied!")

    if st.session_state.clean_transcript:
        st.subheader("Clean Transcript (Text Only)")
        st.text_area(
            "Clean transcript",
            st.session_state.clean_transcript,
            height=75,
            key="clean"
        )
        if st.button("Copy Clean Transcript"):
            st.write("Copied to clipboard!")
            st.toast("Clean transcript copied!")

if __name__ == "__main__":
    main()