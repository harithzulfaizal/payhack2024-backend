import os
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union
from PIL import Image
from termcolor import colored

import autogen
from autogen import Agent, AssistantAgent, ConversableAgent, UserProxyAgent
from autogen.agentchat.contrib.img_utils import _to_pil, get_image_data
from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.coding import LocalCommandLineCodeExecutor
from autogen.coding.jupyter import JupyterCodeExecutor
from autogen.code_utils import DEFAULT_MODEL, UNKNOWN, content_str, execute_code, extract_code, infer_lang

import asyncio
import json_repair
import polars as pl

from utils.models import get_completions
from utils.db import retrieve_from_db, convert_json_to_sql, insert_into_db, get_users
from utils.misc import get_nearby_places

from prompts.template import transactions_summary_template

config_list_gemini = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={
        "model": ["gemini-1.5-pro", "gemini-1.5-flash"],
    },
)

executor = LocalCommandLineCodeExecutor(
    timeout=20,  # Timeout for each code execution in seconds.
    work_dir="coding/",  # Use the temporary directory to store the code files.
)

coder = AssistantAgent(
    name="Coder",
    llm_config={"config_list": config_list_gemini},
    max_consecutive_auto_reply=10,
    description="I am good at writing code",
)

pm = AssistantAgent(
    name="Personal finance analyst",
    system_message="Analyse financial data of client, give recommendations and insights",
    llm_config={"config_list": config_list_gemini},
    max_consecutive_auto_reply=10,
    description="I am good at managing personal finance.",
)

user_proxy = UserProxyAgent(
    name="User_proxy",
    code_execution_config={"executor": executor, "last_n_messages": 20},
    human_input_mode="NEVER",
    is_termination_msg=lambda x: content_str(x.get("content")).find("TERMINATE") >= 0,
    description="I stands for user, and can run code.",
)

groupchat = autogen.GroupChat(agents=[user_proxy, coder, pm], messages=[], max_round=12)

manager = autogen.GroupChatManager(
    groupchat=groupchat,
    llm_config={"config_list": config_list_gemini},
    is_termination_msg=lambda x: content_str(x.get("content")).find("TERMINATE") >= 0,
)

async def get_trxn_viz(user_id, monthly=None):
    print(retrieve_from_db(f"SELECT * FROM transactions a JOIN accounts b ON a.account_id = b.account_id WHERE user_id = {user_id} AND value_datetime >= CURRENT_DATE - INTERVAL '{monthly} MONTH' ORDER BY value_datetime DESC"))
    user_transactions = json_repair.loads(retrieve_from_db(f"SELECT * FROM transactions a JOIN accounts b ON a.account_id = b.account_id WHERE user_id = {user_id} AND value_datetime >= CURRENT_DATE - INTERVAL '{monthly} MONTH' ORDER BY value_datetime DESC"))
    
    df = pl.DataFrame(user_transactions)

    data = {
        "bar_chart": (
            df.group_by("transaction_type")
            .agg(pl.count().alias("value"))
            .rename({"transaction_type": "category"})
            .to_dicts()
        ),
        "linear_chart": (
            df.group_by("value_datetime")
            .agg(pl.col("transaction_amount").sum().alias("value"))
            .sort("value_datetime")
            .to_dicts() 
        ),
        "pie_chart": (
            df.group_by("merchant_name")
            .agg(pl.count().alias("value"))
            .to_dicts()
        )
    }
    return data

async def get_trxn_summary(user_id, monthly=1):
    data = await get_trxn_viz(user_id, monthly)

    message = f"""Based on the data below for a user,
    generate actionable insights of their spending habits based on category types - Food, Utilities, Groceries, Online Shopping.
    
    #DATA:
    {data}

    Analyze and output "observation", "recommendation" and "escalate" which is a binary flag of 0 or 1 to determine whether
    further personalized recommendations can be done for each category in a JSON."""

    print(message)

    result = json_repair.loads(await get_completions(message, "#OUTPUT:"))

    print(result)
    
    for k, v in result.items():
        user = json_repair.loads(get_users(user_id))
        if type(user) == list: user = user[0]
        location = user['address_line_1'] + " " + user['city']
        if k == "Food":
            if v['escalate'] == 1:
                restaurants = get_nearby_places(location, "restaurants budget-friendly")

                message = f"""Based on the previous recommendation on Food and the list of budget-friendly restaurants near your place at {location},
                generate a new recommendation which suggests some these places, alongside option to cook their own meals in one excerpt.

                #PREVIOUS RECOMMENDATION:
                {v['recommendation']}

                #LIST OF RESTAURANTS:
                {restaurants}"""

                _ = await get_completions(message, "#OUTPUT:")
                print(_)

                result['Food']['recommendation'] = _              
        if k == "Groceries":
            if v['escalate'] == 1:
                groceries = get_nearby_places(location, "groceries budget-friendly")

                message = f"""Based on the previous recommendation on Groceries and the list of budget-friendly groceries near your place at {location},
                generate a new recommendation which suggests some these places.

                #PREVIOUS RECOMMENDATION:
                {v['recommendation']}

                #LIST OF GROCERIES PLACE:
                {groceries}"""

                _ = await get_completions(message, "#OUTPUT:")
                print(_)

                result['Groceries']['recommendation'] = _ 
    
    print(result)
    return result


async def get_trxn_summary_(user_id):
    user_profile = json_repair.loads(get_users(user_id))
    user_summary = json_repair.loads(retrieve_from_db(f"SELECT * FROM general_insights WHERE user_id = {user_id}"))
    user_transactions = json_repair.loads(retrieve_from_db(f"SELECT * FROM transactions a JOIN accounts b ON a.account_id = b.account_id WHERE user_id = {user_id} LIMIT 200"))

    res = await get_completions(transactions_summary_template.format_map({"user_profile": user_profile, "user_summary": user_summary, "user_transactions": user_transactions}), "#OUTPUT")
    print(res)

# asyncio.run(get_trxn_summary(5))