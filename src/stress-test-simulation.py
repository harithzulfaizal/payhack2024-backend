import psycopg2
import json
import calendar

user_id = 1 #hardcode for now
# Database connection parameters
conn_params = "postgresql://neondb_owner:CG4zi5OygUKb@ep-flat-band-a1icda59.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"
try:
    conn = psycopg2.connect(conn_params)
    cursor = conn.cursor()
    
    # Retrieve parameters for a specific user or scenario
    cursor.execute("""
        SELECT 
            income_salary,
            fixed_expenses_housing,
            fixed_expenses_utilities,
            fixed_expenses_insurance,
            variable_expenses_groceries,
            variable_expenses_transport,
            variable_expenses_lifestyle,
            variable_expenses_healthcare,
            loans_mortgage,
            loans_car_loan,
            loans_personal_loan,
            loans_credit_card_debt,
            investments_stock_market,
            investments_mutual_funds,
            savings_emergency_fund,
            savings_vacation_fund,
            savings_general_savings,
            savings_other_savings,
            id
        FROM stress_test_parameters
        WHERE user_id = %s
    """, (user_id,))

    simulation_parameters = cursor.fetchone()
except psycopg2.DatabaseError as e:
    print(f"Error: {e}")
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()


income_salary = simulation_parameters[0]
fixed_expenses_housing = simulation_parameters[1]
fixed_expenses_utilities = simulation_parameters[2]
fixed_expenses_insurance = simulation_parameters[3]
variable_expenses_groceries = simulation_parameters[4]
variable_expenses_transport = simulation_parameters[5]
variable_expenses_lifestyle = simulation_parameters[6]
variable_expenses_healthcare = simulation_parameters[7]
loans_mortgage = simulation_parameters[8]
loans_car_loan = simulation_parameters[9]
loans_personal_loan = simulation_parameters[10]
loans_credit_card_debt = simulation_parameters[11]
investments_stock_market = simulation_parameters[12]
investments_mutual_funds = simulation_parameters[13]
savings_emergency_fund = simulation_parameters[14]
savings_vacation_fund = simulation_parameters[15]
savings_general_savings = simulation_parameters[16]
savings_other_savings = simulation_parameters[17]
stress_test_parameters_id = simulation_parameters[18]

# Job loss scenario

print("Starting stress test simulation...")
print("Simulate no disaster scenario...")

# Calculate total monthly expenses
total_fixed_expenses = (
    fixed_expenses_housing + fixed_expenses_utilities + fixed_expenses_insurance
)
total_variable_expenses = (
    variable_expenses_groceries
    + variable_expenses_transport
    + variable_expenses_lifestyle
    + variable_expenses_healthcare
)
total_loan_payments = (
    loans_mortgage + loans_car_loan + loans_personal_loan + loans_credit_card_debt
)
total_monthly_expenses = (
    total_fixed_expenses + total_variable_expenses + total_loan_payments
)

# Total available funds
total_savings = (
    savings_emergency_fund
    + savings_vacation_fund
    + savings_general_savings
    + savings_other_savings
)
total_investments = investments_stock_market + investments_mutual_funds

# Simulation variables
savings = total_savings
investments = total_investments
income = income_salary
months = 0
print(f"Initial income: ${income}")
print(f"Initial savings: ${savings}")
print(f"Initial investments: ${investments}")
print(f"Monthly expenses: ${total_monthly_expenses}")

result = {}
result["before_disaster"] = []

while True:
    if months == 6:
        break
    net_cash_flow = income - total_monthly_expenses
    if net_cash_flow > 0:
        savings += net_cash_flow

    result["before_disaster"].append({
        "month" : str(months),
        "savings": str(round(savings, 2)),
        "investments": str(round(investments, 2)),
        "income": str(round(income, 2)),
        "net_cash_flow": str(round(net_cash_flow, 2))
    })
    if savings >= -net_cash_flow:
        # Use savings to cover expenses
        savings += net_cash_flow
    else:
        # Use remaining savings and dip into investments
        net_cash_flow_after_savings = net_cash_flow + savings
        savings = 0
        if investments >= -net_cash_flow_after_savings:
            investments += net_cash_flow_after_savings
        else:
            # Funds exhausted
            months += 1
            print(f"Month {months}: Savings and investments depleted.")
            break
    months += 1
    print(
        f"Month {months}: Savings: ${savings:.2f}, Investments: ${investments:.2f}"
    )

print(f"Total months before funds run out: {months}")
print('\n')
print(f"Setting monthly income to 0...")

# income_salary = 0  

# Simulation variables
savings = total_savings
investments = total_investments
income = 0
months = 0
print(f"Initial savings: ${savings}")
print(f"Initial investments: ${investments}")
print(f"Monthly expenses: ${total_monthly_expenses}")

result["after_disaster"] = []
while True:
    net_cash_flow = income - total_monthly_expenses
    result["after_disaster"].append({
        "month" : str(months),
        "savings": str(round(savings, 2)),
        "investments": str(round(investments, 2)),
        "income": str(round(income, 2)),
        "net_cash_flow": str(round(net_cash_flow, 2))
    })
    if savings >= -net_cash_flow:
        # Use savings to cover expenses
        savings += net_cash_flow
    else:
        # Use remaining savings and dip into investments
        net_cash_flow_after_savings = net_cash_flow + savings
        savings = 0
        if investments >= -net_cash_flow_after_savings:
            investments += net_cash_flow_after_savings
        else:
            # Funds exhausted
            months += 1
            print(f"Month {months}: Savings and investments depleted.")
            break
    months += 1
    print(
        f"Month {months}: Savings: ${savings:.2f}, Investments: ${investments:.2f}"
    )

print(f"Total months before funds run out: {months}")
print(result)

# Financial resilience score

# Calculate the occupation score out of 25%
# get the occupation of the user from the database
try:
    conn = psycopg2.connect(conn_params)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT job FROM users WHERE user_id = %s
    """, (user_id,))
    occupation = cursor.fetchone()
except psycopg2.DatabaseError as e:
    print(f"Error: {e}")
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()

occupation = occupation[0]
# Using LLM, categorise the occupation into blue or white collar 
import os
import google.generativeai as genai

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def get_completions(system_prompt, text):
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
        system_instruction=system_prompt
    )
    response = model.generate_content(text)
    return response.text
system_prompt = "Categorize the following occupation into one of blue collar, white collar. If blue collar, output 0.5. If white collar, output 1."
text = f"Occupation: {occupation}"

occupation_score = int(get_completions(system_prompt, text)) * 25

# Calculate the debt service ratio (DSR) score out of 25%
# Calculate the DSR
total_debt = loans_mortgage + loans_car_loan + loans_personal_loan + loans_credit_card_debt
dsr_score = total_debt / income_salary
if dsr_score >= 0.4:
    dsr_score = 0.33
elif 0.2 <= dsr_score < 0.39:
    dsr_score = 0.66
else:
    dsr_score = 1
dsr_score = dsr_score * 25 

# Calculate the savings score out of 25%
savings_score = total_savings / income_salary
if savings_score >= 6:
    savings_score = 1
elif 3 <= savings_score < 6:
    savings_score = 0.66
else:
    savings_score = 0.33
savings_score = savings_score * 25

# Calculate the cash flow score out of 25%
cash_flow_score = total_monthly_expenses / income_salary
if cash_flow_score >= 0.8:
    cash_flow_score = 0.33
elif 0.4 <= cash_flow_score < 0.79:
    cash_flow_score = 0.66
else:
    cash_flow_score = 1
cash_flow_score = cash_flow_score * 25

# Calculate the financial resilience score
financial_resilience_score = occupation_score + dsr_score + savings_score + cash_flow_score

print(f"Final score: {financial_resilience_score}")
result["financial_resilience_score"] = f"{financial_resilience_score}%"

# Prepare data for database insertion
result_json = json.dumps(result)

# Insert or update the result in the stress_test_results table
try:
    # Reconnect to the database
    conn = psycopg2.connect(conn_params)
    cursor = conn.cursor()
    
    # Check if an entry with the same stress_test_id exists
    cursor.execute("""
        SELECT id FROM stress_test_results
        WHERE stress_test_id = %s
    """, (stress_test_parameters_id,))
    existing_entry = cursor.fetchone()
    
    if existing_entry:
        # Update the existing entry
        cursor.execute("""
            UPDATE stress_test_results
            SET result = %s, user_id = %s, created_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (result_json, user_id, existing_entry[0]))
        print(f"Updated stress_test_results entry with id {existing_entry[0]}.")
    else:
        # Insert a new entry
        cursor.execute("""
            INSERT INTO stress_test_results (user_id, stress_test_id, result)
            VALUES (%s, %s, %s)
        """, (user_id, stress_test_parameters_id, result_json))
        print("Inserted new stress_test_results entry.")
    
    # Commit the transaction
    conn.commit()
    
except psycopg2.DatabaseError as e:
    print(f"Database error: {e}")
    if conn:
        conn.rollback()
finally:
    if cursor:
        cursor.close()
    if conn:
        conn.close()