import pandas as pd
import pickle

with open('data/orders.pkl', 'rb') as file:
    loaded_orders = pickle.load(file)

with open('data/recurrent_customers.pkl', 'rb') as file:
    loaded_recurrent_customers = pickle.load(file)

print(loaded_orders)
print(loaded_recurrent_customers)





#
# def count_customer_occurrences(date_key, customer_df, data_dict):
#     """
#     Counts the occurrences of customer IDs in the given DataFrame that are present in the DataFrame stored in the dictionary for the given date key.
#
#     Parameters:
#     date_key (str): The key representing the date in the dictionary.
#     customer_df (pd.DataFrame): DataFrame containing customer IDs to check.
#     data_dict (dict): Dictionary with date keys and DataFrames containing 'status' and 'customer_id' fields.
#
#     Returns:
#     int: The count of occurrences of customer IDs in the DataFrame stored in the dictionary for the given date key.
#     """
#     if date_key not in data_dict:
#         raise ValueError(f"Date key {date_key} not found in the dictionary.")
#
#     # Extract the DataFrame for the given date key
#     df_in_dict = data_dict[date_key]
#
#     # Ensure the DataFrame has the required 'customer_id' column
#     if 'customer_id' not in df_in_dict.columns:
#         raise ValueError(f"The DataFrame for date key {date_key} does not contain 'customer_id' column.")
#
#     # Count occurrences of customer IDs in the DataFrame stored in the dictionary
#     count = customer_df['customer_id'].isin(df_in_dict['customer_id']).sum()
#
#     return count
#
#
# # Example usage

# data_dict = {
#     '2024-08-07': pd.DataFrame({
#         'status': ['active', 'inactive', 'active'],
#         'customer_id': [1, 2, 3]
#     })
# }
#
# customer_df = pd.DataFrame({
#     'customer_id': [1, 1, 2, 4]
# })
#
# date_key = '2024-08-07'
# count = count_customer_occurrences(date_key, customer_df, data_dict)
# print(f"Count of customer occurrences: {count}")
#
# import pandas as pd
# import pickle
# from datetime import datetime
#
# # Example dictionary with date keys and DataFrame values
# data_dict = {
#     datetime(2023, 8, 1): pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]}),
#     datetime(2023, 8, 2): pd.DataFrame({'A': [7, 8, 9], 'B': [10, 11, 12]})
# }
#
# # Save the dictionary to a file
# with open('data_dict.pkl', 'wb') as file:
#     pickle.dump(data_dict, file)
#
# # Load the dictionary from the file
# with open('data_dict.pkl', 'rb') as file:
#     loaded_data_dict = pickle.load(file)
#
# # Verify the loaded data
# print(loaded_data_dict)