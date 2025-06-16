import os
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def generate_code(task_description: str) -> str:
    """
    Generate Python code based on a task description using OpenAI's API.
    
    Args:
        task_description (str): Description of the data transformation task to perform
        
    Returns:
        str: Generated Python code for the transform_data function
    """
    # Load API key from environment variables
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found in environment variables")
    
    # Set up the OpenAI client
    client = openai.OpenAI(api_key=api_key)
    
    # Construct the system prompt
    system_prompt = """
    You are an expert Python developer specializing in data science and pandas DataFrame operations.
    
    Your task is to write a Python function named 'transform_data' that performs the requested data transformation.
    
    IMPORTANT REQUIREMENTS:
    1. The function MUST be named 'transform_data'
    2. It MUST accept ONE argument: a pandas DataFrame named 'df'
    3. It MUST return the modified DataFrame
    4. Your response MUST contain ONLY the Python code - no explanations, no markdown, no conversation
    5. The code should be efficient, clean, and follow best practices
    6. Handle potential errors gracefully (e.g., missing columns)
    7. Do not include any print statements or visualizations
    
    Example format of your response:
    ```python
    def transform_data(df):
        # Your code here
        return df
    ```
    
    But remember, do NOT include the markdown code block syntax in your actual response - ONLY the Python code itself.
    """
    
    # Make the API call
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # Using GPT-4 for better code generation
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task_description}
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
        raise Exception(f"Error generating code: {str(e)}")