import time
import json
import os
import requests
import streamlit as st
from openai import OpenAI
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import markdown  # Necessary for the copy button
import pypdf

# --- Assuming get_raw_html exists in your project ---
from extract_html import get_raw_html
# ----------------------------------------------------

# Load variables from .env file
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# 🔹 Initialize OpenAI Client
client = OpenAI(api_key=OPENAI_API_KEY)


# 📄 --- NEW & IMPROVED PDF EXTRACTION FUNCTION --- 📄
# This function is written to handle both local file paths and Streamlit file-like objects.
def extract_text_from_pdf(source):
    """
    Extracts text from a PDF file. The source can be a file path (string)
    or a file-like object (from Streamlit's file_uploader).
    """
    try:
        pdf_reader = pypdf.PdfReader(source)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"❌ Error extracting text from PDF: {e}")
        return None

#
# --- UNCHANGED HELPER FUNCTION ---
#
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
            "Company Name": "String - extract Company Name",
            "Position": "String - Applying position",
            "Salary/Pay_Rate": "" - number or None if it is not provided,
            "Responsibility": [],
            "Requirements": [],
            "Preferred Qualifications": [],
            "Tech Stack": []
        }}
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": extraction_prompt}],
            temperature=0.3
        )

        extracted_data = response.choices[0].message.content.strip()

        if extracted_data.startswith("```json"):
            extracted_data = extracted_data.replace("```json", "").replace("```", "").strip()

        try:
            extracted_data_json = json.loads(extracted_data)
            return extracted_data_json
        except json.JSONDecodeError:
            st.error("❌ JSON Decoding Error: OpenAI response is not valid JSON.")
            return {"raw_response": extracted_data}
    except Exception as e:
        st.error(f"❌ OpenAI API Error: {e}")
        return None

#
# --- UNCHANGED FUNCTION TO GENERATE EMAIL AND RESUME ADVICE ---
#
def generate_email_and_resume_advice(job_data, resume_data):
    """
    Generates a tailored cold email AND provides resume modification advice
    in a single API call, returning a structured JSON object.
    """
    prompt = f"""
    You are an expert career assistant. Your task is to generate two things based on the provided job description and resume:
    1. A professional, skimmable cold email, tailored primarily to the job description.
    2. Actionable advice on how to subtly modify the resume to better align with the job posting.

    **Inputs:**
    - Job Posting: {job_data}
    - My Current Resume: {resume_data}

    **Task 1: Generate the Cold Email**
    - Write a short, professional email expressing interest in the job.
    - **Prioritize tailoring the content to the job description.** Use the resume as a factual basis for experience, but frame it to match the job's needs.
    - Follow the provided email format. Use bullet points for clarity.
    - Use Markdown's double asterisks (`**text**`) to bold key elements for emphasis: **Job Title**, **Company Name**, specific **technical skills**, and **quantifiable metrics**.

    **Email Format to Follow:**
    Hi [Recruiter Name if available],
    I hope you're doing well. I’m reaching out to express my strong interest in the **[Job Title]** opportunity at **[Company Name]**. I’m enthusiastic about the possibility of contributing to your team.
    Here’s a quick overview of how my experience aligns with your needs:
    - [Relevant Experience/Project 1: Frame it to match a responsibility/requirement from the job posting. Include relevant tech.]
    - [Relevant Experience/Project 2: Frame it to match another key requirement. Include relevant tech and quantifiable outcomes if possible.]
    - [Summary of technical proficiency, highlighting skills mentioned in the job description.]
    I am confident that my background in [mention 1-2 key areas from the job description, e.g., 'full-stack development and cloud infrastructure'] makes me a strong candidate.
    I’ve attached my resume for your review and would welcome the opportunity to discuss how my skills can benefit your team.
    Thank you for your time!
    Sincerely,
    [Your Name]

    **Task 2: Generate Resume Modification Advice**
    - Provide a list of specific, actionable suggestions for modifying the resume to better match the job.
    - **Crucial Constraint:** Do NOT invent new projects or work experiences. All suggestions must be based on the existing resume content.
    - Focus on:
        - Rephrasing bullet points to include keywords from the job description.
        - Highlighting or re-ordering skills in the 'Skills' or 'Tech Stack' section to match the job's priorities.
        - Suggesting which projects to emphasize.
    - The advice should be encouraging and easy to follow.

    **Final Output Format:**
    Return a single, valid JSON object with two keys: "email_content" and "resume_advice".
    {{
        "email_content": "The full Markdown text of the generated email goes here.",
        "resume_advice": "The full Markdown text for the resume advice goes here, using bullet points for suggestions."
    }}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            response_format={"type": "json_object"} # Use JSON mode for reliable output
        )

        response_content = response.choices[0].message.content
        response_json = json.loads(response_content)
        
        email = response_json.get("email_content", "Error: Could not generate email.")
        advice = response_json.get("resume_advice", "Error: Could not generate advice.")

        return email, advice

    except Exception as e:
        st.error(f"❌ An error occurred during generation: {e}")
        return None, None

def main_implementation(url, resume_data):
    """
    Main function to fetch job details and generate content.
    Now accepts resume data directly.
    """
    raw_data = get_raw_html(url)
    if not raw_data:
        return "Failed to fetch content from URL.", None

    job_data = extract_job_details_raw_text(raw_data)

    if job_data:
        cold_email, resume_advice = generate_email_and_resume_advice(job_data, resume_data)
        return cold_email, resume_advice
    else:
        return "Failed to extract job details.", "Could not generate advice as job details were not extracted."

#
# --- UNCHANGED FUNCTION FOR THE COPY BUTTON ---
#
def create_copy_button(email_content_markdown):
    """Creates an HTML/JS component for a rich-text copy button."""
    email_html = markdown.markdown(email_content_markdown)
    escaped_html = email_html.replace("`", r"\`")
    component_html = f"""
    <div style="display: flex; justify-content: center; margin-top: 20px;">
        <style>
            #copyBtn {{
                border: 1px solid #777; background-color: #0d1117; color: #fafafa;
                padding: 10px 24px; border-radius: 8px; font-size: 16px; cursor: pointer;
            }}
            #copyBtn:hover {{ background-color: #222; }}
        </style>
        <button id="copyBtn">Copy Email</button>
        <script>
        async function copyHtmlToClipboard() {{
            const htmlContent = `{escaped_html}`;
            try {{
                const blob = new Blob([htmlContent], {{ type: 'text/html' }});
                const clipboardItem = new ClipboardItem({{ 'text/html': blob }});
                await navigator.clipboard.write([clipboardItem]);
                const btn = document.getElementById('copyBtn');
                btn.innerHTML = '✅ Copied!';
                setTimeout(() => {{ btn.innerHTML = 'Copy Email'; }}, 2000);
            }} catch (err) {{
                console.error('Failed to copy: ', err);
            }}
        }}
        document.getElementById('copyBtn').addEventListener('click', copyHtmlToClipboard);
        </script>
    </div>
    </div>
    """
    return component_html

#
# --- STREAMLIT UI UPDATED FOR BOTH OUTPUTS AND RESUME UPLOAD ---
#
st.set_page_config(layout="wide")
st.title("🎯 AI Job Application Assistant")
st.write("Enter a job posting URL to generate a tailored cold email and get advice on how to tune your resume.")

job_url = st.text_input("Job Posting URL", placeholder="e.g., [https://www.linkedin.com/jobs/view/](https://www.linkedin.com/jobs/view/)...")

# --- NEW: Resume Upload Button ---
uploaded_resume = st.file_uploader("Or, upload your own resume (PDF)", type=["pdf"])

if st.button("Generate", type="primary"):
    if job_url:
        with st.spinner("Analyzing job, crafting email, and preparing resume advice..."):
            # --- Conditional logic to get resume data ---
            resume_data = None
            if uploaded_resume:
                # Use the content of the uploaded PDF
                resume_data = extract_text_from_pdf(uploaded_resume)
            else:
                # Use the default resume file
                resume_path = "./resumes/resume.pdf"
                if os.path.exists(resume_path):
                    resume_data = extract_text_from_pdf(resume_path)
                else:
                    st.error("❌ Default resume file not found at './resumes/resume.pdf'. Please upload a resume.")
            
            if resume_data:
                # --- Pass the selected resume data to the main function ---
                cold_email, resume_advice = main_implementation(job_url, resume_data)
                
                if cold_email and resume_advice:
                    st.success("✨ Success! Your email and resume advice are ready.")
                    st.write("---")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.subheader("📧 Email Preview")
                        # Display the formatted email for the user to see
                        with st.container(border=True):
                            st.markdown(cold_email, unsafe_allow_html=True)
                        
                        # Display the custom copy button
                        copy_button_component = create_copy_button(cold_email)
                        st.components.v1.html(copy_button_component, height=50)

                    with col2:
                        st.subheader("💡 Resume Tailoring Suggestions")
                        with st.container(border=True):
                            st.markdown(resume_advice, unsafe_allow_html=True)
                else:
                    st.error("Something went wrong. Please check the URL and try again.")

    else:
        st.warning("Please enter a job URL to begin.")