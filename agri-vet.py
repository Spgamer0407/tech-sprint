

import os
import json
import gradio as gr
from typing import TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END

# --- 1. SETUP API KEY (LOCAL METHOD) ---
# OPTION A: Hardcode it (Easier for testing, but don't share this file)
os.environ["GOOGLE_API_KEY"] = "PASTE_YOUR_GEMINI_API_KEY_HERE"

# OPTION B: Use .env file (Professional way - recommended)
# from dotenv import load_dotenv
# load_dotenv() 

# Check if key is present
if not os.environ.get("GOOGLE_API_KEY"):
    raise ValueError("❌ Error: GOOGLE_API_KEY is missing. Please set it in line 15.")

print("✅ API Key Configured. Connecting to Gemini...")

# --- 2. INITIALIZE MODEL ---
try:
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.0-flash",
        temperature=0.2
    )
    print("✅ Model Connected: Gemini 2.0 Flash")
except Exception as e:
    print(f"❌ Connection Error: {e}")

# --- 3. TOOLS & MEMORY ---
MEMORY_FILE = "agri_vet_records.json"

def save_record(animal, condition, diagnosis, diet):
    """Saves consultation to a local JSON file."""
    data = {"history": []}
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r') as f:
            try: data = json.load(f)
            except: pass
    entry = {"animal": animal, "condition": condition, "diagnosis": diagnosis, "diet": diet}
    data["history"].append(entry)
    with open(MEMORY_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_history(animal):
    """Loads the last 3 medical records for context."""
    if not os.path.exists(MEMORY_FILE): return "No past records."
    with open(MEMORY_FILE, 'r') as f:
        data = json.load(f)
    history = [r for r in data.get("history", []) if r['animal'].lower() == animal.lower()]
    return str(history[-3:]) if history else "No specific history found."

@tool
def check_toxicity(food_item: str, animal_type: str) -> str:
    """Checks if a food item is toxic."""
    food = food_item.lower()
    animal = animal_type.lower()
    toxic_db = {
        "dog": ["chocolate", "grapes", "raisins", "onion", "garlic", "xylitol"],
        "cow": ["meat", "plastic", "oleander", "rhododendron"],
        "cat": ["chocolate", "milk", "onion", "lilies"]
    }
    if animal in toxic_db and any(toxin in food for toxin in toxic_db[animal]):
        return f"🚫 DANGER: {food_item} is TOXIC to {animal_type}."
    return f"✅ Safe: {food_item} appears safe."

# --- 4. AGENT NODES ---
class AgentState(TypedDict):
    animal: str
    symptoms: str
    history: str
    diagnosis: str
    diet_plan: str
    schedule: str

def vet_node(state: AgentState):
    print(f"-> Vet Diagnosing {state['animal']}...")
    prompt = f"You are a Vet. Diagnose {state['animal']} with symptoms: {state['symptoms']}. History: {state['history']}."
    response = llm.invoke(prompt)
    return {"diagnosis": response.content}

def nutritionist_node(state: AgentState):
    print("-> Nutritionist Planning Diet...")
    prompt = f"You are a Nutritionist. Create diet for {state['animal']} with diagnosis: {state['diagnosis']}. SAFETY: If Dog, check for chocolate toxicity."
    # Manual tool check for demo
    if "dog" in state['animal'].lower():
        safety = check_toxicity.invoke({"food_item": "Chocolate", "animal_type": "dog"})
        prompt += f" (Safety Tool Result: {safety})"
    response = llm.invoke(prompt)
    return {"diet_plan": response.content}

def scheduler_node(state: AgentState):
    print("-> Scheduler Creating Timeline...")
    prompt = f"You are a Farm Manager. Create a 24h schedule (6AM-10PM) for {state['animal']} based on: {state['diet_plan']}."
    response = llm.invoke(prompt)
    return {"schedule": response.content}

# --- 5. BUILD GRAPH ---
workflow = StateGraph(AgentState)
workflow.add_node("vet", vet_node)
workflow.add_node("nutritionist", nutritionist_node)
workflow.add_node("scheduler", scheduler_node)
workflow.set_entry_point("vet")
workflow.add_edge("vet", "nutritionist")
workflow.add_edge("nutritionist", "scheduler")
workflow.add_edge("scheduler", END)
app = workflow.compile()

# --- 6. USER INTERFACE ---
def agri_vet_process(user_query, history):
    try:
        # Interpreter
        raw = llm.invoke(f"Extract 'Animal' and 'Symptoms' from '{user_query}'. Format: Animal: X | Symptoms: Y").content
        try:
            parts = raw.split("|")
            animal = parts[0].split(":")[1].strip()
            symptoms = parts[1].split(":")[1].strip()
        except:
            animal = "Farm Animal"
            symptoms = user_query
            
        # Run Graph
        past = load_history(animal)
        result = app.invoke({
            "animal": animal, "symptoms": symptoms, "history": past,
            "diagnosis": "", "diet_plan": "", "schedule": ""
        })
        
        save_record(animal, symptoms, result['diagnosis'], result['diet_plan'])
        
        return (
            f"## 🚜 Agri-Vet Report: {animal}\n"
            f"**Symptoms:** {symptoms}\n---\n"
            f"### 🩺 Diagnosis\n{result['diagnosis']}\n\n"
            f"### 🥗 Diet Plan\n{result['diet_plan']}\n\n"
            f"### ⏰ Schedule\n{result['schedule']}"
        )
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# --- 7. LAUNCH ---
if __name__ == "__main__":
    demo = gr.ChatInterface(
        fn=agri_vet_process,
        type="messages",
        title="🚜 Agri-Vet: Desktop Edition",
        description="Running locally on VS Code",
        theme="soft"
    )
    print("🚀 App Launching! Open your browser to http://127.0.0.1:7860")
    demo.launch()