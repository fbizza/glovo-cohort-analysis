import pickle



def filter_and_count_rc_orders(store_names, verticals):
    with open('../data/orders.pkl', 'rb') as file:
        orders_dict = pickle.load(file)

    with open('../data/recurrent_customers.pkl', 'rb') as file:
        customers_dict = pickle.load(file)

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

