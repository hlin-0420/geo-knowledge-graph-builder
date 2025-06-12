# load_filetypes.py

import pandas as pd
from bs4 import BeautifulSoup

def extract_geo_file_types(htm_file_path):
    """
    Extracts the file type information from a GEO HTM file.

    Args:
        htm_file_path (str): Path to the HTM file.

    Returns:
        pandas.DataFrame: DataFrame containing the extracted table data.
    """
    # Read the HTM file
    with open(htm_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the main table (it has class "Table_Style_1")
    table = soup.find('table', {'class': 'Table_Style_1'})
    if table is None:
        raise ValueError("No table with class 'Table_Style_1' found in the HTML.")

    # Extract table headers
    headers = []
    header_row = table.find('tr')
    for th in header_row.find_all('td'):
        headers.append(th.get_text(strip=True))
    
    # Extract table rows
    data = []
    for row in table.find_all('tr')[1:]:  # Skip header row
        row_data = []
        for td in row.find_all('td'):
            text = td.get_text(' ', strip=True)  # Clean up text
            row_data.append(text)
        data.append(row_data)
    
    # Create and return DataFrame
    df = pd.DataFrame(data, columns=headers)
    return df