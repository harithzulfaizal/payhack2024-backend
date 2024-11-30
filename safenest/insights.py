import asyncio
import json_repair
import pprint

from utils.models import get_completions
from utils.db import get_users, get_accounts, get_balances, convert_json_to_sql, insert_into_db

from prompts.template import accounts_template, balances_template, general_insights_template

async def get_user_summary(user_id):
    user = get_users(user_id)
    account = get_accounts(user_id)
    balance = get_balances(user_id)

    res = await get_completions(accounts_template.format_map({"user_profile": str(user), "account": str(account)}), "#OUTPUT:")
    res1 = await get_completions(balances_template.format_map({"user_profile": str(user), "balance": str(balance)}), "#OUTPUT:")

    input_data = [json_repair.loads(res), json_repair.loads(res1)]
    summary_dict = {
        'linked_accounts': {
            'total_count': input_data[0]['linked_accounts_count'],
            'sharia_compliant_count': input_data[0]['sharia_compliant_accounts_count'],
            'non_sharia_compliant_count': input_data[0]['non_sharia_compliant_accounts_count'],
            'provider_types': input_data[0]['provider_types']
        },
        'financial_behavior': input_data[0]['financial_behavior'],
        'financial_health': input_data[1]['financial_health'],
        'activity_monitoring': input_data[1]['activity_monitoring'],
        'segmentation': input_data[1]['segmentation'],
        'risk_and_compliance': input_data[1]['risk_and_compliance'],
        'retention_and_loyalty_programs': input_data[1]['retention_and_loyalty_programs']
    }

    return summary_dict

async def generate_general_insights(summary_dict):
    res = await get_completions(general_insights_template.format_map({"summary_dict": summary_dict}), "#OUTPUT:")
    print(res)
    general_insights = json_repair.loads(res)

    return general_insights

async def main():
    ids = list(range(5,11))

    for id in ids:
        user_acc_summary = await get_user_summary(id)
        general_insights = await generate_general_insights(user_acc_summary)

        insert_query = await convert_json_to_sql(general_insights, 'general_insights', id)
        print(insert_query)
        insert_into_db(insert_query)

asyncio.run(main())
