from datetime import datetime
import time
import trino
import pandas as pd
import warnings
from datetime import datetime, timedelta
from tqdm import tqdm
import contextlib
import io
from extract_qsr_customers import run_queries
from extract_qsr_customers import get_qsr_data

def generate_completed_months(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

    completed_months = []

    # move to the first day of the next month from the start date
    if start_date.day != 1:
        if start_date.month == 12:
            current_date = datetime(start_date.year + 1, 1, 1)
        else:
            current_date = datetime(start_date.year, start_date.month + 1, 1)
    else:
        current_date = start_date

    # loop through the months until the end date
    while current_date <= end_date:
        completed_months.append(current_date.strftime('%Y-%m-%d'))

        if current_date.month == 12:
            current_date = datetime(current_date.year + 1, 1, 1)
        else:
            current_date = datetime(current_date.year, current_date.month + 1, 1)

    return completed_months

month = '2024-06-01'
qsr_customers, not_qsr_customers = get_qsr_data('2024-01-01', '2024-02-01', ["McDonald''s"], update=False)

def ordered_during_month(customers_df, month):
    customer_ids = customers_df['customer_id'].astype(int).tolist()
    customer_ids_str = ', '.join(str(customer_id) for customer_id in customer_ids)

    sql_query = f"""
    SELECT
        distinct customer_id
    FROM delta.central_order_descriptors_odp.order_descriptors_v2 o
    WHERE order_final_status = 'DeliveredStatus'
      AND order_parent_relationship_type IS NULL
      AND customer_id IN ({customer_ids_str})
      AND date (date_trunc('month', order_started_local_at)) = date '{month}'

    """
    df = run_queries([sql_query])
    return df[0]

# # Example usage
# start_date = '2024-07-26'
# end_date = '2024-12-26'
# print(generate_completed_months(start_date, end_date))

def cohort_of_given_month(df_customers_from_previous_period, month):
    retained_customers = ordered_during_month(df_customers_from_previous_period, month)
    print("Number of customers from previous period", len(df_customers_from_previous_period))
    print("Number of retained customers", retained_customers.size)
    percentage = round(retained_customers.shape[0]/ len(df_customers_from_previous_period), 3)
    print("Percentage of retained customers: ", percentage)


cohort_of_given_month(qsr_customers, month)