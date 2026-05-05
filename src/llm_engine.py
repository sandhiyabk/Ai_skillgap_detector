import json
import requests
import os
from src.config import HF_TOKEN, GROQ_API_KEY, LLM_MODEL, MISTRAL_MODEL

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
        self.hf_model = MISTRAL_MODEL or "HuggingFaceH4/zephyr-7b-beta"

    def _call_groq(self, prompt, max_tokens=1000):
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": "You are an expert Interior Design Consultant. You must respond ONLY with a raw JSON string. Do not include any markdown formatting, preamble, or explanation outside the JSON."},
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
        from huggingface_hub import InferenceClient
        try:
            client = InferenceClient(model=self.hf_model, token=self.hf_token)
            
            # Try chat completion first (OpenAI compatible)
            try:
                response = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are an expert Interior Design Consultant. You must respond ONLY with a raw JSON string. Do not include any markdown formatting, preamble, or explanation outside the JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.1,
                )
                return response.choices[0].message.content
            except Exception as chat_err:
                print(f"HF Chat API Error, falling back to text_generation: {chat_err}")
                # Fallback to standard text generation if chat completion is not supported
                formatted_prompt = f"<s>[INST] You are an expert Interior Design Consultant. Respond ONLY with a raw JSON string.\n\n{prompt} [/INST]"
                response = client.text_generation(
                    formatted_prompt,
                    max_new_tokens=max_tokens,
                    temperature=0.1,
                    stop_sequences=["</s>"]
                )
                return response
        except Exception as e:
            print(f"HF Error: {e}")
            return None

    def _get_json_response(self, prompt):
        content = None
        # Try Groq first if available
        if self.use_groq:
            content = self._call_groq(prompt)
        
        # Fallback to HF if Groq failed or not configured
        if (not content or "error" in content.lower()) and self.hf_token:
            content = self._call_hf(prompt)
            
        if not content:
            return None
            
        try:
            # More robust JSON extraction
            # Clean up the content first (sometimes LLMs wrap in markdown code blocks)
            cleaned_content = content.strip()
            if cleaned_content.startswith("```json"):
                cleaned_content = cleaned_content[7:]
            elif cleaned_content.startswith("```"):
                cleaned_content = cleaned_content[3:]
            if cleaned_content.endswith("```"):
                cleaned_content = cleaned_content[:-3]
            cleaned_content = cleaned_content.strip()

            # Try to find the first '{' and last '}'
            start = cleaned_content.find('{')
            end = cleaned_content.rfind('}') + 1
            
            # Or first '[' and last ']'
            start_arr = cleaned_content.find('[')
            end_arr = cleaned_content.rfind(']') + 1

            # Decide which one is more likely to be the root object
            if start != -1 and (start_arr == -1 or start < start_arr):
                target_json = cleaned_content[start:end]
            elif start_arr != -1:
                target_json = cleaned_content[start_arr:end_arr]
            else:
                target_json = cleaned_content

            return json.loads(target_json)
        except Exception as e:
            print(f"JSON Parse Error: {e}")
            # If it's still failing, try one last attempt by removing all non-JSON-like prefix/suffix
            try:
                import re
                # Find something that looks like a JSON object or array
                match = re.search(r'(\{.*\}|\[.*\])', content, re.DOTALL)
                if match:
                    return json.loads(match.group(1))
            except:
                pass
            print(f"Raw content was: {content}")
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
