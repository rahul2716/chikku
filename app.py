import streamlit as st
import mh

def main():
    # Custom CSS for better styling
    st.markdown("""
        <style>
        .main-title {
            color: #2E86C1;
            font-size: 48px;
            font-weight: bold;
            text-align: center;
            margin-bottom: 20px;
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
            st.session_state.client = mh.create_llm_client()

    # Create a chat interface
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Display chat history with enhanced styling
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🧑" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])

    # Enhanced chat input
    if prompt := st.chat_input("Share what's on your mind... 💭"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑"):
            st.markdown(prompt)

        # Get bot response with loading animation
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                response = mh.get_llm_response(
                    st.session_state.client,
                    prompt,
                    model="Meta-Llama-3.1-8B-Instruct",
                    temperature=0.7
                )
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

    # Enhanced sidebar with better formatting
    with st.sidebar:
        st.markdown("### 📌 Important Information")
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
