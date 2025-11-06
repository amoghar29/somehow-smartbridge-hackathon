"""
Finance-related API routes
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import json
from pathlib import Path

from models.request_models import (
    ChatRequest,
    BudgetRequest,
    GoalRequest,
    TransactionRequest,
    TaxRequest,
    CreateGoalRequest,
    UpdateGoalRequest
)
from models.response_models import (
    ChatResponse,
    BudgetResponse,
    GoalResponse,
    TransactionResponse,
    AnalyticsResponse,
    TaxResponse,
    ErrorResponse,
    CreateGoalResponse,
    UpdateGoalResponse,
    GoalListResponse
)
from agents.budget_agent import analyze_budget
from agents.goal_agent import plan_goal
from agents.tax_agent import get_tax_advice
from agents.intent_router import route_intent, get_fallback_response
from core.granite_service import generate, is_api_available
from core.logger import logger
from core.db_service import TransactionService, ChatHistoryService, GoalService
from core.database import Database
from config.settings import DATA_DIR


router = APIRouter()


@router.post("/ai/generate", response_model=ChatResponse)
async def generate_ai_response(request: ChatRequest):
    """
    General AI response endpoint - Uses Claude API for real AI responses

    Args:
        request: ChatRequest with question and persona

    Returns:
        ChatResponse: AI-generated response
    """
    try:
        logger.info(f"AI generate request: {request.question[:50]}...")

        # Check if Claude API is available
        if not is_api_available():
            error_msg = "⚠️ AI Model not available. Please set ANTHROPIC_API_KEY environment variable to enable AI responses."
            logger.warning(error_msg)
            return ChatResponse(response=error_msg)

        # Generate AI response using Claude API
        try:
            logger.info("Generating AI response using Claude API...")

            # Create a well-structured prompt based on persona
            persona_context = {
                "conservative": "You are a conservative financial advisor who prioritizes safety and guaranteed returns.",
                "professional": "You are a professional financial advisor who provides balanced, practical advice.",
                "aggressive": "You are an aggressive growth-focused financial advisor who emphasizes higher-return investments."
            }

            context = persona_context.get(request.persona, persona_context["professional"])

            prompt = f"""{context}

Provide a clear, concise, and practical answer to the following financial question. Use Indian context (INR, Indian tax laws) where applicable. Format your response in a structured way with bullet points or numbered lists when helpful.

Question: {request.question}

Answer:"""

            response_text = generate(prompt, max_tokens=500, temperature=0.7)

            logger.info("Claude API response generated successfully")

            # Validate response
            if not response_text or len(response_text.strip()) < 20:
                logger.warning("AI response too short")
                response_text = "I couldn't generate a complete response. Please try rephrasing your question or be more specific."

            # Save chat interaction to MongoDB (async, don't wait for it)
            if Database.is_connected():
                try:
                    await ChatHistoryService.save_chat_message(
                        question=request.question,
                        response=response_text,
                        persona=request.persona,
                        metadata={"model": "claude", "timestamp": datetime.now().isoformat()}
                    )
                    logger.info("Chat interaction saved to MongoDB")
                except Exception as save_error:
                    logger.warning(f"Failed to save chat to MongoDB: {str(save_error)}")

            return ChatResponse(response=response_text)

        except Exception as e:
            error_msg = f"AI generation error: {str(e)}. Please try again."
            logger.error(f"AI generation failed: {str(e)}")
            return ChatResponse(response=error_msg)

    except Exception as e:
        logger.error(f"AI generate failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/budget-summary", response_model=BudgetResponse)
async def get_budget_summary(request: BudgetRequest):
    """
    Budget analysis endpoint

    Args:
        request: BudgetRequest with income, expenses, and persona

    Returns:
        BudgetResponse: Budget summary and insights
    """
    try:
        logger.info(f"Budget analysis request for income: {request.income}")

        result = analyze_budget(
            income=request.income,
            expenses=request.expenses,
            persona=request.persona
        )

        return BudgetResponse(
            summary=result["summary"],
            insights=result["insights"]
        )

    except Exception as e:
        logger.error(f"Budget analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/goal-planner", response_model=GoalResponse)
async def plan_financial_goal(request: GoalRequest):
    """
    Goal planning endpoint

    Args:
        request: GoalRequest with goal details

    Returns:
        GoalResponse: Savings plan and advice
    """
    try:
        logger.info(f"Goal planning request: {request.goal_name}")

        result = plan_goal(
            goal_name=request.goal_name,
            target_amount=request.target_amount,
            months=request.months,
            income=request.income,
            persona=request.persona,
            current_savings=request.current_savings
        )

        return GoalResponse(
            plan=result["plan"],
            advice=result["advice"]
        )

    except Exception as e:
        logger.error(f"Goal planning failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/tax-advice", response_model=TaxResponse)
async def get_tax_advisory(request: TaxRequest):
    """
    Tax advice endpoint

    Args:
        request: TaxRequest with income and persona

    Returns:
        TaxResponse: Tax-saving advice
    """
    try:
        logger.info(f"Tax advice request for income: {request.income}")

        advice = get_tax_advice(
            income=request.income,
            persona=request.persona,
            deductions=request.deductions
        )

        return TaxResponse(
            tax_advice=advice,
            estimated_tax=None,
            suggestions=None
        )

    except Exception as e:
        logger.error(f"Tax advice failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics/summary", response_model=AnalyticsResponse)
async def get_analytics_summary():
    """
    Get analytics summary for dashboard

    Returns:
        AnalyticsResponse: Trend data and totals
    """
    try:
        logger.info("Analytics summary requested")

        # Try to get from MongoDB first
        if Database.is_connected():
            transactions_from_db = await TransactionService.get_transactions(limit=1000)

            if transactions_from_db:
                logger.info(f"Using {len(transactions_from_db)} transactions from MongoDB for analytics")
                transactions = transactions_from_db
            else:
                logger.info("No transactions in MongoDB, falling back to JSON file")
                transactions = []
        else:
            transactions = []

        # Fallback to JSON file if MongoDB is not available or has no data
        if not transactions:
            transactions_file = DATA_DIR / "sample_transactions.json"

            if transactions_file.exists():
                with open(transactions_file, 'r') as f:
                    transactions = json.load(f)
                logger.info(f"Loaded {len(transactions)} transactions from JSON file")
            else:
                transactions = []

        # Calculate totals
        total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
        total_expenses = sum(t['amount'] for t in transactions if t['type'] == 'expense')

        # Create trend data (simplified)
        trend_data = [
            {"month": "Jan", "income": total_income * 0.9, "expenses": total_expenses * 0.85},
            {"month": "Feb", "income": total_income * 0.95, "expenses": total_expenses * 0.90},
            {"month": "Mar", "income": total_income, "expenses": total_expenses}
        ]

        totals = {
            "income": total_income,
            "expenses": total_expenses,
            "savings": total_income - total_expenses,
            "savings_rate": ((total_income - total_expenses) / total_income * 100) if total_income > 0 else 0
        }

        return AnalyticsResponse(
            trend_data=trend_data,
            totals=totals
        )

    except Exception as e:
        logger.error(f"Analytics summary failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transactions/add", response_model=TransactionResponse)
async def add_transaction(request: TransactionRequest):
    """
    Add a new transaction

    Args:
        request: TransactionRequest with transaction details

    Returns:
        TransactionResponse: Success status and transaction ID
    """
    try:
        logger.info(f"Adding transaction: {request.description}")

        # Prepare transaction data
        transaction_data = {
            "description": request.description,
            "amount": request.amount,
            "category": request.category,
            "type": request.type,
            "date": request.date if hasattr(request, 'date') and request.date else datetime.now().isoformat()
        }

        # Try to save to MongoDB first
        if Database.is_connected():
            result = await TransactionService.create_transaction(transaction_data)

            if result.get("success"):
                return TransactionResponse(
                    success=True,
                    message="Transaction added successfully",
                    transaction_id=result["transaction_id"]
                )
            else:
                logger.warning(f"Failed to save to MongoDB: {result.get('error')}")

        # Fallback to JSON file if MongoDB is not available
        logger.info("Saving transaction to JSON file (fallback)")
        transactions_file = DATA_DIR / "sample_transactions.json"

        if transactions_file.exists():
            with open(transactions_file, 'r') as f:
                transactions = json.load(f)
        else:
            transactions = []

        # Create new transaction
        new_transaction = {
            "id": f"txn_{len(transactions) + 1}",
            **transaction_data
        }

        transactions.append(new_transaction)

        # Save back to file
        with open(transactions_file, 'w') as f:
            json.dump(transactions, f, indent=2)

        return TransactionResponse(
            success=True,
            message="Transaction added successfully (saved to file)",
            transaction_id=new_transaction["id"]
        )

    except Exception as e:
        logger.error(f"Add transaction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transactions/recent")
async def get_recent_transactions():
    """
    Get recent transactions

    Returns:
        List of recent transactions
    """
    try:
        logger.info("Recent transactions requested")

        # Try to get from MongoDB first
        if Database.is_connected():
            transactions = await TransactionService.get_transactions(limit=50)

            if transactions:
                logger.info(f"Retrieved {len(transactions)} transactions from MongoDB")
                return {"transactions": transactions}
            else:
                logger.info("No transactions found in MongoDB, checking file fallback")

        # Fallback to JSON file
        logger.info("Loading transactions from JSON file (fallback)")
        transactions_file = DATA_DIR / "sample_transactions.json"

        if transactions_file.exists():
            with open(transactions_file, 'r') as f:
                transactions = json.load(f)
        else:
            transactions = []

        # Return last 50 transactions
        return {"transactions": transactions[-50:]}

    except Exception as e:
        logger.error(f"Get transactions failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/goals/add", response_model=CreateGoalResponse)
async def create_goal(request: CreateGoalRequest):
    """
    Create a new goal

    Args:
        request: CreateGoalRequest with goal details

    Returns:
        CreateGoalResponse: Success status and goal ID
    """
    try:
        logger.info(f"Creating goal: {request.name}")

        # Prepare goal data
        goal_data = {
            "name": request.name,
            "target_amount": request.target_amount,
            "current_amount": request.current_amount,
            "category": request.category,
            "deadline": request.deadline,
            "monthly_required": request.monthly_required,
            "status": "active"
        }

        # Save to MongoDB
        if Database.is_connected():
            result = await GoalService.create_goal(goal_data)

            if result.get("success"):
                return CreateGoalResponse(
                    success=True,
                    message="Goal created successfully",
                    goal_id=result["goal_id"]
                )
            else:
                logger.warning(f"Failed to create goal in MongoDB: {result.get('error')}")
                return CreateGoalResponse(
                    success=False,
                    message=f"Failed to create goal: {result.get('error')}"
                )
        else:
            return CreateGoalResponse(
                success=False,
                message="Database not connected"
            )

    except Exception as e:
        logger.error(f"Create goal failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/goals/list", response_model=GoalListResponse)
async def list_goals(status: str = "active"):
    """
    Get all goals

    Args:
        status: Filter by status (active/paused/completed/all)

    Returns:
        GoalListResponse: List of goals
    """
    try:
        logger.info(f"Getting goals with status: {status}")

        if Database.is_connected():
            # Get goals from MongoDB
            if status == "all":
                goals = await GoalService.get_goals(status="")
            else:
                goals = await GoalService.get_goals(status=status)

            return GoalListResponse(
                goals=goals,
                total=len(goals)
            )
        else:
            logger.warning("Database not connected, returning empty list")
            return GoalListResponse(goals=[], total=0)

    except Exception as e:
        logger.error(f"Get goals failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/goals/update/{goal_id}", response_model=UpdateGoalResponse)
async def update_goal(goal_id: str, request: UpdateGoalRequest):
    """
    Update a goal

    Args:
        goal_id: ID of the goal to update
        request: UpdateGoalRequest with updated fields

    Returns:
        UpdateGoalResponse: Success status
    """
    try:
        logger.info(f"Updating goal: {goal_id}")

        if not Database.is_connected():
            return UpdateGoalResponse(
                success=False,
                message="Database not connected"
            )

        # Prepare update data (only include fields that are provided)
        update_data = {}
        if request.current_amount is not None:
            update_data["current_amount"] = request.current_amount
        if request.status is not None:
            update_data["status"] = request.status
        if request.monthly_required is not None:
            update_data["monthly_required"] = request.monthly_required

        if not update_data:
            return UpdateGoalResponse(
                success=False,
                message="No fields to update"
            )

        # Update in MongoDB
        result = await GoalService.update_goal(goal_id, update_data)

        if result.get("success"):
            return UpdateGoalResponse(
                success=True,
                message="Goal updated successfully",
                goal_id=goal_id
            )
        else:
            return UpdateGoalResponse(
                success=False,
                message=result.get("error", "Failed to update goal")
            )

    except Exception as e:
        logger.error(f"Update goal failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


def _get_smart_chat_response(question: str, persona: str = "general") -> str:
    """
    Generate smart contextual responses based on question analysis
    This provides instant, helpful responses without waiting for AI
    """
    question_lower = question.lower()

    # Check if it's a definition question
    is_definition = any(q in question_lower for q in ['what is', 'define', 'meaning of', 'what are'])

    # Savings related
    if any(word in question_lower for word in ['save', 'saving', 'savings']):
        if is_definition:
            return """**What is Savings?**

Savings is the portion of your income that you don't spend immediately and set aside for future use. It's money you keep safe for:
- Emergency situations
- Future goals (house, car, education)
- Retirement
- Financial security

**Types of Savings:**
- **Emergency Fund**: 3-6 months of expenses for unexpected events
- **Short-term Savings**: For goals within 1-3 years (vacation, gadgets)
- **Long-term Savings**: For goals beyond 3 years (house, retirement)

**Why Save?**
- Financial security and peace of mind
- Achieve life goals without debt
- Handle emergencies without stress
- Build wealth over time

**Recommended Savings Rate**: 20-30% of your income (more if possible!)"""
        else:
            return """**Tips to Save More Money:**

1. **Automate Savings**: Set up automatic transfers to a savings account on payday
2. **50/30/20 Rule**: Allocate 50% needs, 30% wants, 20% savings
3. **Track Expenses**: Use apps or spreadsheets to identify wasteful spending
4. **Cut Subscriptions**: Cancel unused subscriptions and memberships
5. **Cook at Home**: Reduce dining out expenses significantly
6. **Emergency Fund**: Build 3-6 months of expenses as a safety net

**Quick Win**: Start by saving just 10% of your income and gradually increase it."""

    # Investment related
    elif any(word in question_lower for word in ['invest', 'investment', 'stocks', 'mutual fund', 'sip', 'equity', 'shares']):
        if is_definition and 'sip' in question_lower:
            return """**What is SIP (Systematic Investment Plan)?**

SIP is a method of investing a fixed amount regularly (monthly/quarterly) in mutual funds.

**How it Works:**
- You invest ₹1,000-₹10,000+ every month
- Units are purchased at different prices over time
- Benefit from rupee cost averaging
- Disciplined, automated investing

**Example:**
- Monthly SIP: ₹5,000
- Duration: 5 years
- Expected return: 12% p.a.
- Invested: ₹3 lakhs
- Value after 5 years: ~₹4.1 lakhs

**Benefits:**
1. Start with small amounts (as low as ₹500)
2. Rupee cost averaging reduces risk
3. Power of compounding
4. Disciplined investing habit
5. Flexibility to increase/pause/stop

**Best For:** Long-term goals (5+ years), first-time investors

**Popular SIP Options:** ELSS funds (tax-saving), Index funds, Large-cap funds"""

        elif is_definition and any(word in question_lower for word in ['stock', 'share', 'equity']):
            return """**What are Stocks/Shares/Equity?**

Stocks (also called shares or equity) represent ownership in a company.

**Key Concepts:**
- 1 share = Small ownership piece of a company
- Stock price changes based on company performance and demand
- You make money through:
  1. **Capital Gains**: Selling at higher price than you bought
  2. **Dividends**: Company's profit distribution

**Example:**
- You buy 10 shares of TCS at ₹3,500 each
- Total investment: ₹35,000
- If price rises to ₹4,000, you gain ₹5,000 (14% return)
- Plus receive dividends if company declares

**Types:**
- **Large Cap**: Big, stable companies (TCS, Reliance)
- **Mid Cap**: Medium-sized, growth companies
- **Small Cap**: Small companies, higher risk/reward

**Risk Level:** High - prices fluctuate daily

**Best For:** Long-term investors (5+ years) with risk appetite

**Tip**: Don't invest money you need in next 2-3 years!"""

        elif is_definition and 'mutual fund' in question_lower:
            return """**What is a Mutual Fund?**

A mutual fund pools money from many investors to invest in stocks, bonds, or other securities, managed by professionals.

**How it Works:**
1. You invest money in a mutual fund
2. Fund manager invests in diversified portfolio
3. You get units based on NAV (Net Asset Value)
4. Returns based on fund performance

**Types:**
- **Equity Funds**: Invest in stocks (high risk, high return)
- **Debt Funds**: Invest in bonds (low risk, steady returns)
- **Hybrid Funds**: Mix of equity and debt (balanced)
- **Index Funds**: Track market indices like Nifty 50

**Advantages:**
- Professional management
- Diversification (reduces risk)
- Start with small amounts
- Liquidity (can redeem anytime)
- Tax benefits (ELSS funds under 80C)

**Returns:** Vary from 6% to 15%+ depending on type

**Costs:** Expense ratio (0.5% to 2.5% per year)

**Best For:** Beginners, busy professionals, long-term wealth building"""

        else:
            return """**Investment Guide for Beginners:**

**Safe Options (Low Risk):**
- Fixed Deposits (FD): 6-7% annual returns
- Public Provident Fund (PPF): Tax-free, 7-8% returns
- Government Bonds

**Moderate Risk:**
- Mutual Funds (SIP): Systematic Investment Plan
- Index Funds: Track market indices
- Balanced Funds: Mix of equity and debt

**Higher Risk:**
- Direct Stocks: Requires research and knowledge
- Equity Mutual Funds

**Golden Rules:**
1. Start early (power of compounding)
2. Diversify your portfolio
3. Invest regularly (SIP approach)
4. Have a long-term view (5+ years)
5. Don't invest in what you don't understand"""

    # Budget related
    elif any(word in question_lower for word in ['budget', 'expense', 'spending']):
        return """**How to Create a Budget:**

**Step 1: Calculate Your Income**
- Monthly salary (after tax)
- Side income, freelance work
- Any other regular income

**Step 2: Track Expenses**
- Fixed: Rent, EMIs, utilities
- Variable: Food, entertainment, shopping
- Occasional: Travel, gifts

**Step 3: Apply 50/30/20 Rule**
- 50% Needs (essentials)
- 30% Wants (lifestyle)
- 20% Savings & Investments

**Step 4: Use Tools**
- Apps like our Finance Assistant
- Spreadsheets
- Envelopes method

**Pro Tip**: Review and adjust your budget monthly based on actual spending."""

    # Tax related
    elif any(word in question_lower for word in ['tax', '80c', 'deduction', 'itr']):
        return """**Tax Saving Tips (India):**

**Section 80C (up to ₹1.5 lakh):**
- PPF (Public Provident Fund)
- ELSS (Equity Linked Savings Scheme)
- EPF (Employee Provident Fund)
- Life Insurance Premium
- NSC (National Savings Certificate)
- Home Loan Principal

**Other Deductions:**
- 80D: Health Insurance (₹25,000-₹100,000)
- 80CCD(1B): NPS Additional (₹50,000)
- 80E: Education Loan Interest
- 80G: Charitable Donations
- 24: Home Loan Interest (₹2 lakh)

**New vs Old Regime:**
- Old: More deductions, higher rates
- New: Lower rates, fewer deductions
- Calculate both to see which saves more

**When to File ITR**: Before July 31st for previous fiscal year."""

    # Emergency fund
    elif any(word in question_lower for word in ['emergency', 'emergency fund']):
        return """**Building an Emergency Fund:**

**Why You Need It:**
- Job loss or income disruption
- Medical emergencies
- Unexpected repairs (car, home)
- Peace of mind

**How Much to Save:**
- Minimum: 3 months of expenses
- Ideal: 6 months of expenses
- If single income: 9-12 months

**Where to Keep It:**
- High-interest savings account
- Liquid mutual funds
- Fixed deposits (with premature withdrawal)

**How to Build:**
1. Calculate monthly expenses
2. Set target (expenses × 6)
3. Start with 10% of income monthly
4. Automate savings
5. Don't touch it unless emergency!

**Timeline**: Aim to build it within 1-2 years."""

    # Debt related
    elif any(word in question_lower for word in ['debt', 'loan', 'credit card', 'emi']):
        return """**Managing Debt Effectively:**

**Priority Order (Pay off in this sequence):**
1. Credit Card Debt (18-36% interest!)
2. Personal Loans
3. Car Loans
4. Home Loans (lowest priority)

**Strategies:**

**Avalanche Method**: Pay highest interest rate first
**Snowball Method**: Pay smallest balance first (psychological wins)

**Tips to Get Out of Debt:**
- Create strict budget
- Cut non-essential expenses
- Use windfalls (bonus, tax refund) for debt
- Consider balance transfer for credit cards
- Negotiate lower interest rates
- Avoid taking new debt

**Credit Card Rules:**
- Always pay full amount (not minimum due)
- Use for rewards only if you can pay off
- Keep utilization below 30%

**Warning**: Avoid loan apps with high interest!"""

    # Credit score
    elif any(word in question_lower for word in ['credit score', 'cibil']):
        return """**Improving Your Credit Score:**

**What is a Good Score:**
- 750+: Excellent (best loan rates)
- 700-749: Good
- 650-699: Fair
- <650: Poor (hard to get loans)

**How to Improve:**

1. **Pay Bills on Time** (35% of score)
   - Set up auto-pay
   - Never miss EMI/credit card payments

2. **Keep Credit Utilization Low** (30% of score)
   - Use <30% of credit limit
   - Request credit limit increase

3. **Maintain Old Accounts** (15% of score)
   - Don't close old credit cards
   - Shows longer credit history

4. **Limit Hard Inquiries** (10% of score)
   - Don't apply for multiple loans at once

5. **Mix Credit Types** (10% of score)
   - Have both credit cards and loans

**Check Your Score Free:** CIBIL, Experian, Equifax websites

**Timeline**: Takes 3-6 months to see improvement."""

    # Retirement planning
    elif any(word in question_lower for word in ['retire', 'retirement', 'pension']):
        return """**Retirement Planning Basics:**

**When to Start:** As early as possible (20s-30s ideal)

**How Much You Need:**
- Rule of thumb: 25-30 times annual expenses
- Example: ₹50,000/month = ₹1.5-1.8 crores

**Best Retirement Options in India:**

1. **NPS (National Pension System)**
   - Tax benefits under 80CCD
   - Market-linked returns
   - Annuity at maturity

2. **PPF (Public Provident Fund)**
   - 15-year lock-in
   - Tax-free returns
   - Safe government scheme

3. **EPF (Employee Provident Fund)**
   - Employer contribution
   - Stable returns
   - Tax benefits

4. **Mutual Funds (Equity)**
   - Higher long-term returns
   - Start SIP early

5. **Real Estate**
   - Rental income in retirement
   - Asset appreciation

**Strategy:**
- Start with 10-15% of income
- Increase by 1% yearly
- Diversify across options
- Review every 5 years"""

    # PPF related
    elif 'ppf' in question_lower or 'public provident fund' in question_lower:
        return """**Public Provident Fund (PPF):**

PPF is a government-backed long-term savings scheme with tax benefits.

**Key Features:**
- Lock-in: 15 years (can extend in 5-year blocks)
- Interest Rate: ~7-7.5% per year (tax-free)
- Minimum: ₹500 per year
- Maximum: ₹1.5 lakh per year
- Tax benefit under Section 80C

**Benefits:**
- Completely safe (government guarantee)
- Returns are tax-free (EEE status)
- Compounding every year
- Partial withdrawal after 7 years
- Loan facility after 3 years

**Best For:**
- Risk-averse investors
- Long-term financial planning
- Retirement corpus
- Tax saving

**Current Rate**: ~7.1% per year (changes quarterly)

**Note**: Can open only 1 PPF account per person"""

    # FD related
    elif 'fixed deposit' in question_lower or ' fd ' in question_lower or question_lower.endswith('fd'):
        return """**Fixed Deposit (FD):**

FD is a safe investment where you deposit money for a fixed period at a guaranteed interest rate.

**Features:**
- Duration: 7 days to 10 years
- Interest: 6-7.5% per year (varies by bank & tenure)
- Safe: Insured up to ₹5 lakh by DICGC
- Premature withdrawal: Allowed with penalty

**Types:**
- **Regular FD**: Standard fixed deposits
- **Tax-Saver FD**: 5-year lock-in, 80C benefit
- **Senior Citizen FD**: Extra 0.5% interest

**Tax:**
- Interest is taxable as per your income slab
- TDS deducted if interest > ₹40,000/year (₹50,000 for seniors)

**Returns Example:**
- Amount: ₹1 lakh
- Rate: 7% for 5 years
- Maturity: ~₹1.4 lakhs

**Best For:** Short-term goals, emergency fund, risk-averse investors

**Tip**: Compare rates across banks before investing!"""

    # Insurance related
    elif any(word in question_lower for word in ['insurance', 'term plan', 'life insurance', 'health insurance']):
        if 'term' in question_lower or 'life' in question_lower:
            return """**Life Insurance / Term Insurance:**

**What is Term Insurance?**
Pure life cover - if you die during the policy term, your family gets the sum assured. No maturity benefit.

**Why You Need It:**
- Replace your income if something happens to you
- Pay off loans (home loan, etc.)
- Secure family's financial future
- Children's education

**How Much Coverage:**
- General rule: 10-15x your annual income
- Example: Income ₹6 lakh → Coverage ₹60-90 lakhs

**Cost:**
Very affordable! ₹50 lakh cover for 30-year-old = ~₹8,000-10,000/year

**Key Features:**
- Pure protection, no investment
- Tax benefit under Section 80C (premium)
- Tax-free payout under Section 10(10D)

**When to Buy:** As early as possible (premiums lower when young)

**Top Insurers:** LIC, HDFC Life, ICICI Prudential, Max Life

**Avoid:** Mixing insurance with investment (ULIPs, Endowment) - buy pure term + invest separately**"""

        else:
            return """**Health Insurance:**

Protection against medical expenses - hospital bills, surgeries, treatments.

**Coverage:**
- Hospitalization expenses
- Pre and post-hospitalization
- Daycare procedures
- Ambulance charges
- Some plans cover OPD too

**Sum Insured:**
- Individual: ₹5-10 lakhs minimum
- Family: ₹10-20 lakhs recommended
- Consider super top-up for extra coverage

**Tax Benefits:**
- Section 80D deduction
- Self & family: Up to ₹25,000
- Parents: Additional ₹25,000
- Senior citizen parents: ₹50,000

**Key Features to Look For:**
- No claim bonus (coverage increases)
- Room rent limit (higher the better)
- Co-payment (lower the better)
- Network hospitals (more the better)
- Waiting period (shorter the better)

**Cost:** ₹30-year-old, ₹5L cover = ~₹7,000-10,000/year

**Tip**: Buy early! Premiums low, no pre-existing conditions"""

    # Income related
    elif any(word in question_lower for word in ['increase income', 'earn money', 'side hustle', 'extra income']):
        return """**Ways to Increase Income:**

**1. Salary Negotiation:**
- Research market salary for your role
- Highlight achievements and value
- Ask for 10-20% raise during appraisal
- Consider job switch for bigger hike

**2. Skill Development:**
- Learn high-demand skills (coding, design, marketing)
- Get certifications in your field
- Freelance with your new skills

**3. Side Hustles:**
- **Online**: Content writing, graphic design, tutoring, YouTube
- **Offline**: Consulting, coaching, photography
- **Passive**: Blogging, affiliate marketing, online courses

**4. Part-time Work:**
- Weekend gigs
- Freelance projects
- Remote work opportunities

**5. Investments:**
- Stock market dividends
- Rental income from property
- Interest from FD/bonds

**6. Sell Unused Items:**
- Electronics, books, clothes on OLX, Facebook
- Declutter and earn

**Popular Platforms:**
- Upwork, Fiverr (freelancing)
- Unacademy, Vedantu (teaching)
- Zomato, Swiggy (delivery on weekends)

**Start Small**: Begin with 1-2 hours daily, scale up gradually"""

    # Default helpful response
    else:
        # Try to understand the intent better
        if '?' in question:
            return f"""I'd love to help answer: **"{question}"**

I specialize in these financial topics:

**📚 Definitions & Basics:**
- What is savings/investment/SIP/mutual fund/stocks?
- What is PPF/FD/insurance/credit score?

**💰 Money Management:**
- How to save more money?
- How to create a budget?
- How to track expenses?

**📈 Investments:**
- Best investment options for beginners
- SIP vs lump sum investment
- How to start investing in stocks?

**💸 Tax Planning:**
- How to save tax under Section 80C?
- Old vs New tax regime
- Tax deductions available

**🏦 Debt & Credit:**
- How to pay off loans faster?
- How to improve credit score?
- Credit card debt management

**🎯 Financial Planning:**
- Emergency fund planning
- Retirement planning
- How to increase income?

**Try rephrasing your question** to match one of these topics, or ask something specific!

**Example questions:**
- "What is SIP?"
- "How can I save more money?"
- "Best way to invest ₹10,000 monthly"
- "How to save tax?"
"""
        else:
            return f"""I'm your AI Financial Assistant! 💰

**You asked:** "{question}"

**I can help you with:**

**💡 Quick Topics:**
Type these questions to get instant detailed answers:
- "What is savings?" or "What is SIP?"
- "How to save money?" or "How to budget?"
- "Best investment for beginners"
- "Tax saving tips" or "What is 80C?"
- "How to build emergency fund?"
- "Ways to increase income"

**🎯 Goal Planning:**
Go to the Goals page to create savings plans with AI assistance!

**📊 Budget Analysis:**
Track your expenses on the Dashboard for insights!

**Need something specific?** Just ask a clear question!

**Examples:**
- "What is a mutual fund?"
- "How do I start investing?"
- "Tips to pay off credit card debt"
"""
