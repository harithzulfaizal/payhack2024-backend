import autogen

config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={
        "model": ["gemini-1.5-pro", "gemini-1.5-flash"],
    },
)
