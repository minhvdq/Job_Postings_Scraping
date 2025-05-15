import time
import json
import pickle
import os
import requests
from openai import OpenAI
from bs4 import BeautifulSoup
from extract_html import get_raw_html
from dotenv import load_dotenv, dotenv_values 
from extract_pdf import extract_text_from_pdf

# loading variables from .env file
load_dotenv() 

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 🔹 Initialize OpenAI Client
client = OpenAI(api_key=OPENAI_API_KEY)

    
def extract_job_details_raw_text( raw_text ):

    try:

        job_section = raw_text

        if not job_section:
            print("❌ OpenAI could not extract a valid job description.")
            return None
        
        # print(job_section)

        # 🔹 OpenAI Prompt to Extract Job Details
        extraction_prompt = f"""
        Extract the key job Company name, Position, Salary or Pay Rate, Responsibilities, requirements, qualifications, preferred qualificicatiosn can be in seperate section because it is important but not required, and tech stack from the following job section:
        
        {job_section}

        Return the output in valid JSON format:
        {{
            "Company Name": String - extract Company Name,
            "Position": String - Appling position
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
            print("❌ JSON Decoding Error: OpenAI response is not valid JSON.")
            return {"raw_response": extracted_data}
    except Exception as e:
        print(f"❌ OpenAI API Error: {e}")
        return None
    
def generate_email ( job_data, resume_data ):
    extraction_prompt = f"""
    Write a short, polished, and skimmable cold email expressing my interest in a job I applied for. The email should have three concise paragraphs:  

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

def main_implememtation( url ): 
    resume_path = "./resumes/resume.pdf"
    resume_data = extract_text_from_pdf(resume_path)
    raw_data = get_raw_html( url )
    # print(f"Raw data to be: {raw_data}")
    job_data = extract_job_details_raw_text(raw_data)
    print(job_data)

    coldemail = generate_email(job_data, resume_data)
    print(coldemail)

# Example Job Posting Urls
url_linkedin = "https://www.linkedin.com/jobs/search/?alertAction=viewjobs&currentJobId=4182056028&distance=25&f_TPR=a1741690540-&f_WT=2&geoId=103644278&keywords=software%20engineer&origin=JOB_ALERT_IN_APP_NOTIFICATION&originToLandingJobPostings=4182056028&savedSearchId=1736536797&sortBy=R"
url_glassdoor = "https://job-boards.greenhouse.io/genies/jobs/6506648003?utm_source=Simplify&ref=Simplify"
url_workday = "https://chghealthcare.wd1.myworkdayjobs.com/en-US/External/job/Software-Engineering-Intern--Summer-2025_JR102937"

main_implememtation(url_workday)
