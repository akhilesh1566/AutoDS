from .state_manager import StateManager
from .code_executor import CodeExecutor
from . import profiler
from ..agents import coder_agent
from ..agents import debugger_agent
from ..agents import ds_agent
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

class Orchestrator:
    """
    The Orchestrator class manages the entire workflow of the AutoDS system.
    
    It coordinates the StateManager, CodeExecutor, CoderAgent, and DebuggerAgent
    to create a self-correcting execution loop that can generate, execute, and debug
    data transformation code automatically.
    """
    
    def __init__(self):
        """
        Initialize the Orchestrator with instances of StateManager and CodeExecutor.
        """
        self.state_manager = StateManager()
        self.code_executor = CodeExecutor()
        self.execution_log = []
        self.console = Console()
        
        self.console.print(Panel.fit(
            "[bold blue]AutoDS Orchestrator Initialized[/bold blue]\n"
            "Ready to execute data science workflows",
            title="AutoDS",
            border_style="blue"
        ))
    
    def run_plan(self, plan: list):
        """
        Execute a plan consisting of multiple data transformation tasks.
        
        The method implements a self-correction mechanism that attempts to debug and
        fix code that fails during execution.
        
        Args:
            plan (list): A list of task dictionaries, each containing 'id' and 'task' keys
                         Example: [{'id': 1, 'task': 'Drop the "address" column'}]
        
        Returns:
            list: The execution log containing details of each task's execution
        """
        self.console.print("[bold]Starting execution plan with", len(plan), "tasks[/bold]")
        
        # Iterate through each task in the plan
        for task_item in plan:
            task_id = task_item['id']
            task_description = task_item['task']
            
            # Log the start of the task
            self.console.print(f"\n[bold green]Executing Task {task_id}: {task_description}[/bold green]")
            
            # Generate code for the task
            self.console.print("[yellow]Generating code...[/yellow]")
            try:
                code_string = coder_agent.generate_code(task_description)
                self.console.print("[green]Code generated successfully[/green]")
                
                # Display the generated code
                self.console.print(Panel(
                    code_string,
                    title="[bold]Generated Code[/bold]",
                    border_style="green",
                    expand=False
                ))
                
            except Exception as e:
                error_msg = f"Error generating code: {str(e)}"
                self.console.print(f"[bold red]{error_msg}[/bold red]")
                self.execution_log.append({
                    'task_id': task_id,
                    'task': task_description,
                    'status': 'failed',
                    'error': error_msg,
                    'stage': 'code_generation'
                })
                continue  # Skip to the next task
            
            # Execution attempt loop (try up to 3 times)
            for attempt in range(3):
                self.console.print(f"[bold]Execution attempt {attempt + 1}/3[/bold]")
                
                # Get the current DataFrame
                current_df = self.state_manager.get_dataframe()
                if current_df is None:
                    self.console.print("[bold red]Error: No DataFrame available for processing[/bold red]")
                    self.execution_log.append({
                        'task_id': task_id,
                        'task': task_description,
                        'status': 'failed',
                        'error': 'No DataFrame available',
                        'stage': 'execution'
                    })
                    break  # Skip to the next task
                
                # Execute the code
                self.console.print("[yellow]Executing code...[/yellow]")
                result = self.code_executor.execute_code(code_string, current_df)
                
                # Check execution result
                if result['status'] == 'success':
                    self.console.print("[bold green]✓ Code executed successfully![/bold green]")
                    
                    # Update the state with the new DataFrame
                    self.state_manager.update_dataframe(result['dataframe'])
                    
                    # Log the successful execution
                    self.execution_log.append({
                        'task_id': task_id,
                        'task': task_description,
                        'code': code_string,
                        'status': 'success',
                        'attempt': attempt + 1
                    })
                    
                    # Break out of the attempt loop
                    break
                    
                else:  # Error occurred
                    error_traceback = result['traceback']
                    self.console.print(f"[bold red]✗ Execution failed (Attempt {attempt + 1}/3)[/bold red]")
                    
                    # Display the error
                    self.console.print(Panel(
                        error_traceback,
                        title="[bold red]Error Traceback[/bold red]",
                        border_style="red",
                        expand=False
                    ))
                    
                    # If we have more attempts left, try debugging
                    if attempt < 2:  # We're on attempt 0 or 1 (out of 0, 1, 2)
                        self.console.print("[yellow]Attempting to debug and fix the code...[/yellow]")
                        
                        try:
                            # Call the debugger agent to fix the code
                            fixed_code = debugger_agent.fix_code(code_string, error_traceback)
                            code_string = fixed_code  # Update the code for the next attempt
                            
                            # Display the fixed code
                            self.console.print(Panel(
                                fixed_code,
                                title="[bold]Fixed Code[/bold]",
                                border_style="yellow",
                                expand=False
                            ))
                            
                        except Exception as e:
                            debug_error = f"Error during debugging: {str(e)}"
                            self.console.print(f"[bold red]{debug_error}[/bold red]")
                    
                    # If this was the last attempt and it failed
                    if attempt == 2:
                        self.console.print("[bold red]All attempts failed. Moving to the next task.[/bold red]")
                        self.execution_log.append({
                            'task_id': task_id,
                            'task': task_description,
                            'code': code_string,
                            'status': 'failed',
                            'error': error_traceback,
                            'attempts': 3
                        })
        
        # Clean up temporary files after all tasks are completed
        self.code_executor.cleanup()
        
        # Print summary
        success_count = sum(1 for log in self.execution_log if log['status'] == 'success')
        total_tasks = len(plan)
        
        self.console.print(f"\n[bold]Execution plan completed: {success_count}/{total_tasks} tasks successful[/bold]")
        
        return self.execution_log
    
    def run_full_pipeline(self, csv_path: str, user_context: str):
        """
        Orchestrate the entire intelligent pipeline from data loading to execution.
        
        This method implements the full autonomous workflow:
        1. Load data from CSV
        2. Profile the data
        3. Generate a dynamic plan using the DSAgent
        4. Execute the plan
        
        Args:
            csv_path (str): Path to the input CSV file
            user_context (str): User's description of their problem and goals
            
        Returns:
            list: The execution log containing details of each task's execution
        """
        self.console.print(Panel.fit(
            "[bold blue]Starting AutoDS Intelligent Pipeline[/bold blue]",
            title="AutoDS",
            border_style="blue"
        ))
        
        # Step 1: Load Data
        self.console.print("[yellow]Loading data from CSV...[/yellow]")
        self.state_manager.load_csv(csv_path)
        df = self.state_manager.get_dataframe()
        if df is None or df.empty:
            self.console.print("[bold red]Error: Failed to load data or dataset is empty[/bold red]")
            return []
        self.console.print(f"[green]Successfully loaded data with shape {df.shape}[/green]")
        
        # Step 2: Profile Data
        self.console.print("[yellow]Profiling dataset...[/yellow]")
        data_profile = profiler.create_data_profile(df)
        self.console.print("[green]Data profiling complete[/green]")
        
        # Step 3: Generate Dynamic Plan
        self.console.print("[yellow]Generating dynamic data processing plan...[/yellow]")
        try:
            plan = ds_agent.generate_plan(data_profile, user_context)
            if not plan or len(plan) == 0:
                self.console.print("[bold red]Error: Generated plan is empty[/bold red]")
                return []
            
            # Display the generated plan
            plan_text = "\n".join([f"Step {task['id']}: {task['task']}" for task in plan])
            self.console.print(Panel(
                plan_text,
                title="[bold]Generated Data Processing Plan[/bold]",
                border_style="green",
                expand=False
            ))
            
        except Exception as e:
            self.console.print(f"[bold red]Error generating plan: {str(e)}[/bold red]")
            return []
        
        # Step 4: Execute the Plan
        self.console.print("[yellow]Executing generated plan...[/yellow]")
        execution_log = self.run_plan(plan)
        
        # Step 5: Final Summary
        success_count = sum(1 for log in execution_log if log['status'] == 'success')
        total_tasks = len(plan)
        
        self.console.print(Panel.fit(
            f"[bold green]AutoDS Pipeline Completed Successfully![/bold green]\n"
            f"Successfully executed {success_count} out of {total_tasks} tasks.",
            title="AutoDS",
            border_style="green"
        ))
        
        return execution_log