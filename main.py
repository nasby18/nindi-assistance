import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

HF_API_KEY = "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"
headers = {"Authorization": f"Bearer {HF_API_KEY}"}
url = "https://api-inference.huggingface.co/models/EleutherAI/gpt-neo-1.3B"

# Predefined questions and answers about IoT
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
    "How does IoT work?": (
        "IoT works by connecting devices to the internet or to each other to share data. Devices equipped with sensors collect data from the environment, "
        "then transmit that data over a network. Data can be analyzed locally or sent to the cloud for further analysis, allowing users to monitor and control devices remotely."
    ),
    "What are examples of IoT applications?": (
        "Examples of IoT applications include:\n"
        "- **Smart Homes**: Devices like smart thermostats, lights, and security cameras can be controlled remotely.\n"
        "- **Healthcare**: Wearable devices monitor patient health and send data to healthcare providers.\n"
        "- **Agriculture**: Sensors monitor soil moisture and crop health, helping farmers optimize water usage and increase yield.\n"
        "- **Industrial Automation**: IoT devices track machine performance and predict maintenance needs in manufacturing."
    ),
    "What are the benefits of IoT?": (
        "IoT offers numerous benefits, such as:\n"
        "- **Efficiency**: Automating tasks and monitoring devices reduces manual labor and optimizes processes.\n"
        "- **Cost Savings**: Remote monitoring and predictive maintenance can reduce operational costs.\n"
        "- **Data-Driven Insights**: IoT generates data that can be analyzed to improve decision-making.\n"
        "- **Enhanced Quality of Life**: IoT in healthcare and smart homes enhances convenience and safety for individuals."
    ),
    "What are the security risks associated with IoT?": (
        "IoT devices can pose security risks, such as:\n"
        "- **Unauthorized Access**: Weak security protocols can make devices vulnerable to hacking.\n"
        "- **Data Privacy Concerns**: IoT devices collect a lot of personal data, which can be misused if not adequately protected.\n"
        "- **Device Manipulation**: Hackers can potentially take control of IoT devices, impacting safety and privacy.\n"
        "- **Network Vulnerabilities**: If IoT devices are compromised, they can be used to attack other systems on the same network."
    ),
    "How does IoT impact the healthcare industry?": (
        "In healthcare, IoT enables real-time monitoring of patient health, which can improve care and potentially save lives. Wearable devices, for instance, "
        "track metrics like heart rate and blood pressure and send data to healthcare providers for ongoing analysis, which allows for proactive intervention."
    ),
    "What are smart cities, and how does IoT contribute to them?": (
        "Smart cities use IoT technologies to improve urban infrastructure and services. Examples include smart traffic systems that reduce congestion, "
        "environmental sensors that monitor pollution, and energy-efficient buildings. IoT data in smart cities helps create a more sustainable, convenient, and safe environment for citizens."
    ),
    "How does IoT contribute to industrial automation?": (
        "IoT enables industrial automation by monitoring machinery and systems in real-time. Sensors collect data on performance and potential faults, "
        "allowing for predictive maintenance. This reduces downtime, improves productivity, and helps in making data-driven operational decisions."
    ),
    "What role does data analytics play in IoT?": (
        "Data analytics is crucial in IoT, as it processes the large volumes of data generated by IoT devices to derive insights. Analytics can help identify patterns, "
        "optimize operations, and improve decision-making. For example, in agriculture, data analytics can process soil and weather data to help farmers improve crop yield."
    ),
}

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the IoT Chatbot API!"}

# Handle favicon.ico requests to prevent 404 errors
@app.get("/favicon.ico")
def favicon():
    return {"message": "No favicon available"}

class ChatRequest(BaseModel):
    question: str

def get_chatbot_response(input_text):
    # Check for a predefined answer
    if input_text in predefined_answers:
        return predefined_answers[input_text]

    # If no predefined answer, fall back to the model
    prompt = f"Explain in detail: {input_text}. Describe its components, applications, and give examples if possible."
    response = requests.post(url, headers=headers, json={"inputs": prompt})
    response_data = response.json()

    if isinstance(response_data, list) and "generated_text" in response_data[0]:
        return response_data[0]["generated_text"]
    else:
        return "I'm not sure how to respond."

@app.post("/chatbot")
def chatbot_endpoint(request: ChatRequest):
    try:
        answer = get_chatbot_response(request.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
