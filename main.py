from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
import json
import os
import random
from pymongo import MongoClient 

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY is missing!")


client = genai.Client(api_key=GEMINI_API_KEY) 


app = FastAPI(title="AI Quiz Builder API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
    expose_headers=["*"],
)

MONGO_URI = "mongodb+srv://rohangupta2134_db_user:vugv3IWwb6BXic4m@quizgenerator.gn4unug.mongodb.net/?retryWrites=true&w=majority&appName=QuizGenerator"
try:
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client["AI_Quiz_App"]
    quizzes_collection = db["quizzes"]
    # Check if connection is successful
    mongo_client.admin.command('ping')
    print("✅ Successfully connected to MongoDB!")
except Exception as e:
    print(f"❌ MongoDB Connection Failed: {e}")

# (Purana quizzes_db = {} ab delete kar diya hai, kyunki ab asli database hai)

# ==========================================
# WebSockets Connection Manager (Slightly updated)
# ==========================================
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}
        self.leaderboards: dict[str, dict[str, int]] = {}

    async def connect(self, websocket: WebSocket, room_pin: str):
        await websocket.accept()
        if room_pin not in self.active_connections:
            self.active_connections[room_pin] = []
            self.leaderboards[room_pin] = {}
        self.active_connections[room_pin].append(websocket)

    def disconnect(self, websocket: WebSocket, room_pin: str):
        if room_pin in self.active_connections:
            if websocket in self.active_connections[room_pin]:
                self.active_connections[room_pin].remove(websocket)

    async def broadcast_leaderboard(self, room_pin: str):
        if room_pin in self.active_connections:
            sorted_scores = dict(sorted(self.leaderboards[room_pin].items(), key=lambda item: item[1], reverse=True))
            message = {"type": "leaderboard", "data": sorted_scores}
            # List create ki hai copy() use karke taaki "RuntimeError: dictionary changed size during iteration" na aaye
            for connection in list(self.active_connections[room_pin]): 
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Failed to send to a client: {e}")

    def update_score(self, room_pin: str, player_name: str, score: int):
        self.leaderboards[room_pin][player_name] = score

manager = ConnectionManager()

class QuizRequest(BaseModel):
    topic: str
    timer_value: int 

def generate_quiz_from_ai(topic: str):
    prompt = f"""
    You are an expert quiz generator. Generate a multiple-choice quiz based on this exact request: "{topic}".
    
    CRITICAL INSTRUCTION: If the user specifies a number of questions (e.g., "10 questions on history"), you MUST generate exactly that many questions. If the user does not specify any number, generate exactly 5 questions by default.
    
    The output MUST have a key "quiz" which contains a list of objects.
    Each object should have:
    - "question": The question text
    - "options": A list of exactly 4 string options
    - "answer": The correct option (exact string from the options)
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    return json.loads(response.text)

@app.post("/create-room")
def create_room(request: QuizRequest):
    quiz_data = generate_quiz_from_ai(request.topic)
    room_pin = str(random.randint(1000, 9999))
    
    while quizzes_collection.find_one({"pin": room_pin}):
        room_pin = str(random.randint(1000, 9999))
        
    # NAYA: timer_value ko bhi database mein save kar rahe hain
    quizzes_collection.insert_one({
        "pin": room_pin,
        "quiz_data": quiz_data,
        "timer_seconds": request.timer_value 
    })
    
    return {"status": "success", "room_pin": room_pin}

@app.get("/join-room/{pin}")
def join_room(pin: str):
    quiz_doc = quizzes_collection.find_one({"pin": pin})
    if quiz_doc:
        return {
            "status": "success", 
            "quiz": quiz_doc["quiz_data"],
            "timer_seconds": quiz_doc.get("timer_seconds", 60) # NAYA: Timer value bhej rahe hain
        }
    else:
        raise HTTPException(status_code=404, detail="Invalid PIN!")

@app.websocket("/ws/{pin}/{player_name}")
async def websocket_endpoint(websocket: WebSocket, pin: str, player_name: str):
    await manager.connect(websocket, pin)
    try:
        await manager.broadcast_leaderboard(pin)
        while True:
            data = await websocket.receive_json()
            if data.get("action") == "submit_score":
                score = data.get("score", 0)
                manager.update_score(pin, player_name, score)
                await manager.broadcast_leaderboard(pin)
    except WebSocketDisconnect:
        manager.disconnect(websocket, pin)
        print(f"Player {player_name} disconnected from room {pin}")
