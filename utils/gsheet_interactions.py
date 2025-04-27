from google.oauth2.service_account import Credentials
from datetime import datetime
import gspread
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")  # Get from your .env file
CREDENTIALS_FILE = "google_sheets_credentials.json"  # Path to your credentials file

def setup_google_sheets():
    """Setup and authenticate with Google Sheets API"""
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    
    try:
        credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
        print(f"fetched credentials")
        gc = gspread.authorize(credentials)
        return gc
    except Exception as e:
        print(f"Error setting up Google Sheets: {e}")
        raise

def load_config_from_google_sheets(gc):
    """
    Load configuration from Google Sheets.
    Expected sheets:
    - Sheet named 'Brands' with columns 'Name' and 'Type' (where Type is 'target' or 'competitor')
    - Sheet named 'Queries' with a column 'Query'
    
    Returns a tuple of (target_brand, competitor_brand, queries)
    """
    print(f"Loading configuration from Google Sheet ID: {SPREADSHEET_ID}")
    
    try:
        # Open the spreadsheet
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        
        # Read brands sheet
        try:
            brands_worksheet = spreadsheet.worksheet("Brands")
            brands_data = brands_worksheet.get_all_records()
            brands_df = pd.DataFrame(brands_data)
            
            target_brands = brands_df[brands_df['Type'].str.lower() == 'target']['Name'].tolist()
            competitor_brands = brands_df[brands_df['Type'].str.lower() == 'competitor']['Name'].tolist()
            
            # Ensure we have at least one target and one competitor
            target_brand = target_brands[0] if target_brands else "Avanza"
            competitor_brand = competitor_brands[0] if competitor_brands else "Nordnet"
        except Exception as e:
            print(f"Error reading Brands sheet: {e}")
            print("Using default brands instead.")
            target_brand = "Avanza"
            competitor_brand = "Nordnet"
            
        # Read queries sheet
        try:
            queries_worksheet = spreadsheet.worksheet("Queries")
            queries_data = queries_worksheet.get_all_records()
            queries_df = pd.DataFrame(queries_data)
            queries = queries_df['Query'].tolist() if 'Query' in queries_df.columns else []
        except Exception as e:
            print(f"Error reading Queries sheet: {e}")
            print("Using default query instead.")
            queries = ["What to use for investing in stocks in Sweden?"]
            
        # Validate that we have at least one query
        if not queries:
            print("No queries found in spreadsheet. Using a default query.")
            queries = ["What to use for investing in stocks in Sweden?"]
        
        print(f"Loaded target brand: {target_brand}")
        print(f"Loaded competitor brand: {competitor_brand}")
        print(f"Loaded {len(queries)} queries")
        
        return target_brand, competitor_brand, queries, spreadsheet
        
    except Exception as e:
        print(f"Error accessing Google Sheet: {e}")
        print("Using default values instead.")
        return "Avanza", "Nordnet", ["What to use for investing in stocks in Sweden?"], None

def create_or_update_results_sheet(spreadsheet, results, target_brand, competitor_brand, repeat_count):
    """Save results to a new sheet in the Google Spreadsheet with raw values"""
    # Create a timestamp for the sheet name
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    sheet_name = f"Results {timestamp}"
    
    try:
        # Create a new sheet for results
        results_sheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
        
        # Prepare headers
        headers = [
            "Query", 
            f"{target_brand} - Gemini Mentions", 
            f"{target_brand} - Perplexity Mentions",
            f"{competitor_brand} - Gemini Mentions", 
            f"{competitor_brand} - Perplexity Mentions"
        ]
        
        # Write headers
        results_sheet.update('A1:E1', [headers])
        
        # Group results by query
        query_results = {}
        for result in results:
            query = result['query']
            model = result['model']
            
            if query not in query_results:
                query_results[query] = {'gemini': None, 'perplexity': None}
                
            query_results[query][model] = result
        
        # Prepare data rows with raw values
        data_rows = []
        for query, models in query_results.items():
            gemini_data = models.get('gemini', {})
            perplexity_data = models.get('perplexity', {})
            
            # Extract raw data for each model (with fallbacks if data is missing)
            gemini_mentions = sum(gemini_data.get('attempts', [])) if gemini_data else 0
            gemini_competitor_mentions = sum(gemini_data.get('competitor_attempts', [])) if gemini_data else 0
            
            perplexity_mentions = sum(perplexity_data.get('attempts', [])) if perplexity_data else 0
            perplexity_competitor_mentions = sum(perplexity_data.get('competitor_attempts', [])) if perplexity_data else 0
            
            data_rows.append([
                query, 
                gemini_mentions,
                perplexity_mentions,
                gemini_competitor_mentions,
                perplexity_competitor_mentions
            ])
        
        # Write data rows
        if data_rows:
            results_sheet.update(f'A2:E{len(data_rows)+1}', data_rows)
        
        # Add summary at the bottom with raw values
        summary_row = len(data_rows) + 3  # Leave a blank row
        results_sheet.update(f'A{summary_row}:A{summary_row+1}', [["SUMMARY"], ["Total Mentions"]])
        
        # Calculate overall statistics
        total_responses = len(query_results) * repeat_count * 2  # *2 because we test two models
        
        # Calculate total mentions across all queries and models
        total_target_mentions = 0
        total_competitor_mentions = 0
        
        for query, models in query_results.items():
            gemini_data = models.get('gemini', {})
            perplexity_data = models.get('perplexity', {})
            
            # Add up target mentions
            if gemini_data and 'attempts' in gemini_data:
                total_target_mentions += sum(gemini_data['attempts'])
            if perplexity_data and 'attempts' in perplexity_data:
                total_target_mentions += sum(perplexity_data['attempts'])
                
            # Add up competitor mentions
            if gemini_data and 'competitor_attempts' in gemini_data:
                total_competitor_mentions += sum(gemini_data['competitor_attempts'])
            if perplexity_data and 'competitor_attempts' in perplexity_data:
                total_competitor_mentions += sum(perplexity_data['competitor_attempts'])
        
        # Write summary data with raw values
        results_sheet.update(f'B{summary_row+1}:E{summary_row+1}', [[
            total_target_mentions,
            total_competitor_mentions,
            total_responses,
            timestamp
        ]])
        
        # Add a row with labels for the summary data
        results_sheet.update(f'B{summary_row}:E{summary_row}', [[
            f"{target_brand} Mentions",
            f"{competitor_brand} Mentions",
            "Total Responses",
            "Timestamp"
        ]])
        
        # Format the sheet
        results_sheet.format('A1:E1', {'textFormat': {'bold': True}})
        results_sheet.format(f'A{summary_row}:E{summary_row}', {'textFormat': {'bold': True}})
        
        print(f"Results saved to Google Sheet tab: '{sheet_name}'")
        return True
    
    except Exception as e:
        print(f"Error saving results to Google Sheet: {e}")
        return False