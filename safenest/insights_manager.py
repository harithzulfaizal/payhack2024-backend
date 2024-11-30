import os
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

import chromadb
from PIL import Image
from termcolor import colored

import autogen
from autogen import Agent, AssistantAgent, ConversableAgent, UserProxyAgent
from autogen.agentchat.contrib.img_utils import _to_pil, get_image_data
from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.coding import LocalCommandLineCodeExecutor
from autogen.code_utils import DEFAULT_MODEL, UNKNOWN, content_str, execute_code, extract_code, infer_lang

from gemini_config import config_list

planner = autogen.AssistantAgent(
    name="planner",
    llm_config={"config_list": config_list},
    # the default system message of the AssistantAgent is overwritten here
    system_message="You are a helpful AI assistant. You suggest coding and reasoning steps for another AI assistant to accomplish a task. Do not suggest concrete code. For any action beyond writing code or reasoning, convert it to a step that can be implemented by writing code. For example, browsing the web can be implemented by writing code that reads and prints the content of a web page. Finally, inspect the execution result. If the plan is not good, suggest a better plan. If the execution is wrong, analyze the error and suggest a fix.",
)

coder = AssistantAgent(
    name="Coder",
    llm_config={"config_list": config_list},
    max_consecutive_auto_reply=10,
    description="I am good at writing code",
)

planner_user = autogen.UserProxyAgent(
    name="planner_user",
    max_consecutive_auto_reply=0,  # terminate without auto-reply
    human_input_mode="NEVER",
    code_execution_config={
        "use_docker": False
    },  # Please set use_docker=True if docker is available to run the generated code. Using docker is safer than running the generated code directly.
)

def ask_planner(message):
    planner_user.initiate_chat(planner, message=message)
    # return the last message received from the planner
    return planner_user.last_message()["content"]

message = """Tables and their columns in the database:

Table: users
    Column: user_id, Type: integer, NOT NULLABLE
    Column: first_name, Type: character varying, NOT NULLABLE
    Column: last_name, Type: character varying, NOT NULLABLE
    Column: middle_name, Type: character varying, NULLABLE
    Column: email, Type: character varying, NOT NULLABLE
    Column: password, Type: character varying, NOT NULLABLE
    Column: date_of_birth, Type: date, NULLABLE
    Column: phone_number, Type: character varying, NULLABLE
    Column: gender, Type: character varying, NULLABLE
    Column: profile_picture_url, Type: text, NULLABLE
    Column: address_line_1, Type: text, NULLABLE
    Column: address_line_2, Type: text, NULLABLE
    Column: city, Type: character varying, NULLABLE
    Column: state, Type: character varying, NULLABLE
    Column: postal_code, Type: character varying, NULLABLE
    Column: country, Type: character varying, NULLABLE
    Column: is_active, Type: boolean, NULLABLE
    Column: is_verified, Type: boolean, NULLABLE
    Column: last_login, Type: timestamp without time zone, NULLABLE
    Column: role, Type: character varying, NULLABLE
    Column: password_reset_token, Type: character varying, NULLABLE
    Column: password_reset_expiration, Type: timestamp without time zone, NULLABLE
    Column: preferences, Type: json, NULLABLE
    Column: language, Type: character varying, NULLABLE
    Column: timezone, Type: character varying, NULLABLE
    Column: subscription_status, Type: character varying, NULLABLE
    Column: loyalty_points, Type: integer, NULLABLE
    Column: create_date, Type: timestamp without time zone, NULLABLE
    Column: updated_date, Type: timestamp without time zone, NULLABLE
    Column: deleted_date, Type: timestamp without time zone, NULLABLE

Table: pensions
    Column: pension_id, Type: integer, NOT NULLABLE
    Column: user_id, Type: integer, NOT NULLABLE
    Column: epf_account_number, Type: character varying, NOT NULLABLE
    Column: total_contributions, Type: numeric, NULLABLE
    Column: employer_contributions, Type: numeric, NULLABLE
    Column: employee_contributions, Type: numeric, NULLABLE
    Column: contribution_date, Type: timestamp without time zone, NULLABLE
    Column: account_status, Type: character varying, NULLABLE

Table: transactions
    Column: transaction_id, Type: uuid, NOT NULLABLE
    Column: account_id, Type: character varying, NOT NULLABLE
    Column: bic_code, Type: character varying, NULLABLE
    Column: account_number, Type: character varying, NULLABLE
    Column: account_type, Type: character varying, NULLABLE
    Column: payment_scheme, Type: character varying, NULLABLE
    Column: credit_debit_indicator, Type: character varying, NULLABLE
    Column: transaction_type, Type: character varying, NULLABLE
    Column: transaction_amount, Type: numeric, NULLABLE
    Column: transaction_currency, Type: character varying, NULLABLE
    Column: account_currency_amount, Type: numeric, NULLABLE
    Column: account_currency, Type: character varying, NULLABLE
    Column: fx_rate, Type: numeric, NULLABLE
    Column: status, Type: character varying, NULLABLE
    Column: booking_datetime, Type: timestamp without time zone, NULLABLE
    Column: value_datetime, Type: timestamp without time zone, NULLABLE
    Column: merchant_category_code, Type: character varying, NULLABLE
    Column: merchant_name, Type: character varying, NULLABLE
    Column: merchant_address, Type: text, NULLABLE
    Column: merchant_postal_code, Type: character varying, NULLABLE
    Column: merchant_city, Type: character varying, NULLABLE
    Column: merchant_country, Type: character varying, NULLABLE
    Column: category, Type: character varying, NULLABLE
    Column: category_purpose_code, Type: character varying, NULLABLE
    Column: business_category_codes, Type: character varying, NULLABLE
    Column: msic, Type: character varying, NULLABLE
    Column: biller_code, Type: character varying, NULLABLE
    Column: biller_code_name, Type: character varying, NULLABLE
    Column: creditor_bic, Type: character varying, NULLABLE
    Column: creditor_agent_name, Type: character varying, NULLABLE
    Column: creditor_account_number, Type: character varying, NULLABLE
    Column: creditor_account_name, Type: character varying, NULLABLE
    Column: debitor_bic, Type: character varying, NULLABLE
    Column: debitor_agent_name, Type: character varying, NULLABLE
    Column: debitor_account_number, Type: character varying, NULLABLE
    Column: debitor_name, Type: character varying, NULLABLE

Table: accounts
    Column: account_id, Type: character varying, NOT NULLABLE
    Column: bic_code, Type: character varying, NOT NULLABLE
    Column: provider_type, Type: character varying, NOT NULLABLE
    Column: account_number, Type: character varying, NOT NULLABLE
    Column: account_type, Type: character varying, NOT NULLABLE
    Column: account_description, Type: character varying, NOT NULLABLE
    Column: account_holder_full_name, Type: character varying, NOT NULLABLE
    Column: id_type, Type: character varying, NOT NULLABLE
    Column: id_value, Type: character varying, NOT NULLABLE
    Column: account_holder_email_address, Type: character varying, NULLABLE
    Column: account_holder_mobile_number, Type: character varying, NULLABLE
    Column: product_type, Type: character varying, NOT NULLABLE
    Column: sharia_compliance, Type: character varying, NOT NULLABLE
    Column: user_id, Type: integer, NULLABLE

Table: balances
    Column: account_detail_id, Type: integer, NOT NULLABLE
    Column: account_id, Type: character varying, NOT NULLABLE
    Column: account_balance_datetime, Type: timestamp without time zone, NOT NULLABLE
    Column: outstanding_balance, Type: numeric, NULLABLE
    Column: pending_balance, Type: numeric, NULLABLE
    Column: available_balance, Type: numeric, NULLABLE
    Column: credit_limit, Type: numeric, NULLABLE
    Column: account_currency, Type: character varying, NOT NULLABLE
    Column: repayment_due_date, Type: date, NULLABLE
    Column: repayment_amount_due, Type: numeric, NULLABLE
    Column: repayment_frequency, Type: character varying, NULLABLE
    Column: maturity_date, Type: date, NULLABLE

Given the schema for the tables above, you are tasked to generate spending insights based on a user.
"""

ask_planner(message)