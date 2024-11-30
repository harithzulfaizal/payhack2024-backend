import os
import json
import psycopg2
from psycopg2 import sql
from datetime import date, datetime
from decimal import Decimal

from .models import get_completions

conn_params = "postgresql://neondb_owner:CG4zi5OygUKb@ep-flat-band-a1icda59.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

async def convert_json_to_sql(insert_dict, table, where):
    res = await get_completions(
        system_prompt=f"Based on the JSON below, create a SQL query for Postgres to insert into table '{table}' where user_id = {where}." +
            "Do not explain the query. Only output the SQL query in ```sql and ```:" +
            f"\n\n#JSON DATA:\n{insert_dict}",
        text="#OUTPUT:"
        )
    
    res = res.replace("```sql", "").replace("```", "")
    return res

def custom_json_serializer(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()  # Convert date/datetime to ISO 8601 string
    elif isinstance(obj, Decimal):
        return float(obj)  # Convert Decimal to float
    raise TypeError(f"Type {type(obj)} not serializable")

def insert_into_db(query):
    try:
        conn = psycopg2.connect(conn_params)
        cursor = conn.cursor()

        cursor.execute(query)
        conn.commit()  # Commit changes

    except psycopg2.DatabaseError as e:
        print(f"Error: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

def retrieve_from_db(query):
    try:
        conn = psycopg2.connect(conn_params)
        cursor = conn.cursor()

        cursor.execute(query)
        
        rows = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]

        result = [dict(zip(colnames, row)) for row in rows]

        return json.dumps(result, default=custom_json_serializer, indent=4)

    except psycopg2.DatabaseError as e:
        print(f"Error: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

def get_users(user_id):
    return retrieve_from_db(f"SELECT * FROM users WHERE user_id = {user_id}")

def get_accounts(user_id):
    return retrieve_from_db(f"SELECT * FROM accounts WHERE user_id = {user_id}")

def get_balances(user_id):
    return retrieve_from_db(f"SELECT * FROM balances a JOIN accounts b on a.account_id = b.account_id WHERE user_id = {user_id}")

