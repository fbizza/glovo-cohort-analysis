from extract_qsr_customers import get_qsr_data
from utils import run_queries
from plot_results import plot_dictionaries
from pprint import pprint

def get_customer_ids_str(df):
    """Convert customer IDs to a string for the SQL query"""
    customer_ids = df['customer_id'].astype(int).tolist()
    return ', '.join(str(customer_id) for customer_id in customer_ids)
def build_queries(customer_ids_str):
    """Build SQL queries for various metrics."""
    queries = {
        "stores": f"""
            SELECT customer_id, COUNT(DISTINCT o.store_name) AS n_stores
            FROM delta.central_order_descriptors_odp.order_descriptors_v2 o
            WHERE order_final_status = 'DeliveredStatus'
              AND order_parent_relationship_type IS NULL
              AND customer_id IN ({customer_ids_str})
            GROUP BY customer_id
        """,
        "frequency": f"""
            SELECT customer_id, COUNT(o.order_id) AS order_frequency
            FROM delta.central_order_descriptors_odp.order_descriptors_v2 o
            WHERE order_final_status = 'DeliveredStatus'
              AND order_parent_relationship_type IS NULL
              AND customer_id IN ({customer_ids_str})
            GROUP BY customer_id
        """,
        "retention": f"""
            SELECT customer_id, COUNT(o.order_id) AS order_count
            FROM delta.central_order_descriptors_odp.order_descriptors_v2 o
            WHERE order_final_status = 'DeliveredStatus'
              AND order_parent_relationship_type IS NULL
              AND customer_id IN ({customer_ids_str})
            GROUP BY customer_id
            HAVING COUNT(o.order_id) >= 2
        """,
        "aov_cm": f"""
            SELECT customer_id, ROUND(AVG(order_total_purchase_local*1.00), 2) AS aov,
                   AVG(contribution_margin_eur) AS avg_contribution_margin_eur
            FROM delta.central_order_descriptors_odp.order_descriptors_v2 o
            LEFT JOIN delta.finance_financial_reports_odp.pnl_order_level f
            ON o.order_id = f.order_id
            WHERE order_final_status = 'DeliveredStatus'
              AND order_parent_relationship_type IS NULL
              AND customer_id IN ({customer_ids_str})
            GROUP BY customer_id
        """,
        "negative_cm_percentage": f"""
            SELECT customer_id,
                   1.000 * COUNT(CASE WHEN contribution_margin_eur < 0 THEN o.order_id ELSE NULL END) / COUNT(o.order_id) AS negative_cm_orders_percentage
            FROM delta.central_order_descriptors_odp.order_descriptors_v2 o
            LEFT JOIN delta.finance_financial_reports_odp.pnl_order_level f
            ON o.order_id = f.order_id
            WHERE order_final_status = 'DeliveredStatus'
              AND order_parent_relationship_type IS NULL
              AND customer_id IN ({customer_ids_str})
            GROUP BY customer_id
        """,
        "prime_orders": f"""
            SELECT customer_id,
                   COUNT(CASE WHEN o.order_is_prime THEN o.order_id ELSE NULL END) as prime_orders_count
            FROM delta.central_order_descriptors_odp.order_descriptors_v2 o
            LEFT JOIN delta.finance_financial_reports_odp.pnl_order_level f
            ON o.order_id = f.order_id
            WHERE order_final_status = 'DeliveredStatus'
              AND order_parent_relationship_type IS NULL
              AND customer_id IN ({customer_ids_str})
            GROUP BY customer_id
        """,
        "promo_types": f"""
            SELECT
                1.0000*count(DISTINCT CASE WHEN discount_subtype = 'PROMOTION_TWO_FOR_ONE' THEN o.order_id ELSE NULL END) / count(DISTINCT o.order_id) AS two_for_one_promo_orders,1.0000*count(DISTINCT CASE WHEN discount_subtype = 'MKTG_PROMOCODE' THEN o.order_id ELSE NULL END) / count(DISTINCT o.order_id) AS mktg_promo_code_promo_orders,
                1.0000*count(DISTINCT CASE WHEN discount_subtype = 'PRIME' THEN o.order_id ELSE NULL END) / count(DISTINCT o.order_id) AS prime_promo_orders,
                1.0000*count(DISTINCT CASE WHEN discount_subtype = 'PROMOTION_PERCENTAGE_DISCOUNT' THEN o.order_id ELSE NULL END) / count(DISTINCT o.order_id) AS percentage_discount_promo_orders,
                1.0000*count(DISTINCT CASE WHEN discount_subtype = 'PROMOTION_FREE_DELIVERY' THEN o.order_id ELSE NULL END) / count(DISTINCT o.order_id) free_delivery_promo_orders,
                1.0000*count(DISTINCT CASE WHEN discount_subtype = 'PROMOTION_BASKET_DISCOUNT' THEN o.order_id ELSE NULL END) / count(DISTINCT o.order_id) AS basket_discount_promo_orders,
                1.0000*count(DISTINCT CASE WHEN discount_subtype = 'SEGMENTATION' THEN o.order_id ELSE NULL END) / count(DISTINCT o.order_id) AS segmentation_promo_orders,
                1.0000*count(DISTINCT CASE WHEN discount_subtype = 'PROMOTION_FLAT_DELIVERY' THEN o.order_id ELSE NULL END) / count(DISTINCT o.order_id) AS flat_delivery_promo_orders
            FROM delta.central_order_descriptors_odp.order_descriptors_v2 o
            LEFT JOIN delta.growth_pricing_discounts_odp.pricing_discounts p
            ON p.order_id = o.order_id
            WHERE order_final_status = 'DeliveredStatus'
              AND order_parent_relationship_type IS NULL
              AND customer_id IN ({customer_ids_str})
        """,
        "lto": f"""
            WITH latest_dates AS (
                SELECT customer_id, MAX(p_date) AS latest_p_date
                FROM delta.growth__customer_lto__odp.customer_lto
                GROUP BY customer_id
            ),
            users_5y_total_orders AS (
                SELECT lto.customer_id, lto.first_order_country,
                       lto.predicted_orders_60mo + oh.number_of_orders AS user_5y_lto,
                       ld.latest_p_date
                FROM delta.growth__customer_lto__odp.customer_lto lto
                FULL JOIN delta.growth__customer_lto__odp.customer_order_history oh
                ON lto.customer_id = oh.customer_id AND lto.p_date = oh.p_date
                JOIN latest_dates ld
                ON lto.customer_id = ld.customer_id AND lto.p_date = ld.latest_p_date
            )
            SELECT avg(user_5y_lto) as avg_lto
            FROM users_5y_total_orders
            WHERE customer_id in ({customer_ids_str})
        """
    }
    return queries
def compute_metrics_for_cohort(df):
    """Compute metrics for a given cohort."""
    customer_ids_str = get_customer_ids_str(df)
    queries = build_queries(customer_ids_str)
    results = run_queries(list(queries.values()))
    result_stores, result_frequency, result_retention, result_aov_cm, result_negative_cm_percentage, result_prime_orders, result_promo_types, result_lto = results
    metrics = {
        'avg_n_stores': round(float(result_stores['n_stores'].mean()), 3),
        'avg_order_frequency': round(float(result_frequency['order_frequency'].mean()), 3),
        'second_order_retention': round(len(result_retention) / len(df), 4),
        'avg_aov': round(float(result_aov_cm['aov'].mean()), 2),
        'avg_cm': round(float(result_aov_cm['avg_contribution_margin_eur'].mean()), 2),
        'negative_cm_orders': round(float(result_negative_cm_percentage['negative_cm_orders_percentage'].mean()), 4),
        'prime_users_conversion': round(len(result_prime_orders[result_prime_orders['prime_orders_count'] > 0]) / len(df), 4),
        '5y_lto': float(result_lto['avg_lto'].values[0]),
        'cohort_size': df.shape[0],
    }
    promo_orders_percentage = {col: float(round(result_promo_types[col].iloc[0], 4)) for col in result_promo_types.columns}
    metrics.update(promo_orders_percentage)
    return metrics

def compute_metrics(customers_dfs):
    """Compute metrics for all customer cohorts."""
    metrics_dict = {}
    for df in customers_dfs:
        print(f"\nProcessing cohort {df.name} ({len(df)} customers)...")
        metrics_dict[df.name] = compute_metrics_for_cohort(df)
    return metrics_dict


if __name__ == "__main__":
    qsr_customers, not_qsr_customers, mc_do = get_qsr_data('2024-01-01', '2024-01-31', ["McDonald''s"], update=False)
    qsr_customers.name = 'qsr_customers'
    not_qsr_customers.name = 'not_qsr_customers'
    mc_do.name = 'McDo'
    customers_dfs = [mc_do, qsr_customers, not_qsr_customers]
    metrics_dict = compute_metrics(customers_dfs)

    print("Metrics for McDo customers:")
    pprint(metrics_dict['McDo'])

    print("\nMetrics for QSR customers:")
    pprint(metrics_dict['qsr_customers'])

    print("\nMetrics for non-QSR customers:")
    pprint(metrics_dict['not_qsr_customers'])

    plot_dictionaries(metrics_dict)