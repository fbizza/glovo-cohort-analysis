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