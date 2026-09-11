import requests
import json
import os
from dotenv import load_dotenv
from typing import Optional, List

load_dotenv()

class OllamaLLM:
    """Integration with Ollama for offline LLM capabilities"""
    
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama2")
        self.is_available = self._check_connection()
    
    def _check_connection(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def generate_response(self, prompt: str, temperature: float = 0.7, max_tokens: int = 500) -> str:
        """Generate response from LLaMA"""
        if not self.is_available:
            return self._get_fallback_response(prompt)
        
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "temperature": temperature,
                "top_k": 40,
                "top_p": 0.9,
                "num_predict": max_tokens,
                "stream": False
            }
            
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "").strip()
        except Exception as e:
            print(f"Error calling Ollama: {e}")
            return self._get_fallback_response(prompt)
    
    def analyze_blood_test(self, blood_values: dict) -> dict:
        """Analyze blood test results"""
        prompt = f"""You are a medical expert. Analyze the following blood test results and provide insights:

Blood Test Results:
{json.dumps(blood_values, indent=2)}

Provide:
1. Abnormalities found
2. Possible conditions
3. Recommendations for further testing
4. Severity assessment

Respond in JSON format."""
        
        response = self.generate_response(prompt, temperature=0.3, max_tokens=1000)
        return self._parse_response(response)
    
    def analyze_medical_finding(self, finding_description: str) -> dict:
        """Analyze medical image finding"""
        prompt = f"""You are a radiologist. Based on the following finding description, provide clinical interpretation:

Finding: {finding_description}

Provide:
1. Clinical significance
2. Differential diagnoses
3. Recommendations
4. Follow-up requirements

Respond in JSON format."""
        
        response = self.generate_response(prompt, temperature=0.3, max_tokens=800)
        return self._parse_response(response)
    
    def check_drug_interaction(self, drug1: str, drug2: str) -> dict:
        """Check if two drugs have interactions"""
        prompt = f"""Check for interactions between these drugs:

Drug 1: {drug1}
Drug 2: {drug2}

Provide:
1. Is there an interaction? (yes/no)
2. Type of interaction (major/moderate/minor)
3. Description
4. Recommendation

Respond in JSON format."""
        
        response = self.generate_response(prompt, temperature=0.2, max_tokens=500)
        return self._parse_response(response)
    
    def generate_diagnosis_recommendation(self, patient_info: dict, test_results: dict) -> dict:
        """Generate diagnosis recommendations"""
        prompt = f"""You are a medical doctor. Based on the patient information and test results, provide diagnostic recommendations:

Patient Info:
{json.dumps(patient_info, indent=2)}

Test Results:
{json.dumps(test_results, indent=2)}

Provide:
1. Most likely diagnosis
2. Alternative diagnoses with probabilities
3. Recommended tests
4. Treatment recommendations
5. Specialist referral if needed

Respond in JSON format."""
        
        response = self.generate_response(prompt, temperature=0.4, max_tokens=1500)
        return self._parse_response(response)
    
    def _parse_response(self, response: str) -> dict:
        """Try to parse JSON from response"""
        try:
            # Try to extract JSON from response
            if "{" in response and "}" in response:
                json_start = response.index("{")
                json_end = response.rindex("}") + 1
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
        
        return {"raw_response": response}
    
    def _get_fallback_response(self, prompt: str) -> str:
        """Fallback response when Ollama is not available"""
        return "Ollama service is not available. Please ensure Ollama is running on " + self.base_url

# Singleton instance
_llm_instance = None

def get_llm() -> OllamaLLM:
    """Get LLM instance"""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = OllamaLLM()
    return _llm_instance