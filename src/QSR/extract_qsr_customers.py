import time
import trino
import pandas as pd
import warnings
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
import pickle
import os
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


def run_queries(queries):
    time.sleep(0.0001)
    results = []
    with trino.dbapi.connect(**conn_details) as conn:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=UserWarning)
            for query in tqdm(queries, desc="Running queries"):
                with contextlib.redirect_stdout(io.StringIO()):  # remove this line to print the link to login page for setting up the connection
                    result = pd.read_sql_query(query, conn)
                results.append(result)
    return results


def extract_customers_acquired_through_qsr(period_start_date, period_end_date, store_names):
    # Convert the list of store names to a string that can be used in the SQL IN clause
    store_names_str = ', '.join(f"'{store}'" for store in store_names)
    print(f"QSR List: {store_names_str}")

    qsr_query = f"""
    SELECT DISTINCT customer_id
    FROM delta.central_order_descriptors_odp.order_descriptors_v2
    WHERE order_country_code = 'PL'
      AND order_final_status = 'DeliveredStatus'
      AND order_parent_relationship_type IS NULL
      AND order_is_first_delivered_order = true
      AND store_name IN ({store_names_str})
      AND order_started_local_at < DATE_ADD('day', 1, DATE '{period_end_date}') 
      AND order_started_local_at >= DATE '{period_start_date}'
    """
    not_qsr_query = f"""
    SELECT DISTINCT customer_id
    FROM delta.central_order_descriptors_odp.order_descriptors_v2
    WHERE order_country_code = 'PL'
      AND order_final_status = 'DeliveredStatus'
      AND order_parent_relationship_type IS NULL
      AND order_is_first_delivered_order = true
      AND store_name NOT IN ({store_names_str})
      AND order_started_local_at < DATE_ADD('day', 1, DATE '{period_end_date}') 
      AND order_started_local_at >= DATE '{period_start_date}'
    """

    queries = [qsr_query, not_qsr_query]
    results = run_queries(queries)
    return results


def get_qsr_data(period_start_date, period_end_date, store_names, update=True):
    if update or not (os.path.exists('data/customers/qsr_customers.pkl') and os.path.exists('data/customers/not_qsr_customers.pkl')):
        print("Updating customers data...")
        qsr, not_qsr = extract_customers_acquired_through_qsr(period_start_date, period_end_date, store_names)

        if not os.path.exists('data/customers'):
            os.makedirs('data/customers')

        qsr.to_pickle('data/customers/qsr_customers.pkl')
        not_qsr.to_pickle('data/customers/not_qsr_customers.pkl')
    else:
        print("Loading customers data...")
        qsr = pd.read_pickle('data/customers/qsr_customers.pkl')
        not_qsr = pd.read_pickle('data/customers/not_qsr_customers.pkl')

    return qsr, not_qsr

