import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from main import UnifiedChatbot  # Importing from your main.py

# Initialize chatbot and workflow only once
if "workflow" not in st.session_state:
    unified_bot = UnifiedChatbot()
    st.session_state.workflow = unified_bot()
    st.session_state.chat_history = []

# Set up Streamlit layout
st.set_page_config(page_title="Unified Chatbot", layout="wide")

# --- Sidebar for Branding and Control ---
with st.sidebar:
    st.title("🤖 Unified Assistant")
    st.markdown("""
    This chatbot supports:
    - 🛒 Budget-Friendly Shopping  
    - 🏬 Stock & Inventory Analysis  
    - 🍲 Recipe Suggestions  

    Simply ask anything like:
    - "Show me the recipe of dal fry"
    - "I want to buy groceries under 200"
    - "Check stock in store 1"
    """)
    if st.button("🔁 Clear Chat"):
        st.session_state.chat_history = []

# --- Main Chat Interface ---
st.title("💬 Talk to Unified Chatbot")
user_input = st.chat_input("Ask something...")

# Display existing chat history
for msg in st.session_state.chat_history:
    with st.chat_message("user" if isinstance(msg, HumanMessage) else "assistant"):
        st.markdown(msg.content)

# Handle new message input
if user_input:
    human_msg = HumanMessage(content=user_input)
    st.session_state.chat_history.append(human_msg)

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.workflow.invoke({
                "messages": st.session_state.chat_history
            })
            ai_msg = response["messages"][-1]
            st.session_state.chat_history.append(ai_msg)
            st.markdown(ai_msg.content)
