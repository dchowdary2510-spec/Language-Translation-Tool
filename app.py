import streamlit as st
from deep_translator import GoogleTranslator
from gtts import gTTS
import tempfile

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="AI Language Translator",
    page_icon="🌍",
    layout="wide"
)

# ---------------- CSS ----------------

st.markdown("""
<style>
.main {
    padding-top: 1rem;
}

.stButton > button {
    width: 100%;
    border-radius: 12px;
    height: 3em;
}

h1 {
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------

if "history" not in st.session_state:
    st.session_state.history = []

if "source_lang" not in st.session_state:
    st.session_state.source_lang = "english"

if "target_lang" not in st.session_state:
    st.session_state.target_lang = "hindi"

if "translated_text" not in st.session_state:
    st.session_state.translated_text = ""

if "original_text" not in st.session_state:
    st.session_state.original_text = ""


# ---------------- TITLE ----------------

st.title("🌍 AI Language Translator")
st.markdown(
    "<center>Translate text instantly into 100+ languages</center>",
    unsafe_allow_html=True
)

# ---------------- LANGUAGES ----------------

languages = GoogleTranslator().get_supported_languages(as_dict=True)
language_names = sorted(languages.keys())

# ---------------- HISTORY ----------------

with st.sidebar:

    st.header("📜 Translation History")

    st.metric(
        "Total Translations",
        len(st.session_state.history)
    )

    if st.button("🧹 Clear All History"):
        st.session_state.history = []
        st.rerun()

    for index, item in enumerate(
        reversed(st.session_state.history)
    ):

        with st.expander(
            f"{item['source']} ➜ {item['target']}"
        ):

            st.markdown("### 📝 Original")
            st.write(item["original"])

            st.markdown("### 🌍 Translation")
            st.write(item["translated"])

            if st.button(
                "🗑 Delete",
                key=f"delete_{index}"
            ):

                actual_index = (
                    len(st.session_state.history)
                    - index - 1
                )

                st.session_state.history.pop(
                    actual_index
                )

                st.rerun()

# ---------------- LANGUAGE SELECTORS ----------------

col1, col2, col3 = st.columns([5, 1, 5])

with col1:

    source_lang = st.selectbox(
        "Source Language",
        language_names,
        index=language_names.index(
            st.session_state.source_lang
        )
    )

with col2:

    st.write("")
    st.write("")

    if st.button("🔄"):

        temp = st.session_state.source_lang

        st.session_state.source_lang = (
            st.session_state.target_lang
        )

        st.session_state.target_lang = temp

        st.rerun()

with col3:

    target_lang = st.selectbox(
        "Target Language",
        language_names,
        index=language_names.index(
            st.session_state.target_lang
        )
    )

st.session_state.source_lang = source_lang
st.session_state.target_lang = target_lang

# ---------------- MAIN LAYOUT ----------------

left, right = st.columns([1, 1])

with left:

    text = st.text_area(
        "📝 Original Text",
        value=st.session_state.original_text,
        height=150,
        placeholder="Type something here..."
    )

    st.caption(
        f"📊 Characters: {len(text)}"
    )

    if st.button("🌐 Translate"):

        if text.strip():

            translated = GoogleTranslator(
                source="auto",
                target=languages[target_lang]
            ).translate(text)

            st.session_state.original_text = text
            st.session_state.translated_text = translated

            st.session_state.history.append({

                "source": source_lang.title(),
                "target": target_lang.title(),
                "original": text,
                "translated": translated

            })

            st.rerun()

        else:

            st.warning(
                "⚠️ Please enter some text."
            )

    st.markdown("### 🔊 Listen Original")

    if st.session_state.original_text:

        try:

            tts_original = gTTS(
                text=st.session_state.original_text,
                lang="en"
            )

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp3"
            ) as fp:

                tts_original.save(fp.name)

                audio = open(fp.name, "rb")

                st.audio(
                    audio.read(),
                    format="audio/mp3"
                )

        except:

            st.warning(
                "Audio unavailable."
            )

with right:

    st.text_area(
        "🌍 Translation",
        value=st.session_state.translated_text,
        height=150,
        disabled=True
    )

    action1, action2 = st.columns(2)

    with action1:

        if st.session_state.translated_text:

            st.download_button(
                label="📥 Download",
                data=st.session_state.translated_text,
                file_name="translation.txt",
                mime="text/plain"
            )

    with action2:

        if st.session_state.translated_text:

            st.code(
                st.session_state.translated_text
            )

    st.markdown("### 🔊 Listen Translation")

    if st.session_state.translated_text:

        try:

            lang_code = languages[target_lang]

            if "-" in lang_code:
                lang_code = lang_code.split("-")[0]

            tts_translated = gTTS(
                text=st.session_state.translated_text,
                lang=lang_code
            )

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp3"
            ) as fp:

                tts_translated.save(fp.name)

                audio = open(fp.name, "rb")

                st.audio(
                    audio.read(),
                    format="audio/mp3"
                )

        except:

            st.warning(
                "Audio unavailable for this language."
            )