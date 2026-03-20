from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import math
import json
import os
from dotenv import load_dotenv
from twilio.rest import Client

# Load environment variables
load_dotenv()

app = FastAPI()

# WebSocket Security
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Initialize Twilio Client
twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    try:
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        print("✅ Twilio client initialized successfully.")
    except Exception as e:
        print(f"❌ Twilio Init Failed: {e}")
else:
    print("⚠️ Twilio credentials missing from environment variables.")

# Health Check
@app.get("/")
async def health_check():
    return {"status": "Last Hope Server Running"}

# The Data Models
class SOSSignal(BaseModel):
    lat: float
    lng: float
    user_id: str
    user_name: Optional[str] = "Unknown User"
    timestamp: str
    type: str  # 'CRASH' | 'MANUAL'
    contacts: Optional[List[str]] = []

class SOSPayload(BaseModel):
    user_name: str
    latitude: float
    longitude: float
    medical_info: Optional[str] = "No medical info provided."
    contacts: List[str]

# Active Incidents
active_incidents = []
connected_clients: List[WebSocket] = []

@app.post("/api/v1/sos-trigger")
async def trigger_sos(payload: SOSPayload):
    if not twilio_client:
        return {"status": "error", "message": "Twilio client not configured"}

    map_link = f"http://maps.google.com/?q={payload.latitude},{payload.longitude}"
    
    success_count = 0
    failures = []

    for contact in payload.contacts:
        message_body = f"URGENT SOS! {payload.user_name} detected a severe crash. Location: {map_link}. Medical: {payload.medical_info}. Sent via Last Hope Cloud Backup."
        try:
            message = twilio_client.messages.create(
                body=message_body,
                from_=TWILIO_PHONE_NUMBER,
                to=contact
            )
            print(f"✅ Twilio SMS sent to {contact}: {message.sid}")
            success_count += 1
        except Exception as e:
            print(f"❌ Failed to send Twilio SMS to {contact}: {e}")
            failures.append({"contact": contact, "error": str(e)})

    return {
        "status": "success",
        "message": f"Alerts processed. Success: {success_count}, Failed: {len(failures)}",
        "failures": failures
    }

@app.websocket("/ws/emergency")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                packet = json.loads(data)
                sos_signal = SOSSignal(**packet)
                incident = process_sos_signal(sos_signal)
                
                # Broadcast
                response = {
                    "event": "NEW_INCIDENT",
                    "incident": incident
                }
                for client in connected_clients:
                    await client.send_json(response)

                # TRIGGER TWILIO SMS (If CRASH)
                if sos_signal.type == "CRASH" or sos_signal.type == "MANUAL":
                     map_link = f"https://maps.google.com/?q={sos_signal.lat},{sos_signal.lng}"
                     send_twilio_alert(sos_signal.user_name, map_link, sos_signal.contacts)
                    
            except Exception as e:
                print(f"Error processing packet: {e}")
                
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

def send_twilio_alert(user_name, location_link, contacts):
    if not twilio_client:
        print("Twilio client not initialized.")
        return

    if not contacts:
        print("No contacts to message.")
        return

    message_body = f"URGENT: {user_name} crashed! Location: {location_link}. Sent by Last Hope Server."

    for contact in contacts:
        try:
            message = twilio_client.messages.create(
                body=message_body,
                from_=TWILIO_PHONE_NUMBER,
                to=contact
            )
            print(f"Twilio SMS sent to {contact}: {message.sid}")
        except Exception as e:
            print(f"Failed to send Twilio SMS to {contact}: {e}")

def process_sos_signal(signal: SOSSignal):
    # Mass Casualty Logic
    for incident in active_incidents:
        dist = haversine_distance(signal.lat, signal.lng, incident['lat'], incident['lng'])
        if dist < 50: # meters
            incident['users'].append(signal.user_id)
            print(f"User {signal.user_id} added to existing incident {incident['id']}")
            return incident

    # New Incident
    new_incident = {
        'id': f"inc_{len(active_incidents) + 1}",
        'lat': signal.lat,
        'lng': signal.lng,
        'users': [signal.user_id],
        'type': signal.type,
        'timestamp': signal.timestamp
    }
    active_incidents.append(new_incident)
    print(f"New Incident created: {new_incident['id']}")
    return new_incident

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000 
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0) ** 2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
