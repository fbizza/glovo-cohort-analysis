import time
import trino
import pandas as pd
import warnings
from datetime import datetime
from tqdm import tqdm
import contextlib
import io


# Set up DB connection
HOST = 'starburst.g8s-data-platform-prod.glovoint.com'
PORT = 443
conn_details = {
    'host': HOST,
    'port': PORT,
    'http_scheme': 'https',
    'auth': trino.auth.OAuth2Authentication()
}


def run_queries(queries, verbose=True):
    time.sleep(0.1)
    results = []
    with trino.dbapi.connect(**conn_details) as conn:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=UserWarning)
            if verbose:
                for query in tqdm(queries, desc="Running queries"):
                    with contextlib.redirect_stdout(io.StringIO()):  # remove this line to print the link to login page for setting up the connection
                        result = pd.read_sql_query(query, conn)
                    results.append(result)
            else:
                for query in queries:
                    with contextlib.redirect_stdout(io.StringIO()):  # remove this line to print the link to login page for setting up the connection
                        result = pd.read_sql_query(query, conn)
                    results.append(result)
    return results

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
    df = run_queries([sql_query], verbose=False)
    return df[0]

def retention_of_given_month(df_customers_from_previous_period, initial_number_of_customers, month):
    retained_customers = ordered_during_month(df_customers_from_previous_period, month)
    percentage = round(retained_customers.shape[0] / initial_number_of_customers, 3)
    print(f"\nNumber of retained customers during {month}: {retained_customers.size}")
    print(f"Percentage of initial customers retained: {percentage}")
    return retained_customers, percentage


def retention_since_given_period(start_date, end_date, list_of_customers_df, customer_cohort_names):
    months = generate_completed_months(start_date, end_date)
    print("Generating retention evolution for the following months: ", months)
    retentions = []
    for customer_cohort in list_of_customers_df:
        retention_list = []
        previous_month_customers = customer_cohort
        n_of_customers = customer_cohort.shape[0]
        for month in months:
            retained_customers, percentage = retention_of_given_month(previous_month_customers, n_of_customers, month)
            retention_list.append(percentage)
            previous_month_customers = retained_customers
        retentions.append(retention_list)

    df = pd.DataFrame(retentions, columns=months, index=customer_cohort_names)

    return df


def clip_dataframes_to_smallest(df_list):
    # Determine the length of the smallest dataframe
    min_length = min(df.shape[0] for df in df_list)
    minimum = min(min_length, 90000)
    # Clip each dataframe to the smallest length and preserve the name
    clipped_dfs = []
    for df in df_list:
        clipped_df = df.sample(n=minimum, random_state=29)
        clipped_df.name = df.name
        clipped_dfs.append(clipped_df)

    return clipped_dfs