# nkrane_gt/utils.py
import json
import pandas as pd
from typing import Dict, List
from .terminology_manager import TerminologyManager

def list_available_options(terminology_source: str = None) -> Dict:
    """
    List available terms from terminology CSV.
    
    Args:
        terminology_source: Path to terminology CSV file
        
    Returns:
        Dictionary with available options
    """
    if not terminology_source:
        return {
            'term_count': 0,
            'message': 'No terminology source provided'
        }
    
    manager = TerminologyManager(target_lang='en', user_csv_path=terminology_source)
    terms = manager.terms
    
    return {
        'term_count': len(terms),
        'terms': list(terms.keys())
    }

def export_terminology(terminology_source: str, 
                      output_format: str = 'json') -> str:
    """
    Export terminology to various formats.
    
    Args:
        terminology_source: Path to terminology CSV file
        output_format: 'json', 'csv', or 'dict'
        
    Returns:
        Terminology in requested format
    """
    manager = TerminologyManager(target_lang='en', user_csv_path=terminology_source)
    terms = manager.terms
    
    # Convert to list of dictionaries
    terms_list = [
        {
            'term': term,
            'translation': translation
        }
        for term, translation in terms.items()
    ]
    
    if output_format == 'json':
        return json.dumps(terms_list, indent=2, ensure_ascii=False)
    elif output_format == 'csv':
        import io
        import csv
        
        output = io.StringIO()
        if terms_list:
            writer = csv.DictWriter(output, fieldnames=terms_list[0].keys())
            writer.writeheader()
            writer.writerows(terms_list)
        return output.getvalue()
    else:  # 'dict'
        return terms_list

def create_sample_terminology() -> pd.DataFrame:
    """
    Create a sample terminology DataFrame for testing.
    
    Returns:
        Sample terminology as DataFrame
    """
    data = {
        'term': ['house', 'car', 'school', 'water', 'market'],
        'translation': ['efie', 'kaa', 'sukuu', 'nsu', 'dwabea']
    }
    
    return pd.DataFrame(data)

def save_sample_terminology(filepath: str = 'sample_terminology.csv'):
    """
    Save sample terminology to a CSV file.
    
    Args:
        filepath: Path where to save the sample terminology
    """
    df = create_sample_terminology()
    df.to_csv(filepath, index=False)
    print(f"✅ Sample terminology saved to {filepath}")
