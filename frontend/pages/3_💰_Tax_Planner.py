"""
Tax Planner page - Calculate taxes and get AI-powered tax-saving suggestions.
"""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Tax Planner", page_icon="💰", layout="wide")

st.title("💰 Tax Planning Assistant")

# Check authentication
if not st.session_state.get('authenticated', False):
    st.warning("Please login to access tax planner")
    st.stop()

# Tax calculation section
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📋 Income Details")

    annual_income = st.number_input("Annual Gross Income (₹)", min_value=0, value=1200000, step=10000)

    # Deductions input
    st.subheader("📉 Deductions")

    tab1, tab2, tab3 = st.tabs(["Section 80C", "Section 80D", "Other Deductions"])

    with tab1:
        st.markdown("**Section 80C - Maximum ₹1,50,000**")
        ppf = st.number_input("PPF Investment", min_value=0, max_value=150000, value=50000)
        elss = st.number_input("ELSS Mutual Funds", min_value=0, max_value=150000, value=30000)
        life_insurance = st.number_input("Life Insurance Premium", min_value=0, max_value=150000, value=20000)
        tuition_fees = st.number_input("Children's Tuition Fees", min_value=0, max_value=150000, value=0)

        total_80c = min(ppf + elss + life_insurance + tuition_fees, 150000)
        st.metric("Total 80C Deductions", f"₹{total_80c:,}")

    with tab2:
        st.markdown("**Section 80D - Medical Insurance**")
        health_insurance_self = st.number_input("Health Insurance (Self & Family)", min_value=0, max_value=25000, value=15000)
        health_insurance_parents = st.number_input("Health Insurance (Parents)", min_value=0, max_value=50000, value=20000)

        total_80d = health_insurance_self + health_insurance_parents
        st.metric("Total 80D Deductions", f"₹{total_80d:,}")

    with tab3:
        st.markdown("**Other Deductions**")
        home_loan_interest = st.number_input("Home Loan Interest (Section 24)", min_value=0, max_value=200000, value=0)
        education_loan = st.number_input("Education Loan Interest (Section 80E)", min_value=0, value=0)
        nps = st.number_input("NPS Contribution (Section 80CCD)", min_value=0, max_value=50000, value=0)

        total_other = home_loan_interest + education_loan + nps
        st.metric("Other Deductions", f"₹{total_other:,}")

with col2:
    st.subheader("📊 Tax Calculation")

    # Tax calculation
    total_deductions = total_80c + total_80d + total_other + 50000  # Standard deduction
    taxable_income = max(annual_income - total_deductions, 0)

    # Calculate tax (simplified new regime)
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

    # Add cess
    tax_with_cess = tax * 1.04

    # Display metrics
    st.metric("Gross Income", f"₹{annual_income:,}")
    st.metric("Total Deductions", f"₹{total_deductions:,}")
    st.metric("Taxable Income", f"₹{taxable_income:,}")
    st.metric("Tax Payable", f"₹{tax_with_cess:,.0f}", f"-₹{(annual_income * 0.3 - tax_with_cess):,.0f} saved")

    # Effective tax rate
    effective_rate = (tax_with_cess / annual_income * 100) if annual_income > 0 else 0
    st.metric("Effective Tax Rate", f"{effective_rate:.1f}%")

st.divider()

# AI Tax Suggestions
st.subheader("🤖 AI Tax-Saving Suggestions")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **📈 Investment Suggestions**
    - Increase ELSS investment by ₹40,000
    - Start NPS with ₹50,000/year
    - Consider PPF for long-term savings

    **Potential Saving**: ₹28,000
    """)

with col2:
    st.markdown("""
    **🏠 Property Benefits**
    - Claim HRA if paying rent
    - Consider home loan for Section 24
    - Register joint ownership for benefits

    **Potential Saving**: ₹45,000
    """)

with col3:
    st.markdown("""
    **👨‍👩‍👧‍👦 Family Planning**
    - Health insurance for parents
    - Education expenses for children
    - Dependent disability benefits

    **Potential Saving**: ₹15,000
    """)

# Tax comparison chart
st.subheader("📊 Old vs New Tax Regime Comparison")

regime_data = pd.DataFrame({
    'Income Slab': ['0-2.5L', '2.5-5L', '5-7.5L', '7.5-10L', '10-12.5L', '12.5-15L', '>15L'],
    'Old Regime': [0, 5, 20, 20, 30, 30, 30],
    'New Regime': [0, 5, 10, 15, 20, 25, 30]
})

fig = go.Figure()
fig.add_trace(go.Bar(name='Old Regime', x=regime_data['Income Slab'], y=regime_data['Old Regime'], marker_color='#667eea'))
fig.add_trace(go.Bar(name='New Regime', x=regime_data['Income Slab'], y=regime_data['New Regime'], marker_color='#84fab0'))

fig.update_layout(
    barmode='group',
    height=300,
    xaxis_title="Income Slab",
    yaxis_title="Tax Rate (%)",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0.02)'
)

st.plotly_chart(fig, use_container_width=True)

# Documents checklist
with st.expander("📄 Documents Required for Tax Filing"):
    st.markdown("""
    **Income Documents:**
    - [ ] Form 16 from employer
    - [ ] Form 26AS (Tax Credit Statement)
    - [ ] Salary slips
    - [ ] Bank statements

    **Investment Proofs:**
    - [ ] PPF passbook/statements
    - [ ] ELSS investment receipts
    - [ ] Life insurance premium receipts
    - [ ] NPS contribution certificate

    **Deduction Proofs:**
    - [ ] Health insurance premium receipts
    - [ ] Home loan interest certificate
    - [ ] Education loan interest certificate
    - [ ] Rent receipts/agreement (for HRA)
    """)

# Tax-saving tips
st.divider()
st.subheader("💡 Quick Tax-Saving Tips")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **Before March 31st:**
    1. Complete Section 80C investments (₹1.5 lakhs)
    2. Pay health insurance premiums
    3. Make NPS contributions
    4. Donate to eligible charities (Section 80G)
    5. Submit investment proofs to employer
    """)

with col2:
    st.markdown("""
    **Year-Round Planning:**
    1. Start SIPs in ELSS funds early
    2. Maintain separate savings for tax payments
    3. Keep all investment receipts organized
    4. Review tax situation quarterly
    5. Consult with a tax professional
    """)
