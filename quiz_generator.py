from google import genai
from google.genai import types
import json

api_key = "AIzaSyB6EDs9NfiK-ML4Kd22HvLQp44-mT77wZQ"
client = genai.Client(api_key=api_key)

def generate_quiz(topic):
    prompt = f"""
    You are an expert quiz generator. Generate a quiz with 3 multiple-choice questions on the topic: {topic}.
    The output MUST have a key "quiz" which contains a list of objects.
    Each object should have:
    - "question": The question text
    - "options": A list of exactly 4 string options
    - "answer": The correct option (exact string from the options)
    """
    
    print(f"Generating quiz for: {topic}...\n")
    
    response = client.models.generate_content(
        model='gemini-2.5-flash', 
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json" 
        )
    )
    
 
    quiz_json = json.loads(response.text)
    
    return quiz_json

# Test
topic = "Linear Control Systems"
result = generate_quiz(topic)

# Result print karke dekhte hain
print(json.dumps(result, indent=4))
