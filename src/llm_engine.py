import json
import requests
import os
from src.config import HF_TOKEN, GROQ_API_KEY, LLM_MODEL

class LLMEngine:
    def __init__(self):
        # We prioritize Groq because it is more reliable and faster for free-tier users
        self.use_groq = GROQ_API_KEY is not None
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.groq_headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        self.hf_token = HF_TOKEN
        self.hf_model = "mistralai/Mistral-7B-Instruct-v0.3"

    def _call_groq(self, prompt, max_tokens=1000):
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are an expert Interior Design Consultant. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": max_tokens
        }
        try:
            response = requests.post(self.groq_url, headers=self.groq_headers, json=payload, timeout=20)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            return None
        except Exception as e:
            print(f"Groq Error: {e}")
            return None

    def _call_hf(self, prompt, max_tokens=1000):
        # Fallback to HF if Groq fails or is not configured
        api_url = f"https://api-inference.huggingface.co/models/{self.hf_model}"
        headers = {"Authorization": f"Bearer {self.hf_token}"}
        payload = {
            "inputs": f"[INST] {prompt} [/INST]",
            "parameters": {"max_new_tokens": max_tokens, "temperature": 0.1}
        }
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=20)
            if response.status_code == 200:
                res_json = response.json()
                if isinstance(res_json, list) and len(res_json) > 0:
                    return res_json[0].get("generated_text", "")
                return str(res_json)
            return None
        except Exception as e:
            print(f"HF Error: {e}")
            return None

    def _get_json_response(self, prompt):
        content = None
        if self.use_groq:
            content = self._call_groq(prompt)
        
        if not content and self.hf_token:
            content = self._call_hf(prompt)
            
        if not content:
            return None
            
        try:
            # Find the JSON block in the response
            start = content.find('{')
            end = content.rfind('}') + 1
            if start == -1 or end == 0:
                start = content.find('[')
                end = content.rfind(']') + 1
                
            if start != -1 and end != 0:
                json_str = content[start:end]
                return json.loads(json_str)
            return None
        except Exception as e:
            print(f"JSON Parse Error: {e}")
            return None

    def analyze_gap(self, task, struggle, context_records):
        context_str = json.dumps(context_records, indent=2)
        prompt = f"""
        Analyze the following task and struggle to identify the specific skill gap.
        
        ### USER TASK:
        {task}
        
        ### USER STRUGGLE:
        {struggle}
        
        ### SIMILAR EXAMPLES FROM KNOWLEDGE BASE:
        {context_str}
        
        ### INSTRUCTIONS:
        Return a JSON object with the following structure:
        {{
          "skill_gap": "specific technical concept",
          "domain": "Design Software / Client Communication / Material Knowledge / Space Planning / Lighting Design / Project Management",
          "severity": "High / Medium / Low",
          "confidence": 0.0 to 1.0,
          "explanation": "2-3 sentences connecting gap to the task",
          "workflow_example": "step-by-step code or process example",
          "resource_link": "real official documentation URL"
        }}
        """
        return self._get_json_response(prompt)

    def match_jd(self, jd_text, user_skills):
        prompt = f"""
        Analyze the following Job Description and compare it with the user's current skills.
        
        ### JOB DESCRIPTION:
        {jd_text}
        
        ### USER SKILLS:
        {user_skills}
        
        ### INSTRUCTIONS:
        Identify the top 3-5 skill gaps. Return a JSON list of objects:
        [
          {{
            "skill": "skill name",
            "severity": "High / Medium / Low",
            "recommendation": "learning recommendation"
          }}
        ]
        """
        return self._get_json_response(prompt)
