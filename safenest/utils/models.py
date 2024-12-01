import os
import google.generativeai as genai

genai.configure(api_key="<insert_api_key>")

async def get_completions(system_prompt, text):
    # Create the model
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

    response = await model.generate_content_async(text)

    # chat_session = model.start_chat(
    # history=[
    # ]
    # )

    # response = chat_session.send_message(text)

    return response.text