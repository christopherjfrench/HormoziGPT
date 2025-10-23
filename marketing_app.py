import os
import streamlit as st
from typing import Dict, Any
import openai
import json

# Set API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

st.title("AI Marketing Planner")

# Initialize session state for storing user information
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}

# Define a function to generate a 90-day marketing plan using OpenAI function calling

def generate_90_day_plan(user_info: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a 90-day marketing plan based on user information."""
    functions = [
        {
            "name": "generate_90_day_plan",
            "description": "Generate a 90-day marketing plan given ICP, product description, business stage, customer reviews and goals",
            "parameters": {
                "type": "object",
                "properties": {
                    "icp": {"type": "string"},
                    "product": {"type": "string"},
                    "stage": {"type": "string"},
                    "reviews": {"type": "string"},
                    "goals": {"type": "string"},
                },
                "required": ["icp", "product", "stage", "goals"]
            }
        }
    ]
    messages = [
        {"role": "system", "content": "You are a helpful marketing assistant that creates comprehensive 90-day marketing plans."},
        {"role": "user", "content": f"Create a 90-day marketing plan for this business.\nICP: {user_info['icp']}\nProduct: {user_info['product']}\nStage: {user_info['stage']}\nReviews: {user_info['reviews']}\nGoals: {user_info['goals']}"},
    ]
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-0613",
            messages=messages,
            functions=functions,
            function_call={"name": "generate_90_day_plan"},
        )
        # Parse the function call arguments returned by the model
        plan_args = response["choices"][0]["message"]["function_call"]["arguments"]
        plan = json.loads(plan_args)
    except Exception as e:
        plan = {"error": str(e)}
    return plan

# Streamlit form to collect user information
with st.form("user_info_form"):
    icp = st.text_area("Describe your ideal customer profile (ICP)", "")
    product = st.text_area("Describe your product or service", "")
    stage = st.selectbox("What stage is your business in?", ["Start-up", "Scaling", "Mature"])
    reviews = st.text_area("Provide any customer reviews or social proof", "")
    goals = st.text_area("What are your goals for the next 90 days? (e.g., leads, revenue)", "")
    submitted = st.form_submit_button("Generate Plan")
    if submitted:
        st.session_state.user_info = {"icp": icp, "product": product, "stage": stage, "reviews": reviews, "goals": goals}
        st.success("Information saved. Generating plan ...")

# Display the 90-day marketing plan once the information has been submitted
if st.session_state.user_info:
    st.header("90-Day Marketing Plan")
    plan = generate_90_day_plan(st.session_state.user_info)
    if "error" in plan:
        st.error(plan["error"])
    else:
        st.write(plan)
