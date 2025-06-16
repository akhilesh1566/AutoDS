import pandas as pd
import io

def create_data_profile(df: pd.DataFrame) -> dict:
    """
    Create a comprehensive profile of the input DataFrame.
    
    Args:
        df: A pandas DataFrame to be profiled
        
    Returns:
        A dictionary containing key statistics and information about the DataFrame
    """
    # Capture df.info() output as a string
    buffer = io.StringIO()
    df.info(buf=buffer)
    info_string = buffer.getvalue()
    
    # Calculate missing values
    missing_values = {}
    for column in df.columns:
        missing_count = df[column].isna().sum()
        missing_percentage = (missing_count / len(df)) * 100
        missing_values[column] = {
            "count": int(missing_count),
            "percentage": round(missing_percentage, 2)
        }
    
    # Create the profile dictionary
    profile = {
        "shape": df.shape,
        "sample_head": df.head(5).to_dict(orient='records'),
        "data_types": info_string,
        "missing_values": missing_values,
        "numeric_description": df.describe(include='number').to_dict(),
        "categorical_description": df.describe(include='object').to_dict(),
        "unique_values": {column: df[column].nunique() for column in df.columns}
    }
    
    return profile