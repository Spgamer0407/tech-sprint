Project Name: Agri-Vet (Autonomous Livestock Hospital)

**CAUTION(run this using kaggle notebook )


1. The Problem Small-scale farmers in rural India often lack immediate access to veterinary doctors. A delay in diagnosis can lead to livestock mortality or reduced yield (milk/meat). Expert advice is often expensive or unavailable at night.

2. The Solution Agri-Vet is an AI-powered triage system that acts as a "Virtual Hospital." It uses a Multi-Agent System to mimic a real medical team. Instead of just chatting, it "thinks" in steps to diagnose, prescribe, and schedule care for farm animals.

3. How It Works (The "Agentic" Workflow) Unlike a simple chatbot, Agri-Vet uses LangGraph to chain three specialized AI Agents together:


Step 1: The Interpreter: It takes a rough farmer query (e.g., "My cow isn't eating") and extracts structured data: Animal: Cow, Symptom: Anorexia.

Step 2: The Vet Agent: It analyzes the symptoms and medical history to provide a Diagnosis (e.g., "Possible Bovine Fever").

Step 3: The Nutritionist Agent: It creates a recovery diet plan. Crucially, it uses a Safety Tool (Python code) to check for toxins (e.g., ensuring a dog isn't prescribed chocolate).

Step 4: The Scheduler Agent: It converts the medical advice into a strict 24-hour operational schedule (e.g., "06:00 AM: Milking, 08:00 AM: Feed Medicine").

4. Key Technologies


Google Gemini 2.0 Flash: The high-speed "brain" powering the agents.

LangGraph: The framework that manages the flow between agents.

Gradio: The simple chat interface for the farmer.

JSON Memory: A local database that remembers the medical history of specific animals.

5. Unique Selling Point (USP)

Safety First: It doesn't just guess; it runs code to verify that food recommendations are safe.

Action-Oriented: It gives farmers a schedule, not just medical theory.

Zero Latency: It provides expert-level advice in seconds, 24/7.
