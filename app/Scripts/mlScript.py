import os
import requests
import pandas as pd
from .tabulate import create_html_table_with_borders

def write_to_csv(file_path, data_frame, delimiter=','):
    """Helper function to delete the file if it exists and then write data to it."""
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Cleared existing data in '{file_path}'")
    data_frame.to_csv(file_path, index=False, sep=delimiter)
    print(f"Data written to '{file_path}' in tabulated format")

try:
    # Configure base URL and error handling
    BASE_URL = 'http://127.0.0.1:8001'

    # Fetch the groups data
    print("Fetching groups data...")
    groups_api = requests.get(f'{BASE_URL}/groups/all')
    groups_api.raise_for_status()
    groups_api_data = groups_api.json()
    print(f"Successfully fetched {len(groups_api_data)} groups")

    # Fetch the reservations data
    print("Fetching reservations data...")
    reservations_api = requests.get(f'{BASE_URL}/reservations')
    reservations_api.raise_for_status()
    reservations_api_data = reservations_api.json()
    print(f"Successfully fetched {len(reservations_api_data)} reservations")

    # Convert the groups data into a pandas DataFrame
    groups_df = pd.DataFrame(groups_api_data)
    write_to_csv('groups_data.csv', groups_df)

    # Convert the reservations data into a pandas DataFrame
    reservations_df = pd.DataFrame(reservations_api_data)
    write_to_csv('reservations_data.csv', reservations_df)

    # Perform different types of merges between groups and reservations
    print("Performing data merges...")

    # Inner join - only matching records between both DataFrames
    inner_join_df = pd.merge(reservations_df, groups_df,
                             left_on='assigned_group_id', right_on='id',
                             how='inner')
    write_to_csv('inner_join.csv', inner_join_df)

    # Outer join - all records from both DataFrames
    outer_join_df = pd.merge(reservations_df, groups_df,
                             left_on='assigned_group_id', right_on='id',
                             how='outer')
    write_to_csv('outer_join.csv', outer_join_df)

    # Right join - all records from groups DataFrame
    right_join_df = pd.merge(reservations_df, groups_df,
                             left_on='assigned_group_id', right_on='id',
                             how='right')
    write_to_csv('right_join.csv', right_join_df)

    # Left join - all records from reservations DataFrame
    left_join_df = pd.merge(reservations_df, groups_df,
                            left_on='assigned_group_id', right_on='id',
                            how='left')
    write_to_csv('left_join.csv', left_join_df)

    # Cross join - cartesian product of both DataFrames
    # Uncomment the following lines to perform and save cross join
    # cross_join_df = pd.merge(reservations_df.assign(key=1), groups_df.assign(key=1), on='key').drop('key', axis=1)
    # write_to_csv('cross_join.csv', cross_join_df)

    # Analyze null values in the merged DataFrames
    null_values_df = pd.DataFrame({
        'Inner Join Nulls': inner_join_df.isnull().sum(),
        'Outer Join Nulls': outer_join_df.isnull().sum(),
        'Right Join Nulls': right_join_df.isnull().sum(),
        'Left Join Nulls': left_join_df.isnull().sum()
    }).reset_index()
    null_values_df.columns = ['Column', 'Inner Join Nulls', 'Outer Join Nulls', 'Right Join Nulls', 'Left Join Nulls']
    write_to_csv('null_values_analysis.csv', null_values_df)

    # Basic statistics for numeric columns
    if 'rating' in groups_df.columns:
        groups_rating_stats = groups_df['rating'].describe().reset_index()
        groups_rating_stats.columns = ['Statistic', 'Groups Rating']
        write_to_csv('groups_rating_stats.csv', groups_rating_stats)

    if 'price' in reservations_df.columns:
        reservations_price_stats = reservations_df['price'].describe().reset_index()
        reservations_price_stats.columns = ['Statistic', 'Reservations Price']
        write_to_csv('reservations_price_stats.csv', reservations_price_stats)

    # Group by analysis
    if 'cleaning_type' in reservations_df.columns and 'price' in reservations_df.columns:
        cleaning_type_avg_price = reservations_df.groupby('cleaning_type')['price'].mean().reset_index()
        cleaning_type_avg_price.columns = ['Cleaning Type', 'Average Price']
        write_to_csv('cleaning_type_avg_price.csv', cleaning_type_avg_price)

    if 'priority' in reservations_df.columns:
        priority_count = reservations_df.groupby('priority').size().reset_index(name='Count')
        priority_count.columns = ['Priority', 'Reservation Count']
        write_to_csv('priority_count.csv', priority_count)

    # Call the function to create HTML tables with borders for each CSV file
    create_html_table_with_borders('groups_data.csv')
    create_html_table_with_borders('reservations_data.csv')
    create_html_table_with_borders('inner_join.csv')
    create_html_table_with_borders('outer_join.csv')
    create_html_table_with_borders('right_join.csv')
    create_html_table_with_borders('left_join.csv')
    create_html_table_with_borders('null_values_analysis.csv')
    create_html_table_with_borders('groups_rating_stats.csv')
    create_html_table_with_borders('reservations_price_stats.csv')
    create_html_table_with_borders('cleaning_type_avg_price.csv')
    create_html_table_with_borders('priority_count.csv')

except requests.exceptions.RequestException as e:
    print(f"Error fetching data from API: {e}")
    print("Please make sure the server is running on port 8001")
except KeyError as e:
    print(f"Error accessing DataFrame column: {e}")
    print("Available columns in groups_df:", groups_df.columns if 'groups_df' in locals() else "Not available")
    print("Available columns in reservations_df:", reservations_df.columns if 'reservations_df' in locals() else "Not available")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
