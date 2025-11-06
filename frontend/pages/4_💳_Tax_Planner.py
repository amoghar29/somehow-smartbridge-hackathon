"""
Tax Planning Page - AI-powered tax advice
"""

import streamlit as st
from utils.api_client import APIClient
from config.settings import BACKEND_URL
import plotly.graph_objects as go

st.set_page_config(page_title="Tax Planner", page_icon="💳", layout="wide")

# Initialize API client
api_client = APIClient(BACKEND_URL)

st.title("💳 Smart Tax Planning")

# Check backend connection
if not api_client.check_health():
    st.error("⚠️ Backend server is not running! Please start it at http://localhost:8000")
    st.stop()

st.write("Get AI-powered tax-saving advice tailored to Indian tax laws.")

# Tax input section
st.subheader("📝 Your Income Details")

col1, col2 = st.columns(2)

with col1:
    annual_income = st.number_input("Annual Gross Income (₹)", min_value=0, value=1200000, step=50000)
    persona = st.selectbox("Tax Planning Approach", ["conservative", "professional", "aggressive"])

with col2:
    st.markdown("**Existing Deductions:**")
    deduction_80c = st.number_input("Section 80C (max ₹1.5L)", min_value=0, max_value=150000, value=50000, step=10000)
    deduction_80d = st.number_input("Section 80D (Health)", min_value=0, max_value=75000, value=25000, step=5000)
    other_deductions = st.number_input("Other Deductions", min_value=0, value=0, step=5000)

total_deductions = deduction_80c + deduction_80d + other_deductions + 50000  # Standard deduction

# Calculate tax (simplified new regime)
taxable_income = max(annual_income - total_deductions, 0)

if taxable_income <= 250000:
    tax = 0
elif taxable_income <= 500000:
    tax = (taxable_income - 250000) * 0.05
elif taxable_income <= 750000:
    tax = 12500 + (taxable_income - 500000) * 0.10
elif taxable_income <= 1000000:
    tax = 37500 + (taxable_income - 750000) * 0.15
elif taxable_income <= 1250000:
    tax = 75000 + (taxable_income - 1000000) * 0.20
elif taxable_income <= 1500000:
    tax = 125000 + (taxable_income - 1250000) * 0.25
else:
    tax = 187500 + (taxable_income - 1500000) * 0.30

# Add cess (4%)
tax_with_cess = tax * 1.04

# Display metrics
st.subheader("📊 Tax Calculation")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Gross Income", f"₹{annual_income:,.0f}")
with col2:
    st.metric("Total Deductions", f"₹{total_deductions:,.0f}")
with col3:
    st.metric("Taxable Income", f"₹{taxable_income:,.0f}")
with col4:
    effective_rate = (tax_with_cess / annual_income * 100) if annual_income > 0 else 0
    st.metric("Effective Tax Rate", f"{effective_rate:.1f}%")

st.metric("**Tax Payable**", f"₹{tax_with_cess:,.0f}", delta=f"₹{(annual_income * 0.3 - tax_with_cess):,.0f} saved")

# Get AI tax advice
if st.button("🤖 Get AI Tax-Saving Advice", use_container_width=True, type="primary"):
    st.divider()
    st.subheader("🤖 AI-Powered Tax Advice")

    with st.spinner("AI is analyzing your tax situation..."):
        # Call backend AI tax advisor
        advice = api_client.get_tax_advice(
            income=annual_income,
            persona=persona
        )

    if advice:
        st.success("✅ Tax Analysis Complete!")
        st.info(f"**💡 AI Tax Advisor:**\n\n{advice}")
    else:
        st.error("Failed to get tax advice. Please try again.")

# Visualization
st.divider()
st.subheader("📊 Tax Breakdown Visualization")

col1, col2 = st.columns(2)

with col1:
    # Income breakdown
    income_data = {
        "Tax Payable": tax_with_cess,
        "Deductions": total_deductions,
        "Net Income": annual_income - tax_with_cess - total_deductions
    }

    fig_pie = go.Figure(data=[go.Pie(
        labels=list(income_data.keys()),
        values=list(income_data.values()),
        hole=0.4,
        marker=dict(colors=['#f5576c', '#feca57', '#84fab0'])
    )])

    fig_pie.update_layout(
        title="Income Distribution",
        height=400,
        paper_bgcolor='rgba(0,0,0,0)'
    )

    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    # Tax slab visualization
    slabs = ["0-2.5L", "2.5-5L", "5-7.5L", "7.5-10L", "10-12.5L", "12.5-15L", ">15L"]
    rates = [0, 5, 10, 15, 20, 25, 30]

    fig_bar = go.Figure(data=[
        go.Bar(x=slabs, y=rates, marker_color='#667eea')
    ])

    fig_bar.update_layout(
        title="Income Tax Slabs (New Regime)",
        xaxis_title="Income Slab",
        yaxis_title="Tax Rate (%)",
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0.02)'
    )

    st.plotly_chart(fig_bar, use_container_width=True)

# Tax-saving instruments
st.divider()
st.subheader("💡 Tax-Saving Investment Options")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **📈 Section 80C (₹1.5L limit)**
    - ELSS Mutual Funds (3 yr lock-in)
    - PPF (15 yr, tax-free returns)
    - NSC (5 yr, fixed returns)
    - Tax Saver FD (5 yr)
    - Life Insurance Premium
    - Home Loan Principal
    - Tuition Fees
    """)

with col2:
    st.markdown("""
    **🏥 Section 80D (Health)**
    - Self & Family: ₹25,000
    - Parents (< 60 yrs): ₹25,000
    - Parents (≥ 60 yrs): ₹50,000
    - Preventive health checkup: ₹5,000
    - Total max: ₹1,00,000

    **🏠 Section 24 (Home Loan)**
    - Interest: Up to ₹2,00,000
    """)

with col3:
    st.markdown("""
    **💰 Other Deductions**
    - 80CCD(1B): NPS ₹50,000
    - 80E: Education Loan Interest
    - 80G: Donations to charity
    - 80GG: Rent paid (no HRA)
    - 80TTA: Savings interest ₹10,000
    - 80TTB: Senior citizens ₹50,000
    """)

# Tax planning checklist
st.divider()
st.subheader("✅ Tax Planning Checklist")

with st.expander("📄 Documents Required for Tax Filing"):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        **Income Documents:**
        - [ ] Form 16 from employer
        - [ ] Form 26AS (Tax Credit Statement)
        - [ ] Salary slips
        - [ ] Bank statements
        - [ ] Interest certificates

        **Investment Proofs:**
        - [ ] PPF passbook/statements
        - [ ] ELSS investment receipts
        - [ ] Life insurance premium receipts
        - [ ] NPS contribution certificate
        """)

    with col2:
        st.markdown("""
        **Deduction Proofs:**
        - [ ] Health insurance premium receipts
        - [ ] Home loan interest certificate
        - [ ] Education loan certificate
        - [ ] Rent receipts/agreement (HRA)
        - [ ] Donation receipts (80G)

        **Other Documents:**
        - [ ] PAN Card
        - [ ] Aadhaar Card
        - [ ] Previous year ITR (if any)
        - [ ] TDS certificates
        """)

# Tax calendar
st.divider()
st.subheader("📅 Important Tax Dates")

col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    **Q1 (Apr-Jun)**
    - Apr 1: Financial Year starts
    - May: Advance tax payment
    - June: Investment planning
    """)

with col2:
    st.info("""
    **Q2-Q3 (Jul-Dec)**
    - July: ITR filing starts
    - Sep: Advance tax payment
    - Dec: Advance tax payment
    """)

with col3:
    st.info("""
    **Q4 (Jan-Mar)**
    - Jan: Last quarter planning
    - Mar 15: Advance tax payment
    - Mar 31: Financial Year ends
    """)
