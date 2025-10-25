import os
import streamlit as st
from typing import Dict, Any
import openai
import json
import tempfile

# Load API key and model
openai.api_key = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-0613")

st.title("AI Marketing Planner with Voice or File Option")

# Initialize session state
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}

# Helper function to transcribe audio using OpenAI Whisper
def transcribe_audio_file(file) -> str:
    if file is not None:
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name
        try:
            transcript = openai.Audio.transcribe("whisper-1", open(tmp_path, "rb"))
            return transcript["text"]
        except Exception as e:
            st.error(f"Error transcribing audio: {e}")
    return ""

# Define function-calling to generate 90-day marketing plan
def generate_90_day_plan(user_info: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a 90-day marketing plan based on detailed user information."""
    functions = [
        {
            "name": "generate_90_day_plan",
            "description": (
                "Generate a 90-day marketing plan given a detailed ideal customer profile (ICP), "
                "product/service description, business stage, customer reviews, goals, "
                "marketing budget and preferred channels."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "icp": {"type": "string"},
                    "product": {"type": "string"},
                    "stage": {"type": "string"},
                    "reviews": {"type": "string"},
                    "goals": {"type": "string"},
                    "budget": {"type": "string"},
                    "channels": {"type": "string"},
                },
                "required": ["icp", "product", "stage", "goals"],
            },
        }
    ]

    messages = [
        {"role": "system", "content": "You are an expert marketing strategist."},
        {
            "role": "user",
            "content": (
                f"Ideal customer profile: {user_info.get('icp','')}\n"
                f"Product/service description: {user_info.get('product','')}\n"
                f"Business stage: {user_info.get('stage','')}\n"
                f"Reviews/testimonials: {user_info.get('reviews','')}\n"
                f"Goals: {user_info.get('goals','')}\n"
                f"Marketing budget: {user_info.get('budget','')}\n"
                f"Preferred channels: {user_info.get('channels','')}\n"
                "Please return a 90-day marketing plan."
            ),
        },
    ]

    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=messages,
            functions=functions,
            function_call={"name": "generate_90_day_plan"},
        )
        arguments = json.loads(
            response["choices"][0]["message"]["function_call"]["arguments"]
        )
        return arguments
    except Exception as e:
        st.error(f"Error generating plan: {e}")
        return {}

# Input method selection (text vs voice)
input_method = st.radio(
    "Select input method for providing answers:",
    ["Text", "Voice"],
)

# Field definitions
fields = [
    ("icp", "Describe your ideal customer profile (e.g., demographics, roles, company size, pain points)"),
    ("product", "Describe your product/service and what makes it unique"),
    ("stage", "Describe your business stage (startup, scaling, mature, etc.)"),
    ("reviews", "Provide any customer reviews/testimonials or case studies"),
    ("goals", "Specify your 90-day goals (e.g., leads, revenue targets)"),
    ("budget", "Marketing budget for the next 90 days (optional)"),
    ("channels", "Preferred marketing channels (e.g., LinkedIn, email, webinars)"),
]

# Collect inputs
for key, prompt in fields:
    if input_method == "Text":
        st.session_state.user_info[key] = st.text_area(
            prompt,
            value=st.session_state.user_info.get(key, ""),
            key=key,
        )
    else:
        # Provide both recording and file upload options
        col1, col2 = st.columns(2)
        with col1:
            audio_data = st.audio_input(f"Record your answer for {prompt}")
        with col2:
            uploaded_file = st.file_uploader(
                f"Or upload an audio file for {prompt}",
                type=["wav", "mp3", "m4a"],
                key=f"{key}_file",
            )

        transcribed_text = ""
        if audio_data is not None:
            transcribed_text = transcribe_audio_file(audio_data)
        elif uploaded_file is not None:
            transcribed_text = transcribe_audio_file(uploaded_file)

        if transcribed_text:
            st.session_state.user_info[key] = transcribed_text
            st.write(f"Transcribed {key}: {transcribed_text}")
        else:
            # keep previous value if any
            st.session_state.user_info[key] = st.session_state.user_info.get(key, "")

# Generate plan button
if st.button("Generate 90-Day Plan"):
    user_info = st.session_state.user_info
    if (
        user_info.get("icp")
        and user_info.get("product")
        and user_info.get("stage")
        and user_info.get("goals")
    ):
        plan = generate_90_day_plan(user_info)
        if plan:
            st.subheader("Generated 90-Day Plan")
            st.json(plan)
    else:
        st.warning("Please provide at least the required fields (ICP, product, stage, goals) before generating the plan.")
