from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
from pydantic import BaseModel
import logging

# Hugging Face API configuration
HF_API_KEY = "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"
headers = {"Authorization": f"Bearer {HF_API_KEY}"}
url = "https://api-inference.huggingface.co/models/EleutherAI/gpt-neo-1.3B"

# Initialize FastAPI app
app = FastAPI()

# Configure CORS to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins temporarily for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define predefined answers in English and Swahili
predefined_answers = {
    "What is IoT?": {
        "english": (
            "IoT, or the Internet of Things, refers to a network of physical devices embedded with sensors, software, "
            "and other technologies to connect and exchange data with other devices and systems over the internet. "
            "Examples include smart home devices like thermostats, wearable health monitors, and industrial machines."
        ),
        "swahili": (
            "IoT, au Mtandao wa Vitu, inahusu mtandao wa vifaa vya kifizikia vilivyo na sensa, programu, "
            "na teknolojia nyingine zinazowezesha kuunganishwa na kubadilishana data kati ya vifaa na mifumo mingine kupitia mtandao. "
            "Mifano ni pamoja na vifaa vya nyumbani vya kisasa kama thermostats, vifaa vya kuvaa vya kufuatilia afya, na mashine za viwandani."
        ),
    },
    "What are the main components of IoT?": {
        "english": (
            "The main components of IoT include:\n"
            "- Sensors and Devices**: These collect data from the environment, such as temperature or motion sensors.\n"
            "- Connectivity: IoT devices connect to each other and to the cloud via various communication methods, like Wi-Fi, Bluetooth, or cellular networks.\n"
            "- Data Processing: This involves analyzing collected data to derive meaningful insights, often done in the cloud or on the device.\n"
            "- User Interface: This allows users to interact with IoT systems, typically through mobile apps or web applications."
        ),
        "swahili": (
            "Vipengele vikuu vya IoT ni pamoja na:\n"
            "- Vihisio na Vifaa: Hivi hukusanya data kutoka kwa mazingira, kama vihisio vya joto au mwendo.\n"
            "- Muunganisho: Vifaa vya IoT huunganishwa kati yao na na wingu kupitia njia mbalimbali za mawasiliano, kama Wi-Fi, Bluetooth, au mtandao wa simu.\n"
            "- Usindikaji wa Data: Hii inahusisha uchambuzi wa data zilizokusanywa ili kupata maarifa muhimu, mara nyingi hufanywa kwenye wingu au kwenye kifaa chenyewe.\n"
            "- Kiolesura cha Mtumiaji: Hii inaruhusu watumiaji kuingiliana na mifumo ya IoT, kawaida kupitia programu za simu au wavuti."
        ),
    },
    "What are some applications of IoT?": {
        "english": (
            "Applications of IoT include:\n"
            "- Smart Homes: IoT devices can control lighting, temperature, and security systems.\n"
            "- Healthcare: Wearable devices monitor patient health in real-time.\n"
            "- Agriculture: Sensors monitor soil quality and crop growth.\n"
            "- Industrial Automation: Machines and equipment are monitored for performance and maintenance needs."
        ),
        "swahili": (
            "Matumizi ya IoT ni pamoja na:\n"
            "- Nyumba za Kisasa: Vifaa vya IoT vinaweza kudhibiti mwanga, joto, na mifumo ya usalama.\n"
            "- Afya: Vifaa vya kuvaa hufuatilia afya ya mgonjwa kwa wakati halisi.\n"
            "- Kilimo: Vihisio hufuatilia ubora wa udongo na ukuaji wa mazao.\n"
            "- Automatiki za Viwanda: Mashine na vifaa hufuatiliwa kwa utendaji na mahitaji ya matengenezo."
        ),
    },
    # Additional questions here...
}

@app.get("/")
def read_root():
    return {"message": "Welcome to the IoT Chatbot API!"}

# Define the request model
class ChatRequest(BaseModel):
    question: str

# Helper function to get a response from either predefined answers or GPT model
def get_chatbot_response(input_text):
    if input_text in predefined_answers:
        return {
            "answer_english": predefined_answers[input_text]["english"],
            "answer_swahili": predefined_answers[input_text]["swahili"]
        }

    # Prompt to get response from GPT model if no predefined answer
    prompt = f"Explain in detail: {input_text}. Describe its components, applications, and give examples if possible."
    try:
        response = requests.post(url, headers=headers, json={"inputs": prompt}, timeout=10)
        response.raise_for_status()  
        response_data = response.json()

        # Process GPT model response
        if isinstance(response_data, list) and "generated_text" in response_data[0]:
            english_response = response_data[0]["generated_text"]
            swahili_response = translate_to_swahili(english_response) 
            return {
                "answer_english": english_response,
                "answer_swahili": swahili_response
            }
        else:
            logger.warning(f"Unexpected response format from GPT model: {response_data}")
            return {
                "answer_english": "I'm not sure how to respond.",
                "answer_swahili": "Samahani, sijaelewa jinsi ya kujibu."
            }
    except requests.RequestException as e:
        logger.error(f"Error connecting to Hugging Face API: {e}")
        return {
            "answer_english": "I'm sorry, there was an error with the server. Please try again later.",
            "answer_swahili": "Samahani, kumekuwa na hitilafu kwa upande wa seva. Tafadhali jaribu tena baadaye."
        }

# Placeholder function to handle English to Swahili translation
def translate_to_swahili(text):
    # Implement translation if needed
    return "Samahani, tafsiri ya Kiswahili haijapatikana kwa sasa."

# Endpoint to handle chatbot requests
@app.post("/chatbot")
def chatbot_endpoint(request: ChatRequest):
    try:
        logger.info(f"Received question: {request.question}")
        answers = get_chatbot_response(request.question)
        return answers
    except Exception as e:
        logger.error(f"Unexpected error in chatbot endpoint: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An error occurred while processing the request.",
                "error": str(e)
            }
        )
