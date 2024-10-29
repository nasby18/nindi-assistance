from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from pydantic import BaseModel

# Hugging Face API configuration
HF_API_KEY = "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"
headers = {"Authorization": f"Bearer {HF_API_KEY}"}
url = "https://api-inference.huggingface.co/models/EleutherAI/gpt-neo-1.3B"

# Predefined question-answer dictionary for common IoT questions
predefined_answers = {
    "What is IoT?": (
        "IoT, or the Internet of Things, refers to a network of physical devices embedded with sensors, software, "
        "and other technologies to connect and exchange data with other devices and systems over the internet. "
        "Examples include smart home devices like thermostats, wearable health monitors, and industrial machines."
    ),
    "What are the main components of IoT?": (
        "The main components of IoT include:\n"
        "- **Sensors and Devices**: These collect data from the environment, such as temperature or motion sensors.\n"
        "- **Connectivity**: IoT devices connect to each other and to the cloud via various communication methods, like Wi-Fi, Bluetooth, or cellular networks.\n"
        "- **Data Processing**: This involves analyzing collected data to derive meaningful insights, often done in the cloud or on the device.\n"
        "- **User Interface**: This allows users to interact with IoT systems, typically through mobile apps or web applications."
    ),
    # More predefined answers...
}

# Initialize FastAPI app
app = FastAPI()

# Configure CORS to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://nindi-assistance.onrender.com"],  # Explicitly set the origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the IoT Chatbot API!"}

# Favicon handler to prevent 404 errors
@app.get("/favicon.ico")
def favicon():
    return {"message": "No favicon available"}

# Define the request model
class ChatRequest(BaseModel):
    question: str

# Helper function to get a response from either predefined answers or GPT model
def get_chatbot_response(input_text):
    # Check for predefined answer
    if input_text in predefined_answers:
        return predefined_answers[input_text]

    # If no predefined answer, fall back to the model with GPT prompt
    prompt = f"Explain in detail: {input_text}. Describe its components, applications, and give examples if possible."
    response = requests.post(url, headers=headers, json={"inputs": prompt})
    response_data = response.json()

    # Extract and return the generated answer
    if isinstance(response_data, list) and "generated_text" in response_data[0]:
        return response_data[0]["generated_text"]
    else:
        return "I'm not sure how to respond."

# Endpoint to handle chatbot requests
@app.post("/chatbot")
def chatbot_endpoint(request: ChatRequest):
    try:
        # Fetch response for the question
        answer = get_chatbot_response(request.question)
        return {"answer": answer}
    except Exception as e:
        # Return error details if any issue occurs
        raise HTTPException(status_code=500, detail=str(e))
