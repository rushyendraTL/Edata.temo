from openai import Client
from dotenv import load_dotenv
import os

load_dotenv()

client = Client(api_key=os.getenv('OPENAI_API_KEY'))


def generate_abi_insight(plot_data, filter_data):
    system_prompt = """You are an expert insurance data analyst generating concise insights for vehicle underwriters.

    ## CONTEXT
    This visualization shows statistics around vehicle specification queries that underwriters from insurance companies request from eData, a vehicle information provider. These queries reflect underwriting interest and market exposure across various vehicle attributes.

    ## INPUT DATA
    The prompt contains two data elements:
    1. FIGURE DATA: Raw Plotly JSON containing all chart data
    2. FILTER DATA: Applied dashboard filters

    ## YOUR TASK
    First, analyze the Plotly JSON to:
    - Identify the chart type and key metrics being visualized
    - Extract the most significant data points and their values
    - Determine what vehicle attribute is being analyzed (make, model, year, etc.)

    Then provide EXACTLY two paragraphs (no headings, no bullet points):

    Paragraph 1 (10-25 words): Analyze the data for underwriting implications. Identify risk concentrations and exposure patterns. Reference specific percentages and values from the data.

    Paragraph 2 (10-25 words): Provide specific underwriting strategy recommendations based on the data. Focus on capacity allocation, risk selection, or pricing approaches that directly address the patterns observed.

    Keep your entire response under 50 words. Use short, declarative sentences. Do not use headers, bullet points, or any other formatting - just two clean paragraphs.
    """

    input_prompt_template = f"""Please analyze this vehicle underwriting data visualization:

    FIGURE DATA:
    {plot_data}

    FILTER DATA:
    {filter_data}
    """

    response = client.chat.completions.create(
        model='gpt-4.1-mini',
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': input_prompt_template}
        ],
    )

    return response.choices[0].message.content
