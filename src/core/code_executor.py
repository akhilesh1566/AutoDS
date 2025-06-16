import os
import subprocess
import pandas as pd
from pathlib import Path

class CodeExecutor:
    """
    A class for safely executing generated Python code in an isolated environment.
    The code is executed in a separate process to prevent any potential issues
    from affecting the main application.
    """
    
    def __init__(self, temp_dir: str = "temp_execution"):
        """
        Initialize the CodeExecutor with a temporary directory for execution.
        
        Args:
            temp_dir (str): Name of the temporary directory to use for code execution
        """
        # Get the project root directory
        project_root = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        
        # Create the temporary directory path
        self.temp_dir = project_root / temp_dir
        
        # Create the directory if it doesn't exist
        self.temp_dir.mkdir(exist_ok=True)
        
        # Define file paths for temporary files
        self.input_csv_path = self.temp_dir / "input.csv"
        self.output_csv_path = self.temp_dir / "output.csv"
        self.script_path = self.temp_dir / "_temp_script.py"
        
        print(f"CodeExecutor initialized with temporary directory: {self.temp_dir}")
    
    def execute_code(self, code_string: str, input_df: pd.DataFrame) -> dict:
        """
        Execute the provided code with the input DataFrame and return the results.
        
        Args:
            code_string (str): The Python code string containing the transform_data function
            input_df (pd.DataFrame): The input DataFrame to process
            
        Returns:
            dict: A dictionary containing either:
                - {'status': 'success', 'dataframe': resulting_dataframe} if successful
                - {'status': 'error', 'traceback': error_message} if an error occurs
        """
        try:
            # Save the input DataFrame to CSV
            input_df.to_csv(self.input_csv_path, index=False)
            
            # Construct the full script
            full_script = f"""
# Import necessary libraries
import pandas as pd

# Load the input data
df = pd.read_csv(r"{self.input_csv_path}")

# Define the transformation function
{code_string}

# Apply the transformation
try:
    df = transform_data(df)
    # Save the result
    df.to_csv(r"{self.output_csv_path}", index=False)
    print("Transformation completed successfully")
except Exception as e:
    import traceback
    print(f"Error during transformation: {{str(e)}}")
    print(traceback.format_exc())
    exit(1)
"""
            
            # Write the script to a file
            with open(self.script_path, 'w') as f:
                f.write(full_script)
            
            # Execute the script in a subprocess
            result = subprocess.run(
                ["python", str(self.script_path)],
                capture_output=True,
                text=True,
                check=False  # We'll handle errors ourselves
            )
            
            # Check if the execution was successful
            if result.returncode == 0 and self.output_csv_path.exists():
                # Read the output DataFrame
                output_df = pd.read_csv(self.output_csv_path)
                return {
                    'status': 'success',
                    'dataframe': output_df,
                    'stdout': result.stdout
                }
            else:
                # Return the error information
                return {
                    'status': 'error',
                    'traceback': result.stderr or result.stdout,  # Sometimes errors are in stdout
                    'returncode': result.returncode
                }
        
        except Exception as e:
            # Handle any exceptions in the execution process itself
            import traceback
            return {
                'status': 'error',
                'traceback': f"Error in code execution process: {str(e)}\n{traceback.format_exc()}"
            }
    
    def cleanup(self):
        """
        Clean up temporary files created during execution.
        """
        try:
            # Remove temporary files if they exist
            if self.input_csv_path.exists():
                self.input_csv_path.unlink()
            
            if self.output_csv_path.exists():
                self.output_csv_path.unlink()
            
            if self.script_path.exists():
                self.script_path.unlink()
                
            print("Temporary files cleaned up successfully")
            
        except Exception as e:
            print(f"Error cleaning up temporary files: {str(e)}")