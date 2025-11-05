"""
AI Assistant page - Chat with AI for financial advice and learning.
"""

import streamlit as st
from datetime import datetime

st.set_page_config(page_title="AI Assistant", page_icon="🤖", layout="wide")

st.title("🤖 AI Financial Assistant")

# Check authentication
if not st.session_state.get('authenticated', False):
    st.warning("Please login to access AI assistant")
    st.stop()

# Chat interface
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📚 Learning Center", "❓ FAQs"])

with tab1:
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm your personal finance assistant. How can I help you today?"}
        ]

    # Chat context selector
    col1, col2 = st.columns([3, 1])
    with col1:
        context = st.selectbox(
            "Select Context",
            ["General Finance", "Goal Planning", "Tax Advice", "Investment", "Learning"],
            key="chat_context"
        )
    with col2:
        if st.button("Clear Chat"):
            st.session_state.messages = [
                {"role": "assistant", "content": "Chat cleared. How can I help you?"}
            ]
            st.rerun()

    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me about your finances..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.write(prompt)

        # Generate AI response (simulated)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Simulated AI response based on context
                if "tax" in prompt.lower():
                    response = """Based on your income profile, here are some tax-saving suggestions:

1. **Maximize Section 80C** (₹1.5 lakhs limit):
   - Consider ELSS mutual funds for better returns
   - PPF for guaranteed tax-free returns

2. **Health Insurance (Section 80D)**:
   - You can claim up to ₹25,000 for self and family
   - Additional ₹50,000 for parents (senior citizens)

3. **NPS Contribution**:
   - Extra ₹50,000 deduction under Section 80CCD(1B)

Would you like me to calculate your potential tax savings?"""

                elif "goal" in prompt.lower():
                    response = """I can help you plan your financial goals! Based on your current savings rate of 25%, here's what I suggest:

**For your Emergency Fund goal:**
- Target: ₹3,00,000 (6 months of expenses)
- Current: ₹1,80,000 (60% complete)
- Monthly contribution needed: ₹15,000
- Timeline: 8 months to completion

**Tips to accelerate:**
1. Reduce dining expenses by 20% (save ₹2,000/month)
2. Optimize subscriptions (save ₹1,500/month)
3. Consider a side hustle for extra income

Shall I create a detailed savings plan for you?"""

                elif "invest" in prompt.lower():
                    response = """Based on your moderate risk profile, here's a balanced investment strategy:

**Recommended Asset Allocation:**
- **Equity (50%)**: ₹2,70,000
  - Large Cap Funds: 30%
  - Mid Cap Funds: 15%
  - International Funds: 5%

- **Debt (30%)**: ₹1,62,000
  - Corporate Bonds: 15%
  - Government Securities: 15%

- **Gold (10%)**: ₹54,000
  - Sovereign Gold Bonds

- **Emergency Fund (10%)**: ₹54,000
  - Liquid Funds

Your current portfolio seems overweight in equity. Consider rebalancing for better risk management.

Would you like specific fund recommendations?"""

                else:
                    response = f"""I understand you're asking about {prompt}. Let me help you with that.

Based on your financial profile:
- Monthly Income: ₹60,000
- Monthly Expenses: ₹45,000
- Savings Rate: 25%

Here's my analysis and suggestions:

1. You're doing well with a 25% savings rate
2. Consider automating your savings
3. Review and optimize your expenses monthly
4. Set up specific goals for better planning

Is there anything specific you'd like to explore?"""

                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

with tab2:
    st.subheader("📚 Financial Learning Center")

    # Learning categories
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **📈 Investment Basics**
        - What are Mutual Funds?
        - Understanding Stock Markets
        - Bond Investment Guide
        - Portfolio Diversification
        - Risk vs Returns
        """)
        if st.button("Start Learning →", key="invest_learn"):
            st.info("Loading investment course...")

    with col2:
        st.markdown("""
        **💰 Tax Planning**
        - Income Tax Basics
        - Deductions & Exemptions
        - Tax-saving Instruments
        - ITR Filing Guide
        - Advance Tax Planning
        """)
        if st.button("Start Learning →", key="tax_learn"):
            st.info("Loading tax planning course...")

    with col3:
        st.markdown("""
        **🎯 Financial Planning**
        - Budgeting 101
        - Emergency Fund Setup
        - Goal-based Investing
        - Retirement Planning
        - Insurance Planning
        """)
        if st.button("Start Learning →", key="plan_learn"):
            st.info("Loading financial planning course...")

    # Interactive quiz
    st.divider()
    st.subheader("🎮 Test Your Knowledge")

    with st.expander("Take a Quick Quiz"):
        q1 = st.radio(
            "What is the maximum deduction under Section 80C?",
            ["₹1,00,000", "₹1,50,000", "₹2,00,000", "₹2,50,000"]
        )

        q2 = st.radio(
            "Which investment has the shortest lock-in period for tax saving?",
            ["PPF", "ELSS", "NSC", "Tax Saver FD"]
        )

        if st.button("Submit Quiz"):
            score = 0
            if q1 == "₹1,50,000":
                score += 1
            if q2 == "ELSS":
                score += 1

            st.success(f"Your score: {score}/2")
            if score == 2:
                st.balloons()

with tab3:
    st.subheader("❓ Frequently Asked Questions")

    faqs = [
        {
            "question": "How much should I save monthly?",
            "answer": "A good rule of thumb is the 50-30-20 rule: 50% for needs, 30% for wants, and 20% for savings. However, aim for at least 20-30% savings rate for better financial security."
        },
        {
            "question": "What is an emergency fund?",
            "answer": "An emergency fund is 3-6 months of expenses saved for unexpected situations like job loss or medical emergencies. Keep it in liquid instruments like savings accounts or liquid funds."
        },
        {
            "question": "ELSS vs PPF - Which is better?",
            "answer": "ELSS offers potentially higher returns (12-15%) with 3-year lock-in, while PPF provides guaranteed returns (7.1%) with 15-year lock-in. Choose based on your risk appetite and liquidity needs."
        },
        {
            "question": "How to improve credit score?",
            "answer": "Pay bills on time, maintain low credit utilization (<30%), avoid multiple loan applications, maintain old credit accounts, and regularly check your credit report for errors."
        },
        {
            "question": "Should I invest in stocks or mutual funds?",
            "answer": "For beginners, mutual funds are generally better as they offer professional management and diversification. Direct stock investing requires significant research and time commitment."
        },
        {
            "question": "What is the best retirement planning strategy?",
            "answer": "Start early, aim to save at least 15-20% of income for retirement, diversify across equity and debt, consider NPS for additional tax benefits, and review your plan annually."
        }
    ]

    for faq in faqs:
        with st.expander(faq["question"]):
            st.write(faq["answer"])
