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
from utils import run_queries


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
      LIMIT 100000
    """
    not_qsr_query = f"""
    SELECT DISTINCT customer_id
    FROM delta.central_order_descriptors_odp.order_descriptors_v2
    WHERE order_country_code = 'PL'
      AND order_final_status = 'DeliveredStatus'
      AND order_parent_relationship_type IS NULL
      AND order_is_first_delivered_order = true
      AND store_name NOT IN ({store_names_str}, 'McDonald''s')
      AND order_started_local_at < DATE_ADD('day', 1, DATE '{period_end_date}') 
      AND order_started_local_at >= DATE '{period_start_date}'
      LIMIT 100000
    """

    mc_donalds_query = f"""
    SELECT DISTINCT customer_id
    FROM delta.central_order_descriptors_odp.order_descriptors_v2
    WHERE order_country_code = 'PL'
      AND order_final_status = 'DeliveredStatus'
      AND order_parent_relationship_type IS NULL
      AND order_is_first_delivered_order = true
      AND store_name = 'McDonald''s'
      AND order_started_local_at < DATE_ADD('day', 1, DATE '{period_end_date}') 
      AND order_started_local_at >= DATE '{period_start_date}'
      LIMIT 100000
    """

    queries = [qsr_query, not_qsr_query, mc_donalds_query]
    results = run_queries(queries)
    return results


def get_qsr_data(period_start_date, period_end_date, store_names, update=True):
    if update or not (os.path.exists('data/customers/qsr_customers.pkl') and os.path.exists('data/customers/not_qsr_customers.pkl') and os.path.exists('data/customers/mc_do.pkl')):
        print("Updating customers data...")
        qsr, not_qsr, mc_do = extract_customers_acquired_through_qsr(period_start_date, period_end_date, store_names)

        if not os.path.exists('data/customers'):
            os.makedirs('data/customers')

        qsr.to_pickle('data/customers/qsr_customers.pkl')
        not_qsr.to_pickle('data/customers/not_qsr_customers.pkl')
        mc_do.to_pickle('data/customers/mc_do.pkl')
        print("Update completed")
    else:
        print("Loading customers data...")
        qsr = pd.read_pickle('data/customers/qsr_customers.pkl')
        not_qsr = pd.read_pickle('data/customers/not_qsr_customers.pkl')
        mc_do = pd.read_pickle('data/customers/mc_do.pkl')
        print("Loading completed")

    return qsr, not_qsr, mc_do

