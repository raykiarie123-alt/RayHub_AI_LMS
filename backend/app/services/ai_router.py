from app.services.gemini_client import ask_gemini
from app.services.deepseek_client import ask_deepseek


class AIError(Exception):
    pass


# ── CPA topic guard ────────────────────────────────────────────────────────────
# These keywords cover the full KASNEB CPA syllabus and related study topics.
CPA_KEYWORDS = {
    # Core CPA subjects
    "accounting", "audit", "auditing", "tax", "taxation", "finance", "financial",
    "management", "economics", "law", "governance", "ethics", "reporting",
    "costing", "cost", "budget", "budgeting", "revenue", "expenditure",
    "ledger", "journal", "trial balance", "balance sheet", "income statement",
    "cash flow", "depreciation", "amortisation", "amortization", "accrual",
    "prepayment", "debtors", "creditors", "receivable", "payable", "equity",
    "liability", "asset", "capital", "profit", "loss", "dividend", "interest",
    "bank reconciliation", "vat", "paye", "withholding", "corporation tax",
    "kasneb", "cpa", "atd", "cs", "ccp", "icpak",
    # Audit & assurance
    "internal control", "risk", "materiality", "sampling", "evidence",
    "assertion", "opinion", "going concern", "fraud", "misstatement",
    # Finance & investment
    "npv", "irr", "wacc", "portfolio", "bond", "share", "stock", "derivative",
    "hedge", "investment", "valuation", "working capital", "liquidity", "ratio",
    "solvency", "profitability", "gearing", "leverage",
    # Economics
    "supply", "demand", "elasticity", "inflation", "gdp", "monetary policy",
    "fiscal policy", "market", "competition", "monopoly", "oligopoly",
    # Law & governance
    "contract", "company", "director", "shareholder", "constitution", "statute",
    "regulation", "compliance", "insolvency", "liquidation", "agency",
    "corporate governance", "board",
    # General study/exam help
    "explain", "define", "calculate", "compute", "difference between",
    "example of", "how to", "what is", "meaning of", "formula",
    "journal entry", "double entry", "debit", "credit",
}

OFF_TOPIC_RESPONSE = (
    "I'm RayHub's CPA Study Assistant — I can only help with CPA and accounting-related topics. "
    "Your question appears to be outside that scope.\n\n"
    "Try asking me about topics like:\n"
    "• Financial Accounting & Reporting\n"
    "• Auditing & Assurance\n"
    "• Taxation\n"
    "• Management Accounting\n"
    "• Finance & Investment\n"
    "• Business Law & Ethics\n"
    "• Economics\n\n"
    "How can I help you with your CPA studies?"
)

CPA_SYSTEM_PROMPT = """You are RayHub AI Tutor, a specialized assistant for KASNEB CPA (Certified Public Accountant) students in Kenya.

Your role:
- Answer questions ONLY about CPA subjects: Financial Accounting, Management Accounting, Auditing & Assurance, Taxation, Finance & Investment, Business Law, Economics, and Governance & Ethics.
- Provide clear, accurate, exam-focused explanations tailored to KASNEB CPA syllabi.
- Use practical examples, journal entries, and step-by-step workings where helpful.
- If a question is not related to CPA studies or accounting, politely decline and redirect the student.

Do NOT answer questions about unrelated topics such as cooking, sports, entertainment, politics, or general knowledge outside of business/accounting."""


def _is_cpa_related(prompt: str) -> bool:
    """Return True if the prompt contains at least one CPA-related keyword."""
    lower = prompt.lower()
    return any(keyword in lower for keyword in CPA_KEYWORDS)


def generate_ai_response(prompt: str) -> str:
    # Guard: reject off-topic questions before hitting the AI API
    if not _is_cpa_related(prompt):
        return OFF_TOPIC_RESPONSE

    # Prepend the system context to the prompt
    full_prompt = f"{CPA_SYSTEM_PROMPT}\n\nStudent question: {prompt}"

    try:
        print("Trying Gemini...")
        return ask_gemini(full_prompt)
    except Exception as e:
        print(f"Gemini failed → switching to DeepSeek: {e}")
        try:
            print("Trying DeepSeek...")
            return ask_deepseek(full_prompt)
        except Exception as e2:
            print(f"Both failed: {e2}")
            raise AIError("All AI providers are unavailable.")