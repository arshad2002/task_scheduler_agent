from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
import json
from calander import authenticate_with_oauth, add_event
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')


llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=api_key
)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant that provides event details in JSON format. "
            "Extract the event information from the unstructured input and format it as JSON with these fields: "
            "summary, location, description, start_time, end_time, attendees, reminders. "
            "Respond only with valid JSON."
        ),
        ("human", "Extract event details from this text and format as JSON: {input}"),
    ]
)

chain = prompt | llm
input_paragraph = """
The event will take place at 123 Event St, Sample City, SC. It is titled 'Bangla Event'. The event will be held on 30th August 2025, starting at 9:00 AM and ending at 10:00 AM. Attendees include example@example.com. Please make sure to remind everyone 10 minutes before the event begins.
"""
result = chain.invoke({
    "input": input_paragraph
})

def extract_json_from_response(response_text):
    """Extract JSON content from markdown code blocks."""
    text = response_text.strip()
    
    # Remove markdown code block formatting
    if text.startswith('```json'):
        text = text[7:]  # Remove '```json'
    elif text.startswith('```'):
        text = text[3:]   # Remove '```'
    
    if text.endswith('```'):
        text = text[:-3]  # Remove trailing '```'
    
    return text.strip()

def prepare_attendees(attendees_data):
    """Convert attendees to proper format."""
    if isinstance(attendees_data, str):
        return [attendees_data]
    return attendees_data or []

def create_calendar_event(event_data):
    """Create calendar event from parsed data."""
    service = authenticate_with_oauth()
    
    add_event(
        service=service,
        summary=event_data.get('summary'),
        location=event_data.get('location'),
        description=event_data.get('description'),
        start_time=event_data.get('start_time'),
        end_time=event_data.get('end_time'),
        attendees=prepare_attendees(event_data.get('attendees')),
        reminders=event_data.get('reminders')
    )

if __name__ == "__main__":
    clean_json = extract_json_from_response(result.content)
    event_data = json.loads(clean_json)
    create_calendar_event(event_data)
    print("\nEvent successfully added to Google Calendar!")
