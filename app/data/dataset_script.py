import requests
import pandas as pd
try:
    # Configure base URL and error handling
    BASE_URL = 'http://127.0.0.1:8001'  # Updated port to match main.py
    
    # Fetch the groups data
    print("Fetching groups data...")
    groups_api = requests.get(f'{BASE_URL}/groups/all')
    groups_api.raise_for_status()
    groups_api_data = groups_api.json()
    print(f"Successfully fetched {len(groups_api_data)} groups")
    
    # Fetch the reservations data
    print("Fetching reservations data...")
    reservations_api = requests.get(f'{BASE_URL}/reservations/all')
    reservations_api.raise_for_status()
    reservations_api_data = reservations_api.json()
    print(f"Successfully fetched {len(reservations_api_data)} reservations")
    
    # Convert the groups data into a pandas DataFrame
    groups_df = pd.DataFrame(groups_api_data)
    print("\nGroups DataFrame:\n{}".format(groups_df))
    
    # Convert the reservations data into a pandas DataFrame
    reservations_df = pd.DataFrame(reservations_api_data)
    print("\nReservations DataFrame:\n{}".format(reservations_df))
    
    # Perform different types of merges between groups and reservations
    print("\nPerforming data merges...")
    
    # Inner join - only matching records between both DataFrames
    merged_df = pd.merge(groups_df, reservations_df, 
                        left_on='id', right_on='assigned_group_id', 
                        how='inner')
    print("\nInner Join Result (first 5 rows):\n", merged_df.head())
    
    # Outer join - all records from both DataFrames
    merged_df2 = pd.merge(groups_df, reservations_df, 
                         left_on='id', right_on='assigned_group_id', 
                         how='outer')
    print("\nOuter Join Result (first 5 rows):\n", merged_df2.head())
    
    # Cross join - cartesian product of both DataFrames
    merged_df3 = pd.merge(groups_df, reservations_df, 
                         left_on='id', right_on='assigned_group_id', 
                         how='cross')
    print("\nCross Join Result (first 5 rows):\n", merged_df3.head())
    
    # Right join - all records from reservations DataFrame
    merged_df4 = pd.merge(groups_df, reservations_df, 
                         left_on='id', right_on='assigned_group_id', 
                         how='right')
    print("\nRight Join Result (first 5 rows):\n", merged_df4.head())
    
    # Left join - all records from groups DataFrame
    merged_df5 = pd.merge(groups_df, reservations_df, 
                         left_on='id', right_on='assigned_group_id', 
                         how='left')
    print("\nLeft Join Result (first 5 rows):\n", merged_df5.head())
    
    # Print shapes to understand the size of each merged DataFrame
    print("\nDataFrame Shapes:")
    print("Original Groups shape:", groups_df.shape)
    print("Original Reservations shape:", reservations_df.shape)
    print("Inner join shape:", merged_df.shape)
    print("Outer join shape:", merged_df2.shape)
    print("Cross join shape:", merged_df3.shape)
    print("Right join shape:", merged_df4.shape)
    print("Left join shape:", merged_df5.shape)
    
    # Analyze null values in the merged DataFrames
    print("\nNull Values Analysis:")
    print("Null values in inner join:\n", merged_df.isnull().sum())
    print("\nNull values in outer join:\n", merged_df2.isnull().sum())
    
    # Basic statistics for numeric columns
    print("\nBasic Statistics:")
    if 'rating' in groups_df.columns:
        print("Groups rating statistics:\n", groups_df['rating'].describe())
    if 'price' in reservations_df.columns:
        print("\nReservations price statistics:\n", reservations_df['price'].describe())
    
    # Group by analysis
    print("\nGroup By Analysis:")
    if 'cleaning_type' in reservations_df.columns and 'price' in reservations_df.columns:
        print("Average price by cleaning type:\n", 
              reservations_df.groupby('cleaning_type')['price'].mean())
    if 'priority' in reservations_df.columns:
        print("\nReservation count by priority:\n", 
              reservations_df.groupby('priority').size())
    
except requests.exceptions.RequestException as e:
    print(f"Error fetching data from API: {e}")
    print("Please make sure the server is running on port 8001")
except KeyError as e:
    print(f"Error accessing DataFrame column: {e}")
    print("Available columns in groups_df:", groups_df.columns if 'groups_df' in locals() else "Not available")
    print("Available columns in reservations_df:", reservations_df.columns if 'reservations_df' in locals() else "Not available")
except Exception as e:
    print(f"An unexpected error occurred: {e}")