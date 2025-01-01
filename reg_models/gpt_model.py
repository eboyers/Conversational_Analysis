from openai import AzureOpenAI

def run_gpt(query, model):
    """
    Defines the usage of GPT models (3.5 turbo, 4 turbo, and 4o)
    """
    client = AzureOpenAI(
        api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx", # HIDDEN
        api_version="xxxxxxxxxxxxxx",
        azure_endpoint="https://xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.openai.azure.com/",
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system",
                "content": """You are an expert in analyzing SOAP (Subjective, Objective, Assessment, Plan) notes from clinical 
                              conversations to see if they meet MEAT (Monitoring, Evaluation, Assessment, Treatment) criteria."""},
            {"role": "user",
                "content": query}
        ],
        temperature=0, # fine-tune here
        top_p=0.8,
        max_tokens=1024
    )

    return response.choices[0].message.content
