import trino
import pandas as pd
import warnings
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from tqdm import tqdm
import pickle
import os
import matplotlib.pyplot as plt
import numpy as np

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
    first_monthly_order_date_rc AS (
    SELECT customer_id, date(MIN(order_started_local_at)) AS monthly_first_order_date
    FROM delta.central_order_descriptors_odp.order_descriptors_v2
    WHERE customer_id IN (SELECT customer_id FROM rc)
    AND order_started_local_at <= DATE_ADD('day', 1, DATE '{period_end_date}') and order_started_local_at >= DATE '{period_start_date}'
    GROUP BY customer_id
),
    last_order_before_first AS (
    SELECT a.customer_id, date(MAX(b.order_started_local_at)) AS last_order_date
    FROM first_monthly_order_date_rc a
    LEFT JOIN delta.central_order_descriptors_odp.order_descriptors_v2 b ON a.customer_id = b.customer_id
    WHERE b.order_started_local_at < a.monthly_first_order_date
    GROUP BY a.customer_id
),
    rc_categorization AS (
    SELECT
        a.customer_id,
        a.monthly_first_order_date,
        b.last_order_date,
        CASE
            WHEN DATE_DIFF('day', b.last_order_date, a.monthly_first_order_date) <= 28 THEN 'Ongoing'
            WHEN DATE_DIFF('day', b.last_order_date, a.monthly_first_order_date) > 28 THEN 'Reactivated'
        END AS customer_status
    FROM first_monthly_order_date_rc a
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
            customer_id
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


def filter_and_count_rc_orders(customers_dict, orders_dict, store_names, verticals):
    results = {}
    for time_span in customers_dict:
        if time_span in orders_dict:
            customers_df = customers_dict[time_span]
            orders_df = orders_dict[time_span]
            n_orders_by_recurrent_customers = int(orders_df['customer_id'].isin(customers_df['customer_id']).sum())
            results[time_span] = {}
            results[time_span]['total'] = n_orders_by_recurrent_customers
            results[time_span]['rest'] = n_orders_by_recurrent_customers
            for store in store_names:
                store_orders_df = orders_df[orders_df['store_name'] == store]
                n_store_orders_by_recurrent_customers = int(
                    store_orders_df['customer_id'].isin(customers_df['customer_id']).sum())
                results[time_span][store] = n_store_orders_by_recurrent_customers
                results[time_span]['rest'] -= n_store_orders_by_recurrent_customers
            for vertical in verticals:
                vertical_orders_df = orders_df[orders_df['order_vertical'] == vertical]
                n_vertical_orders_by_recurrent_customers = int(
                    vertical_orders_df['customer_id'].isin(customers_df['customer_id']).sum())
                results[time_span][vertical] = n_vertical_orders_by_recurrent_customers
                results[time_span]['rest'] -= n_vertical_orders_by_recurrent_customers
    return results


def process_queries(timeframe='monthly', n_periods=13):
    recurrent_customers = {}
    orders = {}
    current_date = datetime.now().replace(day=1) - relativedelta(days=1) if timeframe == 'monthly' \
        else datetime.now() - timedelta(days=datetime.now().weekday() + 1)
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
    os.makedirs('data', exist_ok=True)
    with open('data/recurrent_customers.pkl', 'wb') as file:
        pickle.dump(recurrent_customers, file)
    with open('data/orders.pkl', 'wb') as file:
        pickle.dump(orders, file)
    return recurrent_customers, orders


def plot_results(results, timeframe):
    print(results)
    dates = list(results.keys())

    if timeframe == 'monthly':
        periods = [pd.to_datetime(date.split(' to ')[0]).strftime('%b %y') for date in dates]
    else:
        periods = [pd.to_datetime(date.split(' to ')[0]).strftime('%d %b %y') for date in dates]

    totals = [results[date]['total'] for date in dates]
    sorted_indices = np.argsort([pd.to_datetime(date.split(' to ')[0]) for date in dates])
    periods = [periods[i] for i in sorted_indices]
    totals = [totals[i] for i in sorted_indices]
    results = {dates[i]: results[dates[i]] for i in sorted_indices}

    categories = set()
    for value in results.values():
        categories.update(value.keys())
    categories.discard('total')
    categories.discard('rest')
    categories = list(categories)

    category_values = {category: [results[date].get(category, 0) for date in results.keys()] for category in categories}
    rest = [results[date]['rest'] for date in results.keys()]
    category_percentages = {category: [value / total * 100 for value, total in zip(values, totals)] for category, values
                            in category_values.items()}
    rest_pct = [r / t * 100 for r, t in zip(rest, totals)]

    fig, ax = plt.subplots(figsize=(12, 6))
    bottoms = np.zeros(len(dates))
    bars = {}

    for category in categories:
        bars[category] = ax.bar(periods, category_values[category], bottom=bottoms, label=category)
        bottoms += category_values[category]

    bars['rest'] = ax.bar(periods, rest, bottom=bottoms, label='Rest')
    ax.set_title('Recurrent customers orders')
    ax.legend()

    def add_labels(bars, percentages):
        for bar, pct in zip(bars, percentages):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_y() + height / 2,
                f'{pct:.1f}%',
                ha='center',
                va='center',
                color='white',
                fontsize=7,
                fontweight='bold'
            )

    for category in categories:
        add_labels(bars[category], category_percentages[category])
    add_labels(bars['rest'], rest_pct)
    if timeframe == 'monthly':
        for i, total in enumerate(totals):
            ax.text(
                i,
                bottoms[i] + rest[i],
                f'{total / 1e6:.2f}M',
                ha='center',
                va='bottom',
                fontsize=8
            )
    elif (timeframe == 'weekly'):
        for i, total in enumerate(totals):
            ax.text(
                i,
                bottoms[i] + rest[i],
                f'{total / 1e3:.0f}k',
                ha='center',
                va='bottom',
                fontsize=8
            )


    ax.yaxis.set_visible(False)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('monthly2.png')


# Example usage
recurrent_customers, orders = process_queries(timeframe='monthly', n_periods=3)
results = filter_and_count_rc_orders(recurrent_customers, orders, ["McDonald's", 'KFC'], ['QCommerce'])
plot_results(results, 'monthly')