import pandas as pd
from pathlib import Path
from datetime import datetime
import os

class StateManager:
    """
    Central hub for handling all data I/O and managing the state of the data-processing pipeline.
    Manages run-specific directories and files for each execution of the AutoDS system.
    """
    
    def __init__(self):
        """
        Initialize the StateManager with a unique run ID and create necessary directories.
        """
        # Generate a unique run_id based on current date and time
        self.run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Define the base output directory path
        base_output_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / 'outputs'
        
        # Create the run-specific directory
        self.run_dir = base_output_dir / self.run_id
        self.run_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for data, plots, and reports
        self.data_dir = self.run_dir / 'data'
        self.plots_dir = self.run_dir / 'plots'
        self.reports_dir = self.run_dir / 'reports'
        
        self.data_dir.mkdir(exist_ok=True)
        self.plots_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Initialize DataFrame to None
        self.df = None
        
        print(f"StateManager initialized with run ID: {self.run_id}")
        print(f"Output directory: {self.run_dir}")
    
    def load_csv(self, file_path: str):
        """
        Load a CSV file into a pandas DataFrame and store it in the instance.
        
        Args:
            file_path (str): Path to the CSV file to load
        """
        try:
            self.df = pd.read_csv(file_path)
            print(f"Loaded CSV from {file_path} with {len(self.df)} rows and {len(self.df.columns)} columns")
            return True
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return False
    
    def get_dataframe(self):
        """
        Return the current DataFrame stored in the instance.
        
        Returns:
            pandas.DataFrame: The current DataFrame
        """
        return self.df
    
    def update_dataframe(self, new_df):
        """
        Update the instance's DataFrame with a new one.
        
        Args:
            new_df (pandas.DataFrame): The new DataFrame to store
        """
        self.df = new_df
        print(f"DataFrame updated with {len(self.df)} rows and {len(self.df.columns)} columns")
    
    def save_dataframe(self, filename: str):
        """
        Save the current DataFrame to a CSV file in the run-specific data directory.
        
        Args:
            filename (str): Name of the file to save (e.g., "final_data.csv")
        """
        if self.df is None:
            print("No DataFrame to save")
            return False
        
        file_path = self.data_dir / filename
        try:
            self.df.to_csv(file_path, index=False)
            print(f"DataFrame saved to {file_path}")
            return True
        except Exception as e:
            print(f"Error saving DataFrame: {e}")
            return False
    
    def save_plot(self, figure, filename: str):
        """
        Save a matplotlib figure to the run-specific plots directory.
        
        Args:
            figure: A matplotlib figure object
            filename (str): Name of the file to save (e.g., "distribution.png")
        """
        file_path = self.plots_dir / filename
        try:
            figure.savefig(file_path, bbox_inches='tight')
            print(f"Plot saved to {file_path}")
            return True
        except Exception as e:
            print(f"Error saving plot: {e}")
            return False
    
    def save_report(self, content: str, filename: str):
        """
        Save a report to the run-specific reports directory.
        
        Args:
            content (str): Content of the report
            filename (str): Name of the file to save (e.g., "final_report.md")
        """
        file_path = self.reports_dir / filename
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Report saved to {file_path}")
            return True
        except Exception as e:
            print(f"Error saving report: {e}")
            return False