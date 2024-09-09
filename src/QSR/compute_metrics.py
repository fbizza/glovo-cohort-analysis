from extract_qsr_customers import get_qsr_data
from utils import run_queries
from plot_results import plot_dictionaries

def compute_metrics(customers_dfs):
    metrics_dict = {}

    for i, df in enumerate(customers_dfs, start=1):

        customer_ids = df['customer_id'].astype(int).tolist()
        customer_ids_str = ', '.join(str(customer_id) for customer_id in customer_ids)
        print(f"\nProcessing cohort {i} ({len(customer_ids)} customers)...")

        # avg number of different stores customers ordered from
        query_stores = f"""
        SELECT
            customer_id,
            COUNT(DISTINCT o.store_name) AS n_stores
        FROM delta.central_order_descriptors_odp.order_descriptors_v2 o
        WHERE order_final_status = 'DeliveredStatus'
          AND order_parent_relationship_type IS NULL
          AND customer_id IN ({customer_ids_str})
        GROUP BY customer_id
        """

        # avg frequency
        query_frequency = f"""
        SELECT
            customer_id,
            COUNT(o.order_id) AS order_frequency
        FROM delta.central_order_descriptors_odp.order_descriptors_v2 o
        WHERE order_final_status = 'DeliveredStatus'
          AND order_parent_relationship_type IS NULL
          AND customer_id IN ({customer_ids_str})
        GROUP BY customer_id
        """

        # retention: percentage of customers who placed at least two orders
        query_retention = f"""
        SELECT
            customer_id,
            COUNT(o.order_id) AS order_count
        FROM delta.central_order_descriptors_odp.order_descriptors_v2 o
        WHERE order_final_status = 'DeliveredStatus'
          AND order_parent_relationship_type IS NULL
          AND customer_id IN ({customer_ids_str})
        GROUP BY customer_id
        HAVING COUNT(o.order_id) >= 2
        """

        # avg order value (AOV) and avg contribution margin (CM)
        query_aov_cm = f"""
              SELECT
                  customer_id,
                  ROUND(AVG(order_total_purchase_local*1.00), 2) AS aov,
                  AVG(contribution_margin_eur) AS avg_contribution_margin_eur
              FROM delta.central_order_descriptors_odp.order_descriptors_v2 o
              LEFT JOIN delta.finance_financial_reports_odp.pnl_order_level f
              ON o.order_id = f.order_id
              WHERE order_final_status = 'DeliveredStatus'
                AND order_parent_relationship_type IS NULL
                AND customer_id IN ({customer_ids_str})
              GROUP BY customer_id
              """

        # percentage of negative CM orders
        query_negative_cm_percentage = f"""
                SELECT
                    customer_id,
                    1.000 * COUNT(CASE WHEN contribution_margin_eur < 0 THEN o.order_id ELSE NULL END) / COUNT(o.order_id) AS negative_cm_orders_percentage
                FROM delta.central_order_descriptors_odp.order_descriptors_v2 o
                LEFT JOIN delta.finance_financial_reports_odp.pnl_order_level f
                ON o.order_id = f.order_id
                WHERE order_final_status = 'DeliveredStatus'
                  AND order_parent_relationship_type IS NULL
                  AND customer_id IN ({customer_ids_str})
                GROUP BY customer_id
                """

        # for computing percentage of customers who became prime users
        query_count_prime_orders = f"""
                        SELECT
                            customer_id,
                            COUNT(CASE WHEN o.order_is_prime THEN o.order_id ELSE NULL END) as prime_orders_count
                        FROM delta.central_order_descriptors_odp.order_descriptors_v2 o
                        LEFT JOIN delta.finance_financial_reports_odp.pnl_order_level f
                        ON o.order_id = f.order_id
                        WHERE order_final_status = 'DeliveredStatus'
                          AND order_parent_relationship_type IS NULL
                          AND customer_id IN ({customer_ids_str})
                        GROUP BY customer_id
                        """

        query_promo_types = f"""
                                SELECT 
                                    1.0000*count(DISTINCT CASE WHEN discount_subtype = 'PROMOTION_TWO_FOR_ONE' THEN o.order_id ELSE NULL END) / count(DISTINCT o.order_id) AS two_for_one_promo_orders,
                                    1.0000*count(DISTINCT CASE WHEN discount_subtype = 'MKTG_PROMOCODE' THEN o.order_id ELSE NULL END) / count(DISTINCT o.order_id) AS mktg_promo_code_promo_orders,
                                    1.0000*count(DISTINCT CASE WHEN discount_subtype = 'PRIME' THEN o.order_id ELSE NULL END) / count(DISTINCT o.order_id) AS prime_promo_orders,
                                    1.0000*count(DISTINCT CASE WHEN discount_subtype = 'PROMOTION_PERCENTAGE_DISCOUNT' THEN o.order_id ELSE NULL END) / count(DISTINCT o.order_id) AS percentage_discount_promo_orders,
                                    1.0000*count(DISTINCT CASE WHEN discount_subtype = 'PROMOTION_FREE_DELIVERY' THEN o.order_id ELSE NULL END) / count(DISTINCT o.order_id) free_delivery_promo_orders,
                                    1.0000*count(DISTINCT CASE WHEN discount_subtype = 'PROMOTION_BASKET_DISCOUNT' THEN o.order_id ELSE NULL END) / count(DISTINCT o.order_id) AS basket_discount_promo_orders,
                                    1.0000*count(DISTINCT CASE WHEN discount_subtype = 'SEGMENTATION' THEN o.order_id ELSE NULL END) / count(DISTINCT o.order_id) AS segmentation_promo_orders,
                                    1.0000*count(DISTINCT CASE WHEN discount_subtype = 'PROMOTION_FLAT_DELIVERY' THEN o.order_id ELSE NULL END) / count(DISTINCT o.order_id) AS flat_delivery_promo_orders
                                FROM delta.central_order_descriptors_odp.order_descriptors_v2 o LEFT JOIN delta.growth_pricing_discounts_odp.pricing_discounts p ON p.order_id = o.order_id
                                WHERE order_final_status = 'DeliveredStatus'
                                    AND order_parent_relationship_type IS NULL
                                    AND customer_id IN ({customer_ids_str})
                                """

        # Run the queries
        results = run_queries([query_stores, query_frequency, query_retention, query_aov_cm, query_negative_cm_percentage, query_count_prime_orders, query_promo_types])
        result_stores, result_frequency, result_retention, result_aov_cm, result_negative_cm_percentage, result_prime_orders, result_promo_types = results
        # Compute the metrics
        avg_n_stores = round(float(result_stores['n_stores'].mean()), 3)
        avg_order_frequency = round(float(result_frequency['order_frequency'].mean()), 3)
        retention_rate = round(len(result_retention) / len(customer_ids), 4)
        avg_aov = round(float(result_aov_cm['aov'].mean()), 2)
        avg_cm_eur = round(float(result_aov_cm['avg_contribution_margin_eur'].mean()), 2)
        negative_cm_orders_percentage = round(float(result_negative_cm_percentage['negative_cm_orders_percentage'].mean()), 4)
        prime_users_percentage = round(len(result_prime_orders[result_prime_orders['prime_orders_count'] > 0]) / len(customer_ids), 4)
        promo_orders_percentage = {col: float(round(result_promo_types[col].iloc[0], 4)) for col in result_promo_types.columns}


        # Save metrics in the dictionary
        metrics_dict[df.name] = {
            'avg_n_stores': avg_n_stores,
            'avg_order_frequency': avg_order_frequency,
            'second_order_retention': retention_rate,
            'avg_aov': avg_aov,
            'avg_cm': avg_cm_eur,
            'negative_cm_orders': negative_cm_orders_percentage,
            'prime_users_conversion': prime_users_percentage,
        }
        metrics_dict[df.name].update(promo_orders_percentage)
    return metrics_dict

# Example usage
if __name__ == "__main__":
    qsr_customers, not_qsr_customers, mc_do = get_qsr_data('2024-01-01', '2024-01-31', ["McDonald''s"], update=False)
    qsr_customers.name = 'qsr_customers'
    not_qsr_customers.name = 'not_qsr_customers'
    mc_do.name = 'McDo'
    customers_dfs = [mc_do, qsr_customers, not_qsr_customers]
    metrics_dict = compute_metrics(customers_dfs)

    print("Metrics for McDo customers:", metrics_dict['McDo'])
    print("Metrics for QSR customers:", metrics_dict['qsr_customers'])
    print("Metrics for non-QSR customers:", metrics_dict['not_qsr_customers'])
    plot_dictionaries(metrics_dict)