import pandas as pd

def create_html_table_with_borders(file_path):
    """Reads CSV data and outputs it as an HTML table with borders."""
    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)

        # Remove duplicates if any
        df = df.drop_duplicates()

        # Create HTML table with borders
        html_table = df.to_html(border=1, index=False)

        # Save the HTML output to a file
        html_file_path = file_path.replace('.csv', '_table_with_borders.html')
        with open(html_file_path, 'w') as f:
            f.write(html_table)

        print(f"HTML table with borders has been written to '{html_file_path}'.")

    except Exception as e:
        print(f"An error occurred while creating the HTML table: {e}")

# Example function call (Replace with your actual CSV file path)
create_html_table_with_borders('priority_count.csv')
