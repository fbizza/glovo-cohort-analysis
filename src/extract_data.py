import trino
import pandas as pd
import warnings
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
import pickle
import os


# Set up DB connection
HOST = 'starburst.g8s-data-platform-prod.glovoint.com'
PORT = 443
conn_details = {
    'host': HOST,
    'port': PORT,
    'http_scheme': 'https',
    'auth': trino.auth.OAuth2Authentication()
}
def get_recurrent_customers_for_period(period_start_date, period_end_date):
    sql_query = f"""
    WITH nc as (
    SELECT DISTINCT customer_id
    FROM delta.central_order_descriptors_odp.order_descriptors_v2
    WHERE order_country_code = 'PL'
      AND order_final_status = 'DeliveredStatus'
      AND order_parent_relationship_type IS NULL
      AND order_is_first_delivered_order = true
      AND order_started_local_at <= DATE_ADD('day', 1, DATE '{period_end_date}') and order_started_local_at >= DATE '{period_start_date}'
),
    rc AS (
    SELECT DISTINCT customer_id
    FROM delta.central_order_descriptors_odp.order_descriptors_v2
    WHERE order_country_code = 'PL'
      AND order_final_status = 'DeliveredStatus'
      AND order_parent_relationship_type IS NULL
      AND order_started_local_at <= DATE_ADD('day', 1, DATE '{period_end_date}') and order_started_local_at >= DATE '{period_start_date}'
    EXCEPT
    SELECT * FROM nc
),
    first_period_order_date_rc AS (
    SELECT customer_id, date(MIN(order_started_local_at)) AS period_first_order_date
    FROM delta.central_order_descriptors_odp.order_descriptors_v2
    WHERE customer_id IN (SELECT customer_id FROM rc)
    AND order_started_local_at <= DATE_ADD('day', 1, DATE '{period_end_date}') and order_started_local_at >= DATE '{period_start_date}'
    GROUP BY customer_id
),
    last_order_before_first AS (
    SELECT a.customer_id, date(MAX(b.order_started_local_at)) AS last_order_date
    FROM first_period_order_date_rc a
    LEFT JOIN delta.central_order_descriptors_odp.order_descriptors_v2 b ON a.customer_id = b.customer_id
    WHERE b.order_started_local_at < a.period_first_order_date
    GROUP BY a.customer_id
),
    rc_categorization AS (
    SELECT
        a.customer_id,
        a.period_first_order_date,
        b.last_order_date,
        CASE
            WHEN DATE_DIFF('day', b.last_order_date, a.period_first_order_date) <= 28 THEN 'Ongoing'
            WHEN DATE_DIFF('day', b.last_order_date, a.period_first_order_date) > 28 THEN 'Reactivated'
        END AS customer_status
    FROM first_period_order_date_rc a
    JOIN last_order_before_first b ON a.customer_id = b.customer_id
),
    ongoing_customers AS (
        SELECT customer_id
        FROM rc_categorization
        WHERE customer_status = 'Ongoing'
),
    reactivated_customers AS (
        SELECT customer_id
        FROM rc_categorization
        WHERE customer_status = 'Reactivated'
)
SELECT 'Ongoing' as status, customer_id FROM ongoing_customers
UNION
SELECT 'Reactivated' as status, customer_id FROM reactivated_customers"""
    with trino.dbapi.connect(**conn_details) as conn:
        df = pd.read_sql_query(sql_query, conn)
    return df

def get_orders_for_period(period_start_date, period_end_date):
    sql_query = f"""
        WITH orders AS (
        SELECT order_id,
            DATE (order_started_local_at) AS DATE,
            store_name,
            order_vertical,
            customer_id,
            order_city_code,
            order_is_prime
        FROM delta.central_order_descriptors_odp.order_descriptors_v2 o
        WHERE o.order_country_code = 'PL'
                AND o.order_final_status = 'DeliveredStatus'
                AND o.order_parent_relationship_type IS NULL
                AND order_started_local_at <= DATE_ADD('day', 1, DATE '{period_end_date}') and order_started_local_at >= DATE '{period_start_date}'
        )
    SELECT *
    FROM orders
        """
    with trino.dbapi.connect(**conn_details) as conn:
        df = pd.read_sql_query(sql_query, conn)
    return df

def process_queries(timeframe, n_periods=3):
    recurrent_customers = {}
    orders = {}
    current_date = datetime.now().replace(day=1) - relativedelta(days=1) if timeframe == 'monthly' else datetime.now() - timedelta(days=datetime.now().weekday() + 1)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        for i in tqdm(range(n_periods), desc="Processing queries"):
            if timeframe == 'monthly':
                end_date = current_date - relativedelta(months=i)
                start_date = end_date.replace(day=1)
            else:
                end_date = current_date - timedelta(weeks=i)
                start_date = end_date - timedelta(days=6)
            df_customers = get_recurrent_customers_for_period(start_date.strftime('%Y-%m-%d'),
                                                              end_date.strftime('%Y-%m-%d'))
            recurrent_customers[f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"] = df_customers
            df_orders = get_orders_for_period(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
            orders[f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"] = df_orders
        print("Completed processing all periods.")
    os.makedirs('../data', exist_ok=True)
    with open(f'../data/{timeframe}/recurrent_customers.pkl', 'wb') as file:
        pickle.dump(recurrent_customers, file)
    with open(f'../data/{timeframe}/orders.pkl', 'wb') as file:
        pickle.dump(orders, file)
    print("Recurrent customers and orders saved into files")
