import pymongo
from pymongo import MongoClient
import os
import openai
import streamlit as st
from dotenv import load_dotenv
import datetime

os.environ["SAMBANOVA_API_KEY"] = "f73bf144-c816-4e8b-a7c0-23dc86ada6f2"

def connect_to_mongodb():
    password = "B4DxRahulOp"
    uri = f"mongodb+srv://rahulpandeyk8220:{password}@chikku.rqvyz.mongodb.net/?ssl=true&ssl_cert_reqs=CERT_NONE"
    client = MongoClient(uri, 
                        tls=True,
                        tlsAllowInvalidCertificates=True)
    db = client.project0
    return db



def create_llm_client(base_url="https://api.sambanova.ai/v1"):
    """
    Creates a secure LLM client with proper error handling.
    Returns: OpenAI client instance.
    """
    # Load environment variables from .env file
    load_dotenv()
    
    
    # Get API key from environment variables
    api_key = os.getenv("SAMBANOVA_API_KEY")
    if not api_key:
        raise ValueError("API key not found in environment variables")

    try:
        client = openai.OpenAI(api_key=api_key, base_url=base_url)
        return client
    except Exception as e:
        raise ConnectionError(f"Failed to initialize API client: {str(e)}")

def get_llm_response(client, prompt, model="deepseek-ai/deepseek-r1-distill-70b", temperature=0.7, top_p=0.9):
    """
    Sends a request to the LLM API with error handling.
    
    Args:
        client: OpenAI client instance.
        prompt: String prompt to send to the model.
        model: Model identifier string.
        temperature: Float between 0 and 1.
        top_p: Float between 0 and 1.
    
    Returns: 
        Generated response text.
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful chatbot."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            top_p=top_p
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error getting LLM response: {str(e)}"

def save_chat_message(db, user_id, message):
    chat_collection = db.chats
    chat_doc = {
        "user_id": user_id,
        "role": message["role"],
        "content": message["content"],
        "timestamp": datetime.datetime.now()
    }
    chat_collection.insert_one(chat_doc)

def chat():
    """
    Runs a chatbot loop where the user can continuously interact with the LLM.
    """
    prompt = """You are a knowledgeable and compassionate mental wellness guide with expertise in:

1. Providing clear, actionable strategies for mental wellbeing
2. Sharing evidence-based techniques for managing stress and anxiety
3. Offering practical tools for emotional regulation
4. Building resilience through proven methods
5. Teaching mindfulness and meditation practices
6. Recommending lifestyle improvements for better mental health
7. Guiding positive habit formation
8. Fostering healthy thought patterns
9. Promoting self-care routines
10. Strengthening emotional intelligence

Deliver responses with confidence, warmth, and directness. Focus on practical solutions and positive actions. Share specific techniques, exercises, and strategies that users can implement immediately. Keep responses action-oriented and empowering."""

    try:
        client = create_llm_client()
        print("Chatbot is ready! Type 'exit' to quit.")

        while True:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                print("Chatbot: Goodbye! Have a great day.")
                break
            
            # Fixed: Pass user_input as the prompt parameter
            response = get_llm_response(client, prompt)

            print(f"Chatbot: {response}")

    except Exception as e:
        print(f"Error: {str(e)}")


def main():
    # Initialize MongoDB connection
    db = connect_to_mongodb()
    # Store it in session state for reuse
    if 'mongodb' not in st.session_state:
        st.session_state.mongodb = db

    # Custom CSS for better styling
    st.markdown("""
        <style>
        .main-title {
            color: #2E86C1;
            font-size: 48px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
            background-color:red;
        }
        .subtitle {
            color: #566573;
            font-size: 20px;
            text-align: center;
            margin-bottom: 30px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Enhanced title and welcome message
    st.markdown('<p class="main-title">🌟 CHIKKU 🌟</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Mental wellness starts with a conversation. Let\'s talk, reflect, and find peace together. 💭✨</p>', unsafe_allow_html=True)

    # Add a decorative separator
    st.markdown("---")

    # Initialize the LLM client with a loading spinner
    if 'client' not in st.session_state:
        with st.spinner("Setting up your personal wellness assistant..."):
            st.session_state.client = create_llm_client()

    # Create a chat interface
    if 'messages' not in st.session_state:
        st.session_state.messages = []

  

    # Enhanced chat input
    if prompt := st.chat_input("Share what's on your mind... 💭"):
        message = {"role": "user", "content": prompt}
        st.session_state.messages.append(message)
        # Save to MongoDB
        save_chat_message(st.session_state.mongodb, "user123", message)
        with st.chat_message("user", avatar="🧑"):
            st.markdown(prompt)

        # Get bot response with loading animation
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                response = get_llm_response(
                    st.session_state.client,
                    prompt,
                    model="Meta-Llama-3.1-8B-Instruct",
                    temperature=0.7
                )
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
      # Enhanced sidebar with chat history organization
        with st.sidebar:
          st.markdown("📌 Important Information")
          st.info("""
          🤝 This is your supportive AI companion for mental health guidance.
        
          🚨 In case of emergency:
          • Call 108 immediately
        
          ⚕️ Remember: 
          This tool complements but does not replace professional mental healthcare.
        
          🤖 You're not alone in this journey.
          """)
        

                      
if __name__ == "__main__":
    main()
