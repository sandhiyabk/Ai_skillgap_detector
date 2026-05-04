import json
import requests
from huggingface_hub import InferenceClient
from src.config import HF_TOKEN, MISTRAL_MODEL

class LLMEngine:
    def __init__(self):
        self.client = InferenceClient(model=MISTRAL_MODEL, token=HF_TOKEN)

    def analyze_gap(self, task, struggle, context_records):
        """Analyze the skill gap using Mistral-7B with structured JSON output."""
        context_str = json.dumps(context_records, indent=2)
        
        prompt = f"""
        You are an expert Interior Design Consultant. Analyze the following task and struggle to identify the specific skill gap.
        
        ### USER TASK:
        {task}
        
        ### USER STRUGGLE:
        {struggle}
        
        ### SIMILAR EXAMPLES FROM KNOWLEDGE BASE:
        {context_str}
        
        ### INSTRUCTIONS:
        Return a JSON object with the following structure. Do not include any other text or markdown formatting.
        {{
          "skill_gap": "specific technical concept",
          "domain": "one of: Design Software / Client Communication / Material Knowledge / Space Planning / Lighting Design / Project Management",
          "severity": "High / Medium / Low",
          "confidence": 0.0 to 1.0,
          "explanation": "2-3 sentences connecting gap to the task",
          "workflow_example": "step-by-step code or process example",
          "resource_link": "real official documentation URL"
        }}
        """
        
        try:
            response = self.client.text_generation(prompt, max_new_tokens=1000, temperature=0.1)
            # Find the JSON block in the response
            start = response.find('{')
            end = response.rfind('}') + 1
            json_str = response[start:end]
            return json.loads(json_str)
        except Exception as e:
            print(f"Error in LLM analysis: {e}")
            return None

    def match_jd(self, jd_text, user_skills):
        """Match a job description against user skills and identify gaps."""
        prompt = f"""
        You are an expert recruiter in the Interior Design industry. 
        Analyze the following Job Description and compare it with the user's current skills.
        
        ### JOB DESCRIPTION:
        {jd_text}
        
        ### USER SKILLS:
        {user_skills}
        
        ### INSTRUCTIONS:
        Identify the top 3-5 skill gaps. For each gap, provide:
        1. Skill Name
        2. Severity (High / Medium / Low)
        3. Recommendation (How to learn it)
        
        Return a JSON list of objects:
        [
          {{
            "skill": "skill name",
            "severity": "High / Medium / Low",
            "recommendation": "learning recommendation"
          }},
          ...
        ]
        """
        
        try:
            response = self.client.text_generation(prompt, max_new_tokens=1000, temperature=0.1)
            start = response.find('[')
            end = response.rfind(']') + 1
            json_str = response[start:end]
            return json.loads(json_str)
        except Exception as e:
            print(f"Error in JD matching: {e}")
            return None
