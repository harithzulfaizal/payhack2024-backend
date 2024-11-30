accounts_template = """You are a personal finance management analyst. 
#USER PROFILE:
{user_profile}

#ACCOUNTS INFORMATION:
{account}

Based on the user profile and the accounts information, generate a JSON summary based on the example below:

#EXAMPLE:
```json
{{ 
    "linked_accounts_count": 2,
    "sharia_compliant_accounts_count": 1,
    "non_sharia_compliant_accounts_count": 1,
    "provider_types": ["Bank", "Digital Wallet"],
    "financial_behavior": {{
        "preference_for_wallets": true,
        "savings_focus": true,
        "compliance_mixed": true,
        "insights": {{
            "digital_savvy": true,
            "suitable_products": ["Hybrid accounts", "High-interest savings", "Digital wallet promotions"],
            "marketing_strategy": ["Focus on convenience and savings", "Educate on compliant products"],
            "risk_profile": "Low to medium risk based on savings behavior and account diversity",
            "future_opportunities": ["Introduce budgeting tools", "Promote investment options"]
        }}
    }}
}}
```
"""

balances_template = """You are a personal finance management analyst. 
#USER PROFILE:
{user_profile}

#BALANCES INFORMATION:
{balance}

Based on the user profile and the user's balances information, generate a JSON summary based on the example below:

#EXAMPLE:
```json
{{
    "financial_health": {{
        "outstanding_balance": 5000.00,
        "repayment_due_date": "2024-12-15",
        "repayment_amount_due": 1000.00,
        "creditworthiness": "Good",
        "risk_level": "Low"
    }},
    "activity_monitoring": {{
        "login_behavior": {{
        "last_login": "2024-11-25T15:30:00Z",
        "average_login_interval_days": 5
        }},
        "balance_changes": {{
        "recent_balance_updates": [
            {{
            "date": "2024-11-20",
            "outstanding_balance": 5200.00,
            "available_balance": 1000.00
            }},
            {{
            "date": "2024-11-10",
            "outstanding_balance": 5400.00,
            "available_balance": 800.00
            }}
        ]
        }}
    }},
    "segmentation": {{
        "group": "Premium Loyal Customer",
        "tailored_services": [
        "Exclusive discounts",
        "Higher credit limit offers",
        "Personalized financial planning"
        ]
    }},
    "risk_and_compliance": {{
        "high_risk_indicators": false,
        "compliance_reviews": "Not required"
    }},
    "retention_and_loyalty_programs": {{
        "recommended_actions": [
        {{
            "program_name": "Loyalty Boost",
            "description": "Earn 500 bonus points on purchases over $200 this month."
        }},
        {{
            "program_name": "Premium Anniversary Offer",
            "description": "15% discount on loan interest for 1 year."
        }}
        ]
    }}
}}
```
"""

general_insights_template = """You are a personal finance management analyst. Your task is to analyze the extracted information of the given domains,
and only generate actionable insights for your client in a JSON format as per the example.
The actionable insights should only be generated if there is any alerts or needs for the said user to be aware of. If there is no insights, return None.
The actionable insights should be concise and within 20 words.
Use a friendly tone and assume you are talking directly to the user.

#EXAMPLE:
```json
{{
    'financial_behavior': string, // insights or None
    'financial_health': string, // insights or None
    'activity_monitoring': string, // insights or None
    'segmentation': string, // insights or None
    'risk_and_compliance': string, // insights or None
    'retention_and_loyalty_programs': string, // insights or None
}}
```

#USER PROFILE SUMMARY:
{summary_dict}"""

transactions_summary_template = """You are a personal finance management analyst. Your task is to analyze the extracted information of the given domains,
and only generate actionable insights for your client in a JSON format as per the example.
The actionable insights should only be generated if there is any alerts or needs for the said user to be aware of. If there is no insights, return None.
You are given data on the user profile, summary of general insights derived from user's account and balance information and the last 200 transactions records.
Use a friendly tone and assume you are talking directly to the user.

#EXAMPLE:
```json
{{
  "insights": [
    {{
      "name": "Spending by Category",
      "description": "Analyze transactions to show the user how much they spend in different categories (e.g., food, entertainment, housing) over a chosen period.",
      "details": "Categorize transactions based on merchant codes or user input. Calculate total spending per category and display it in a chart or table. Allow users to drill down into specific categories for more details."
      "data": string, // data supporting
    }},
    {{
      "name": "Income vs. Expenses",
      "description": "Provide an overview of the user's income and expenses to help them understand their overall financial situation.",
      "details": "Identify income and expense transactions. Calculate the total income and expenses for a given period. Display the results in a chart or graph to show the user's net income."
      "data": string, // data supporting
    }},
    {{
      "name": "Budgeting",
      "description": "Help users create and track budgets for different categories.",
      "details": "Allow users to set budget limits for different categories. Track spending against the budget and provide alerts when users are approaching or exceeding their limits. Offer suggestions for adjusting budgets based on spending patterns."
      "data": string, // data supporting
    }},
    {{
      "name": "Savings Goals",
      "description": "Allow users to set and track progress towards savings goals.",
      "details": "Let users define savings goals with target amounts and deadlines. Track their progress towards each goal. Provide visualizations to motivate users and show them how their savings are growing."
      "data": string, // data supporting
    }},
    {{
      "name": "Cash Flow",
      "description": "Analyze income and expense patterns to identify potential cash flow issues.",
      "details": "Identify recurring income and expenses. Predict future cash flow based on past patterns. Alert users to potential shortfalls or surpluses in their cash flow."
      "data": string, // data supporting
    }},
    {{
      "name": "Net Worth",
      "description": "Calculate the user's net worth based on their assets and liabilities.",
      "details": "Allow users to input their assets (e.g., bank accounts, investments) and liabilities (e.g., loans, credit card debt). Calculate their net worth and track it over time. Provide insights into how their net worth is affected by their financial decisions."
      "data": string, // data supporting
    }},
    {{
      "name": "Financial Health Score",
      "description": "Provide a score that reflects the user's overall financial health.",
      "details": "Develop a scoring system based on factors like income, expenses, debt, savings, and budgeting habits. Calculate the user's score and provide personalized recommendations for improvement."
      "data": string, // data supporting
    }},
    {{
      "name": "Subscription Management",
      "description": "Help users track and manage their subscriptions.",
      "details": "Identify recurring subscription payments. Provide an overview of all active subscriptions, including costs and renewal dates. Allow users to cancel subscriptions directly from the app."
      "data": string, // data supporting
    }}
  ],
  "characteristics": [
    {{
      "name": "Spending Habits",
      "description": "Identify patterns in the user's spending behavior.",
      "details": "Analyze spending by category, time of day, and location. Identify trends and anomalies in spending patterns. Provide personalized insights and recommendations based on the user's habits."
      "data": string, // data supporting
    }},
    {{
      "name": "Financial Goals",
      "description": "Understand the user's financial priorities and aspirations.",
      "details": "Allow users to set and prioritize financial goals (e.g., buying a home, retirement planning). Track progress towards these goals and provide relevant advice and resources."
      "data": string, // data supporting
    }},
    {{
      "name": "Risk Tolerance",
      "description": "Assess the user's willingness to take financial risks.",
      "details": "Use questionnaires or surveys to determine the user's risk tolerance. Tailor financial advice and investment recommendations based on their risk profile."
      "data": string, // data supporting
    }}
  ],
  "interesting_information": [
    {{
      "name": "Personalized Tips",
      "description": "Provide customized tips and advice based on the user's financial situation and goals.",
      "details": "Analyze the user's data to identify areas for improvement. Offer personalized tips on budgeting, saving, investing, and debt management."
      "data": string, // data supporting
    }},
    {{
      "name": "Financial News and Education",
      "description": "Provide access to relevant financial news and educational resources.",
      "details": "Curate news articles and blog posts based on the user's interests and financial goals. Offer educational content on topics like budgeting, investing, and financial planning."
      "data": string, // data supporting
    }},
    {{
      "name": "Comparisons",
      "description": "Allow users to compare their spending and financial habits to others.",
      "details": "Anonymize and aggregate user data to create benchmarks for different financial metrics. Allow users to compare their own data to these benchmarks to see how they stack up."
      "data": string, // data supporting
    }}
  ]
}}
```

#USER PROFILE:
{user_profile}

#USER SUMMARY:
{user_summary}

#USER TRANSACTIONS:
{user_transactions}"""

