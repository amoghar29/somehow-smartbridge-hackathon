"""
AI Chat Assistant Page - Real-time AI financial advice
"""

import streamlit as st
from utils.api_client import APIClient
from config.settings import BACKEND_URL
from datetime import datetime

st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")

# Initialize API client
api_client = APIClient(BACKEND_URL)

st.title("🤖 AI Financial Assistant")

# Check backend connection
if not api_client.check_health():
    st.error("⚠️ Backend server is not running! Please start it at http://localhost:8000")
    st.stop()

# Check model status
health = api_client.get_health_status()
if health.get("model_loaded"):
    st.success("✅ AI Model loaded and ready!")
else:
    st.warning("⚠️ AI Model is loading... First response may take longer.")

st.write("Chat with your AI-powered financial advisor. Ask anything about personal finance, budgeting, investments, or taxes.")

# Initialize chat history
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "Hello! I'm your AI financial assistant powered by IBM Granite AI. How can I help you today?", "timestamp": datetime.now()}
    ]

# Chat context selector (outside tabs)
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    chat_persona = st.selectbox(
        "Financial Profile",
        ["professional", "conservative", "aggressive"],
        help="Choose your risk tolerance for personalized advice"
    )

with col2:
    chat_context = st.selectbox(
        "Topic Context",
        ["General Finance", "Budgeting", "Goal Planning", "Tax Planning", "Investment"],
        help="Select the topic you want to discuss"
    )

with col3:
    if st.button("Clear Chat", use_container_width=True):
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Chat cleared. How can I help you?", "timestamp": datetime.now()}
        ]
        st.rerun()

st.divider()

# Chat interface
tab1, tab2 = st.tabs(["💬 Chat", "📚 Example Questions"])

with tab1:
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                if "timestamp" in message:
                    st.caption(f"🕒 {message['timestamp'].strftime('%I:%M %p')}")

with tab2:
    st.subheader("💡 Example Questions You Can Ask")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **💰 Budgeting & Savings**
        - How much should I save each month?
        - What's the 50-30-20 budgeting rule?
        - How to create an emergency fund?
        - Tips to reduce monthly expenses?
        - How to track my spending effectively?

        **🎯 Goal Planning**
        - How to plan for retirement?
        - Best way to save for a house down payment?
        - How much emergency fund do I need?
        - Planning for children's education?
        - Short-term vs long-term goals?

        **📊 Investment Advice**
        - What are mutual funds?
        - Should I invest in stocks or bonds?
        - How to diversify my portfolio?
        - What is SIP and how does it work?
        - Risk vs returns in investing?
        """)

    with col2:
        st.markdown("""
        **💳 Debt Management**
        - How to pay off credit card debt?
        - Good debt vs bad debt?
        - Should I consolidate my loans?
        - How to improve credit score?
        - Managing EMIs effectively?

        **📈 Tax Planning**
        - What are Section 80C deductions?
        - How to save tax on income?
        - Old vs new tax regime?
        - Tax-saving investment options?
        - When should I file ITR?

        **💡 General Finance**
        - What is financial freedom?
        - How to create a financial plan?
        - Insurance types and coverage?
        - Inflation and its impact?
        - How to build wealth over time?
        """)

    st.divider()

    st.subheader("🚀 Quick Actions")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("💰 Analyze My Budget", use_container_width=True):
            st.switch_page("pages/2_💰_Budget.py")

    with col2:
        if st.button("🎯 Plan My Goals", use_container_width=True):
            st.switch_page("pages/1_🎯_Goals.py")

    with col3:
        if st.button("📊 View Dashboard", use_container_width=True):
            st.switch_page("app.py")

# Sidebar with AI info
with st.sidebar:
    st.subheader("🤖 AI Model Info")

    if health.get("model_loaded"):
        st.success("Model: IBM Granite 3.0 2B")
        st.info("Status: Ready")
    else:
        st.warning("Status: Loading...")

    st.divider()

    st.subheader("💡 Tips for Better Responses")
    st.markdown("""
    - Be specific with your questions
    - Provide context when needed
    - Ask follow-up questions
    - Mention your income/expenses for personalized advice
    """)

    st.divider()

    # Export chat
    if st.button("📥 Export Chat History"):
        chat_text = "\n\n".join([
            f"{msg['role'].upper()}: {msg['content']}"
            for msg in st.session_state.chat_messages
        ])
        st.download_button(
            label="Download Chat",
            data=chat_text,
            file_name=f"finance_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain"
        )

# Chat input - MUST be outside tabs/columns/expander/sidebar
user_input = st.chat_input("Ask me anything about personal finance...")

if user_input:
    # Add user message
    st.session_state.chat_messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now()
    })

    # Get AI response
    with st.spinner("🤖 AI is thinking..."):
        response = api_client.get_ai_advice(user_input, persona=chat_persona)

    # Add AI response to chat history
    st.session_state.chat_messages.append({
        "role": "assistant",
        "content": response,
        "timestamp": datetime.now()
    })

    # Rerun to show new messages
    st.rerun()
