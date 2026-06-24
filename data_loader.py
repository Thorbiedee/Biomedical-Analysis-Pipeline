# File: data_loader.py

import pandas as pd

class ExperimentDataLoader:
    def __init__(self, filepath: str, sample_col='Animal ID', group_col='Group'):
        self.filepath = filepath
        self.data = None
        
        # Strip any accidental spaces from the inputs
        self.sample_col = sample_col.strip()
        self.group_col = group_col.strip()

    def load(self):
        # Load the raw data
        df = pd.read_csv(self.filepath)
        
        # CLEANUP: Strip accidental whitespace from the beginning/end of all column headers
        df.columns = df.columns.str.strip()
        
        # Rename the columns dynamically
        self.data = df.rename(columns={self.sample_col: 'Sample', self.group_col: 'Group'})
        
        # Update internal variables
        self.sample_col = 'Sample'
        self.group_col = 'Group'
        
        return self.data

    def get_numeric_parameters(self):
        numeric_cols = []
        
        for col in self.data.columns[2:]:
            # CLEANUP: Extract only the numerical part of the cell using regex.
            # This turns "120 mg/dl" into "120.0" safely without crashing.
            if self.data[col].dtype == object: # If Pandas thinks it's text
                extracted_numbers = self.data[col].astype(str).str.extract(r'([-+]?\d*\.?\d+)')[0]
                self.data[col] = pd.to_numeric(extracted_numbers, errors='coerce')
            else:
                self.data[col] = pd.to_numeric(self.data[col], errors='coerce')
            
            # If the column has at least one valid number, keep it
            if self.data[col].notna().any():
                numeric_cols.append(col)
                
        return numeric_cols