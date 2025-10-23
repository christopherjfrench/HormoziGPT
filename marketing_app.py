import os
import streamlit as st
from typing import Dict, Any
import openai
import json

# Load API key and model from environment
openai.api_key = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-0613")  # default model; set to gpt-5 if available

st.title("AI Marketing Planner")

# Initialize session state
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}

def generate_90_day_plan(user_info: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a 90-day marketing plan based on detailed user information."""
    functions = [{
        "name": "generate_90_day_plan",
        "description": ("Generate a 90-day marketing plan given a detailed ideal customer profile (ICP), "
                        "product/service description, business stage, customer reviews, goals, "
                        "marketing budget and preferred channels."),
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
            "required": ["icp", "product", "stage", "goals"]
        }
    }]
    messages = [
        {"role": "system", "content": "You are a helpful marketing assistant that creates comprehensive 90-day marketing plans."},
        {"role": "user", "content": (
            f"Create a 90-day marketing plan for this business.\n"
            f"ICP: {user_info['icp']}\n"
            f"Product: {user_info['product']}\n"
            f"Stage: {user_info['stage']}\n"
            f"Reviews: {user_info['reviews']}\n"
            f"Goals: {user_info['goals']}\n"
            f"Budget: {user_info['budget']}\n"
            f"Preferred Channels: {user_info['channels']}"
        )},
    ]
    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=messages,
            functions=functions,
            function_call={"name": "generate_90_day_plan"},
        )
        plan_args = response["choices"][0]["message"]["function_call"]["arguments"]
        plan = json.loads(plan_args)
    except Exception as e:
        plan = {"error": str(e)}
    return plan

with st.form("user_info_form"):
    st.header("Tell us about your business")
    icp = st.text_area("Describe your ideal customer profile (ICP) in detail (demographics, roles, company size, pain points)", "")
    product = st.text_area("Describe your product or service and its unique selling points", "")
    stage = st.selectbox("What stage is your business in?", ["Pre-launch", "Start-up", "Scaling", "Mature"])
    reviews = st.text_area("Provide any customer reviews, testimonials, or case studies (optional)", "")
    goals = st.text_area("What are your specific goals for the next 90 days? (e.g., number of leads, revenue target, brand awareness)", "")
    budget = st.text_input("What is your approximate marketing budget for this period? (e.g., $5,000)", "")
    channels = st.text_area("Preferred marketing channels (e.g., LinkedIn, email, webinars, paid ads)", "")
    submitted = st.form_submit_button("Generate 90-Day Plan")
    if submitted:
        st.session_state.user_info = {
            "icp": icp,
            "product": product,
            "stage": stage,
            "reviews": reviews,
            "goals": goals,
            "budget": budget,
            "channels": channels,
        }
        st.success("Information saved. Generating your 90-day marketing plan...")

if st.session_state.user_info:
    st.header("Your 90-Day Marketing Plan")
    plan = generate_90_day_plan(st.session_state.user_info)
    if "error" in plan:
        st.error(plan["error"])
    else:
        st.write(plan)
