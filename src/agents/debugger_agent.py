import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def fix_code(faulty_code: str, error_traceback: str) -> str:
    """
    Fix Python code based on error traceback using OpenAI's API.
    
    Args:
        faulty_code (str): The code that caused an error
        error_traceback (str): The full error traceback message
        
    Returns:
        str: Corrected Python code
    """
    # Load API key from environment variables
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found in environment variables")
    
    # Set up the OpenAI client
    client = openai.OpenAI(api_key=api_key)
    
    # Construct the system prompt
    system_prompt = """
    You are an expert Python code debugger specializing in data science and pandas operations.
    
    You will be provided with:
    1. Faulty Python code that caused an error
    2. The error traceback message
    
    Your task is to analyze the error and provide a corrected version of the code.
    
    IMPORTANT REQUIREMENTS:
    1. Your response MUST contain ONLY the corrected Python code - no explanations, no markdown, no conversation
    2. The function name and signature must remain the same (transform_data function that accepts a DataFrame)
    3. Fix ALL issues in the code, not just the one causing the immediate error
    4. The corrected code should be robust and handle edge cases
    5. Do not add any print statements or visualizations
    
    Example format of your response:
    ```python
    def transform_data(df):
        # Your corrected code here
        return df
    ```
    
    But remember, do NOT include the markdown code block syntax in your actual response - ONLY the Python code itself.
    """
    
    # Make the API call
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # Using GPT-4 for better debugging
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Faulty code:\n\n{faulty_code}\n\nError traceback:\n\n{error_traceback}"}
            ],
            temperature=0.2,  # Lower temperature for more deterministic outputs
            max_tokens=1000
        )
        
        # Extract the code from the response
        code_content = response.choices[0].message.content.strip()
        
        # Remove any potential markdown code block syntax
        if code_content.startswith("```python"):
            code_content = code_content.split("```python", 1)[1]
        if code_content.endswith("```"):
            code_content = code_content.rsplit("```", 1)[0]
        
        return code_content.strip()
    
    except Exception as e:
        raise Exception(f"Error fixing code: {str(e)}")