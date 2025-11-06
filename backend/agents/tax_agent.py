"""
Tax Advisory Agent
Provides educational tax-saving advice for Indian users
"""
from typing import Dict, Any, Optional
from core.granite_api import generate
from core.utils import format_currency
from core.logger import logger


def get_tax_advice(income: float, persona: str = "general", deductions: Optional[Dict[str, float]] = None) -> str:
    """
    Generate tax-saving advice based on income

    Args:
        income: Annual income
        persona: User persona
        deductions: Current deductions (optional)

    Returns:
        str: Tax advice
    """
    try:
        logger.info(f"Generating tax advice for income: {format_currency(income)}")

        # Build AI prompt
        persona_context = _get_persona_context(persona)

        deductions_info = ""
        if deductions:
            total_deductions = sum(deductions.values())
            deductions_info = f"\nCurrent Deductions: {format_currency(total_deductions)}"

        prompt = f"""You are a tax advisor providing educational advice about Indian tax laws.

{persona_context}

Annual Income: {format_currency(income)}{deductions_info}

Provide:
1. Brief overview of applicable tax regime (old vs new)
2. 3-4 common tax-saving investments under Section 80C
3. Other tax deductions to consider
4. General tax planning tips

Keep it educational and concise (under 200 words). Note: This is general guidance, not professional tax advice."""

        # Generate advice using AI
        advice = generate(prompt, max_new_tokens=250, temperature=0.7)

        logger.info("Tax advice generated successfully")

        return advice.strip()

    except Exception as e:
        logger.error(f"Tax advice generation failed: {str(e)}")
        return _get_fallback_tax_advice(income, persona)


def _get_persona_context(persona: str) -> str:
    """Get context based on user persona"""
    contexts = {
        "student": "The user is a student with limited income. Focus on basic tax concepts.",
        "professional": "The user is a salaried professional. Focus on maximizing deductions and investments.",
        "general": "Provide general tax advice for Indian taxpayers."
    }
    return contexts.get(persona.lower(), contexts["general"])


def _get_fallback_tax_advice(income: float, persona: str) -> str:
    """Generate fallback tax advice when AI fails"""

    if income < 500000:
        return """**Tax Planning Tips:**

For income under ₹5 lakhs, you're likely in a lower tax bracket.

**Section 80C Deductions (up to ₹1.5 lakhs):**
- Public Provident Fund (PPF)
- Employee Provident Fund (EPF)
- Equity Linked Savings Scheme (ELSS)
- Life Insurance premiums
- National Savings Certificate (NSC)

**Other Deductions:**
- Section 80D: Health insurance premiums
- Section 80E: Education loan interest

**Tip:** Compare old vs new tax regime to see which benefits you more. The new regime has lower rates but fewer deductions.

*This is educational information, not professional tax advice.*"""

    elif income < 1000000:
        return """**Tax Planning Strategies:**

For your income range (₹5-10 lakhs), tax planning is crucial.

**Priority Investments:**
1. **Section 80C (₹1.5L limit):** Max out EPF/PPF, ELSS funds
2. **Section 80D:** Health insurance for self and parents
3. **NPS (Section 80CCD(1B)):** Additional ₹50,000 deduction
4. **HRA:** If you pay rent, claim HRA exemption

**Smart Tips:**
- Invest early in the financial year
- Keep medical bills and rent receipts
- Consider tax-saving FDs
- Review investments annually

**New vs Old Regime:** Calculate both to find the better option.

*Consult a tax professional for personalized advice.*"""

    else:
        return """**Advanced Tax Planning:**

For higher income brackets (₹10L+), strategic tax planning is essential.

**Key Strategies:**
1. **Maximize Deductions:**
   - Section 80C: ₹1.5 lakhs
   - NPS additional: ₹50,000 (80CCD(1B))
   - Health insurance: ₹25,000-₹100,000 (80D)

2. **Smart Investments:**
   - ELSS for 80C + equity exposure
   - PPF for long-term, tax-free returns
   - NPS for retirement + tax benefits

3. **Other Benefits:**
   - HRA exemption if renting
   - Home loan interest (Section 24)
   - Education loan interest (Section 80E)

4. **Consider:**
   - Tax-loss harvesting in equity
   - Employer's salary structure optimization
   - Charitable donations (Section 80G)

**Important:** For complex situations, hire a CA.

*This is general guidance only.*"""
