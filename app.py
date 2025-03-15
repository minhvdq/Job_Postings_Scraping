import time
import json
import os
import requests
import streamlit as st
from openai import OpenAI
from bs4 import BeautifulSoup
from extract_html import get_raw_html
from dotenv import load_dotenv
from extract_pdf import extract_text_from_pdf

# Load variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 🔹 Initialize OpenAI Client
client = OpenAI(api_key=OPENAI_API_KEY)

def extract_job_details_raw_text(raw_text):
    try:
        if not raw_text:
            st.error("❌ OpenAI could not extract a valid job description.")
            return None

        extraction_prompt = f"""
        Extract the key job details: Company Name, Position, Salary or Pay Rate, Responsibilities, Requirements, 
        Qualifications, Preferred Qualifications (if available), and Tech Stack from the following job posting:

        {raw_text}

        Return the output in valid JSON format:
        {{
            "Company Name": String - extract Company Name,
            "Position": String - Applying position,
            "Salary/Pay_Rate": "" - number or None if it is not provided,
            "Responsibility": [...],
            "Requirements": [...],
            "Preferred Qualifications": [...],
            "Tech Stack": [...]
        }}
        """

        # 🔹 Call OpenAI to Extract Structured Data
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": extraction_prompt}],
            temperature=0.3
        )

        extracted_data = response.choices[0].message.content.strip()

        if extracted_data.startswith("```json"):
            extracted_data = extracted_data.replace("```json", "").replace("```", "").strip()

        # 🔹 Convert OpenAI response to JSON
        try:
            extracted_data_json = json.loads(extracted_data)
            return extracted_data_json
        except json.JSONDecodeError:
            st.error("❌ JSON Decoding Error: OpenAI response is not valid JSON.")
            return {"raw_response": extracted_data}
    except Exception as e:
        st.error(f"❌ OpenAI API Error: {e}")
        return None

def generate_email(job_data, resume_data):
    extraction_prompt = f"""
    Write a short, polished, and skimmable cold email expressing my interest in a job I applied for. 
    The email should have three concise paragraphs:

    1️⃣ A warm opening stating that I recently applied for the role and expressing enthusiasm for the opportunity.  
    2️⃣ A brief highlight of my relevant skills and experience that make me a strong fit.  
    3️⃣ A closing sentence politely requesting to schedule a call to discuss further.  

    **Job Posting:** {job_data}  
    **My Resume:** {resume_data}  

    Keep the tone professional yet friendly, making it easy for the recruiter to skim quickly while still leaving a strong impression. Avoid unnecessary details or long sentences.
    """

    # 🔹 Call OpenAI API to generate the email
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": extraction_prompt}],
        temperature=0.3
    )

    # Extract and return the response
    return response.choices[0].message.content.strip()

def main_implementation(url):
    resume_path = "./resumes/Minh_Vu.pdf"
    resume_data = extract_text_from_pdf(resume_path)

    # Extract raw HTML job data
    raw_data = get_raw_html(url)
    job_data = extract_job_details_raw_text(raw_data)

    if job_data:
        cold_email = generate_email(job_data, resume_data)
        return cold_email
    else:
        return "Failed to extract job details."

# 🔹 Streamlit UI
st.title("Cold Email Generator for Job Applications")

st.write("Enter the job posting URL below and get a well-crafted cold email.")

job_url = st.text_input("Job Posting URL", placeholder="Enter job URL here...")

if st.button("Generate Email"):
    if job_url:
        with st.spinner("Extracting job details and generating email..."):
            cold_email = main_implementation(job_url)
            st.success("Cold Email Generated!")
            st.text_area("Generated Email", cold_email, height=200)
    else:
        st.error("Please enter a valid job URL.")
