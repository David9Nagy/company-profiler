from flask import Flask, render_template, request
import requests
import openai
import os

app = Flask(__name__)

# Load API keys from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CUSTOM_SEARCH_ENGINE_ID = os.getenv("CUSTOM_SEARCH_ENGINE_ID")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_info', methods=['POST'])
def get_info():
    company_name = request.form['company_name']
    # Step 4: Fetch data from Google Custom Search API
    search_results = google_search(company_name)
    # Step 5: Process the JSON data
    processed_data = process_search_results(search_results)
    # Step 6: Generate report using GPT-3
    report = generate_report(company_name, processed_data)
    return render_template('result.html', company_name=company_name, report=report)

def google_search(query):
    url = 'https://www.googleapis.com/customsearch/v1'
    params = {
        'key': GOOGLE_API_KEY,
        'cx': CUSTOM_SEARCH_ENGINE_ID,
        'q': query,
        'num': 5  # Number of results to return
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        return {}

def process_search_results(results):
    items = results.get('items', [])
    info = ''
    for item in items:
        title = item.get('title', '')
        snippet = item.get('snippet', '')
        link = item.get('link', '')
        info += f"Title: {title}\nSnippet: {snippet}\nLink: {link}\n\n"
    return info

def generate_report(company_name, info):
    prompt = f"""
    Generate a comprehensive report about {company_name} using the information below.

    Information:
    {info}

    The report should cover:
    - Overview of the company
    - Products and services
    - Financial performance
    - Recent news and developments
    - Any other relevant publicly available information

    Present the information in a clear and organized manner.
    """
    try:
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',  # or 'gpt-4' if you have access
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates company reports."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1024,
            temperature=0.7,
        )
        report = response.choices[0].message.content.strip()
        return report.replace('\n', '<br>')
    except Exception as e:
        # Log the exception and return the error message
        error_message = f"OpenAI API Error: {str(e)}"
        print(error_message)
        return error_message

if __name__ == '__main__':
    app.run(debug=True)