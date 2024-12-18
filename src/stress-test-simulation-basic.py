import psycopg2
import json

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

print(f"Setting monthly income to 0...")

income_salary = 0  

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
print(f"Initial savings: ${savings}")
print(f"Initial investments: ${investments}")
print(f"Monthly expenses: ${total_monthly_expenses}")

result = {}
while True:
    net_cash_flow = income - total_monthly_expenses
    result[str(months)] = {
        "savings": str(round(savings, 2)),
        "investments": str(round(investments, 2)),
        "income": str(round(income, 2)),
        "net_cash_flow": str(round(net_cash_flow, 2))
    }
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
            months += 0.5
            print(f"Month {months}: Savings and investments depleted.")
            break
    months += 0.5
    print(
        f"Month {months}: Savings: ${savings:.2f}, Investments: ${investments:.2f}"
    )

print(f"Total months before funds run out: {months}")
print(result)
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