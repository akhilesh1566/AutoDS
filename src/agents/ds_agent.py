import os
import json
import openai
from typing import List, Dict, Any

def generate_plan(data_profile: dict, user_context: str) -> list:
    """
    Generate a strategic data processing plan based on the data profile and user context.
    
    Args:
        data_profile: A dictionary containing the profile of the dataset
        user_context: A string describing the user's problem or goal
        
    Returns:
        A list of dictionaries, each representing a step in the data processing plan
    """
    # Load OpenAI API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
    
    # Construct the system prompt
    system_prompt = """
    You are a world-class senior data scientist with expertise in data preparation, cleaning, and analysis.
    
    You will be provided with a detailed profile of a dataset and a description of the user's problem or goal.
    Your task is to create a logical, step-by-step data preparation plan that will transform the raw data into a format
    suitable for analysis or modeling based on the user's needs.
    
    Each step in your plan should be clear, specific, and include the rationale behind it.
    For example, instead of just saying "Clean missing values", specify which columns have missing values,
    what method to use for imputation (mean, median, mode, etc.), and why that method is appropriate for that column.
    
    Your response MUST be a valid JSON list of dictionaries. Each dictionary represents one task in the plan and must have these keys:
    - "id": An integer representing the step number (starting from 1)
    - "task": A clear, descriptive string explaining the action to be taken and the rationale
    
    Example output format:
    [
        {"id": 1, "task": "Drop the 'customer_id' column as it is just an identifier and not useful for modeling."},
        {"id": 2, "task": "Impute missing values in the 'income' column using the median, as the distribution is likely skewed by high earners."}
    ]
    
    Be comprehensive but focused. Prioritize actions that will have the most impact on the quality of the final dataset.
    """
    
    # Prepare the user message with the data profile and context
    user_message = f"""Data Profile:\n{json.dumps(data_profile, indent=2)}\n\nUser Context:\n{user_context}"""
    
    try:
        # Make the API call to OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Using GPT-4 for better reasoning capabilities
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.2,  # Lower temperature for more focused and deterministic outputs
            max_tokens=2000  # Adjust as needed based on expected plan complexity
        )
        
        # Extract the content from the response
        plan_json_string = response.choices[0].message.content.strip()
        
        # Parse the JSON string into a Python list
        plan = json.loads(plan_json_string)
        
        # Validate the structure of the plan
        for step in plan:
            if "id" not in step or "task" not in step:
                raise ValueError(f"Invalid step format in plan: {step}")
        
        return plan
    
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        # Fallback: Return a basic plan indicating the error
        return [
            {"id": 1, "task": "Error generating plan. Please check the data profile and try again."}
        ]
    
    except Exception as e:
        print(f"Error generating plan: {e}")
        # Fallback: Return a basic plan indicating the error
        return [
            {"id": 1, "task": f"Error generating plan: {str(e)}"}
        ]