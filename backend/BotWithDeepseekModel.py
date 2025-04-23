from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Groq client with API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = groq.Client(api_key=GROQ_API_KEY)


# MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
MODEL = "deepseek-r1-distill-llama-70b"
# MODEL = "llama-3.3-70b-versatile"  # Use the latest model

# System prompt to guide the model to act as a DevOps engineer assistant
SYSTEM_PROMPT = """
You are a highly knowledgeable DevOps engineer assistant. You can help with:
- CI/CD pipelines and tools (Jenkins, GitHub Actions, GitLab CI)
- Infrastructure as Code (Terraform, CloudFormation, Ansible)
- Container orchestration (Kubernetes, Docker Swarm)
- Cloud platforms (AWS, Azure, GCP)
- Monitoring and logging (Prometheus, Grafana, ELK stack)
- Automation scripts and best practices
- DevSecOps principles and implementation
- Site Reliability Engineering concepts

Provide concise, practical advice with code examples when appropriate.
"""

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = data.get('messages', [])
        
        # Ensure the system prompt is included
        if messages and messages[0].get('role') != 'system':
            messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
        
        # Call the Groq API
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1024
        )
        
        return jsonify({
            'response': response.choices[0].message.content,
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
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)