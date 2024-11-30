import pandas as pd

def generate_spending_insights(user_id, transactions_df, balances_df):
    """
    Generates spending insights for a given user based on their transactions.

    Args:
        user_id: The ID of the user.
        transactions_df: Pandas DataFrame containing transaction data.
        balances_df: Pandas DataFrame containing balance data.

    Returns:
        A dictionary containing spending insights.  Returns None if no data is found.
    """


    user_transactions = transactions_df[transactions_df['account_id'].isin(
        balances_df[balances_df['user_id'] == user_id]['account_id']
    )]


    if user_transactions.empty:
        return None

    # Basic Spending Insights
    total_spending = abs(user_transactions[user_transactions['credit_debit_indicator'] == 'Debit']['transaction_amount'].sum())
    average_transaction = abs(user_transactions[user_transactions['credit_debit_indicator'] == 'Debit']['transaction_amount'].mean())

    # Spending by Category
    spending_by_category = user_transactions.groupby('category')['transaction_amount'].sum().abs().to_dict()

    # Spending Trends Over Time (Monthly)
    user_transactions['month'] = user_transactions['booking_datetime'].dt.to_period('M')  # Extract month
    monthly_spending = user_transactions.groupby('month')['transaction_amount'].sum().abs()


    # Current Account Balances
    current_balances = balances_df[balances_df['user_id'] == user_id][['account_id', 'available_balance', 'account_currency']].to_dict('records')

    insights = {
        "total_spending": total_spending,
        "average_transaction": average_transaction,
        "spending_by_category": spending_by_category,
        "monthly_spending_trend": monthly_spending.to_dict(),
        "current_balances": current_balances
    }


    # Advanced Insights (Examples - can be expanded)
    if 'Groceries' in spending_by_category:
        insights['grocery_spending'] = spending_by_category['Groceries']
    if 'Entertainment' in spending_by_category:
        insights['entertainment_spending'] = spending_by_category['Entertainment']



    return insights




# Example Usage (Assuming you have loaded your data into Pandas DataFrames)
# transactions = pd.read_csv("transactions.csv")  # Replace with your data loading method
# balances = pd.read_csv("balances.csv") # Replace with your data loading method

# user_insights = generate_spending_insights(123, transactions, balances) # Example user ID

# if user_insights:
#     print(user_insights)
# else:
#     print("No transaction data found for this user.")
