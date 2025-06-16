import pandas as pd
from src.core.orchestrator import Orchestrator

if __name__ == "__main__":
    # Instantiate the Orchestrator
    orchestrator = Orchestrator()
    
    # Define the user context (problem description)
    user_context = """
    The dataset is from a lending company. My primary goal is to prepare this data for a machine learning model that will predict loan status (either 'Fully Paid' or 'Charged Off').
    I need to clean the data, handle missing values, and remove any columns that are irrelevant or contain sensitive information like addresses.
    Please also perform some basic feature engineering, especially on columns like 'term' which is currently a string.
    """
    
    # Run the full intelligent pipeline
    orchestrator.run_full_pipeline('inputs/loan_data.csv', user_context)
    
    # Verify Final State
    final_df = orchestrator.state_manager.get_dataframe()
    
    # Print Final Output
    print("\nAutoDS Intelligent Pipeline Complete! Final DataFrame:")
    print("\nDataFrame Head:")
    print(final_df.head())
    print("\nDataFrame Info:")
    print(final_df.info())