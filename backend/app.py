from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import groq
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Groq client with API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = groq.Client(api_key=GROQ_API_KEY)

# MODEL = "deepseek-r1-distill-llama-70b"
MODEL = "llama-3.3-70b-versatile"  # Using LLaMA 3.3 for better performance

# System prompt focused exclusively on Azure DevOps
AZURE_SYSTEM_PROMPT = """
You are a highly specialized Azure DevOps engineer assistant. You provide expert guidance only on Azure-related topics including:

- Azure DevOps Services (Boards, Repos, Pipelines, Test Plans, Artifacts)
- Azure infrastructure management
- Azure Resource Manager (ARM) templates
- Azure Kubernetes Service (AKS)
- Azure Container Registry and container solutions
- Azure Monitor, Log Analytics, and Application Insights
- Azure Policy and Governance
- Azure Security Center and security best practices
- Azure Automation and Functions
- Azure CI/CD pipelines and integration
- Azure Virtual Networks and networking solutions
- Azure Terraform and Infrastructure as Code

When answering, refer to the latest Azure documentation provided to you. Provide concise, accurate answers with code examples when appropriate. Your advice should follow Azure best practices and recommended patterns.
"""

# Function to fetch relevant Azure documentation
def fetch_azure_docs(query):
    try:
        # Use Microsoft Learn's Azure documentation search
        search_url = f"https://learn.microsoft.com/api/search?search={query}&locale=en-us&%24filter=category%20eq%20%27Documentation%27&scope=Azure"
        response = requests.get(search_url)
        data = response.json()
        print(data)  # Debugging line to check the response structure
        
        results = []
        if 'results' in data:
            for item in data['results'][:3]:  # Take top 3 results
                title = item.get('title', '')
                url = item.get('url', '')
                description = item.get('description', '')
                
                # Get detailed content if URL is available
                content = ""
                if url:
                    try:
                        page_response = requests.get(url)
                        soup = BeautifulSoup(page_response.text, 'html.parser')
                        # Extract main content from Microsoft Learn pages
                        main_content = soup.find('div', {'id': 'main'})
                        if main_content:
                            # Extract text from paragraphs and code blocks
                            paragraphs = main_content.find_all(['p', 'pre', 'code', 'h1', 'h2', 'h3'])
                            content = "\n".join([p.get_text().strip() for p in paragraphs])
                    except:
                        pass
                
                results.append({
                    "title": title,
                    "url": url,
                    "description": description,
                    "content": content[:1000]  # Limit content length
                })
        
        return results
    except Exception as e:
        print(f"Error fetching Azure docs: {str(e)}")
        return []

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = data.get('messages', [])
        query = messages[-1].get('content', '') if messages else ''
        
        # Ensure the Azure-specific system prompt is included
        if messages and messages[0].get('role') != 'system':
            messages.insert(0, {"role": "system", "content": AZURE_SYSTEM_PROMPT})
        
        # Fetch relevant Azure documentation
        azure_docs = fetch_azure_docs(query)
        
        # Add documentation context to the system prompt
        if azure_docs:
            docs_context = "\n\nHere is relevant Azure documentation to help answer this query:\n\n"
            for i, doc in enumerate(azure_docs):
                docs_context += f"Document {i+1}: {doc['title']}\n"
                docs_context += f"URL: {doc['url']}\n"
                if doc['content']:
                    docs_context += f"Content: {doc['content']}\n\n"
                else:
                    docs_context += f"Description: {doc['description']}\n\n"
            
            # Update system message with documentation
            if messages[0]['role'] == 'system':
                messages[0]['content'] = AZURE_SYSTEM_PROMPT + docs_context
            else:
                messages.insert(0, {"role": "system", "content": AZURE_SYSTEM_PROMPT + docs_context})
        
        # Call the Groq API
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.5,  # Lower temperature for more focused responses
            max_tokens=1500
        )
        
        # Include sources of information in the response
        sources = []
        if azure_docs:
            sources = [{"title": doc["title"], "url": doc["url"]} for doc in azure_docs]
        
        return jsonify({
            'response': response.choices[0].message.content,
            'sources': sources,
            'usage': {
                'prompt_tokens': response.usage.prompt_tokens,
                'completion_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'focus': 'Azure DevOps'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)