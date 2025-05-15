# Job Application Cold Email Generator

A Streamlit web application that helps job seekers generate personalized cold emails for job applications. The application analyzes job postings and your resume to create tailored, professional cold emails that highlight your relevant experience and skills.

## Features


- Extracts job details from job posting URLs
- Analyzes your resume to match relevant experience
- Generates personalized cold emails using GPT-4
- User-friendly web interface built with Streamlit

## Prerequisites

- Python 3.x
- OpenAI API key
- LinkedIn account credentials

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd crawl-project
```

2. Install the required dependencies:
```bash
pip install -r requirement.txt
```

3. Create a `.env` file in the root directory with the following credentials:
```
OPENAI_API_KEY=your_api_key_here
LINKEDIN_EMAIL=your_linkedin_email
LINKEDIN_PASSWORD=your_linkedin_password
COOKIES_PATH="linkedin_cookies.pkl"
```

4. Place your resume in the `resumes` directory:
   - Rename your resume file to `resume.pdf`
   - Or update the resume path in `app.py` to match your resume's filename

## Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the provided local URL (typically http://localhost:8501)

3. Enter the job posting URL in the input field

4. Click "Generate Email" to create a personalized cold email

## Project Structure

- `app.py` - Main Streamlit application
- `extract_html.py` - HTML extraction utilities
- `extract_pdf.py` - PDF resume parsing
- `resumes/` - Directory for storing resume files
- `requirement.txt` - Project dependencies

## Dependencies

- openai
- streamlit
- BeautifulSoup
- selenium

## License

[Add your license information here]
