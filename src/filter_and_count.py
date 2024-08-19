import pickle


def filter_and_count_rc_orders(timeframe, store_names, verticals):
    with open(f'../data/{timeframe}/orders.pkl', 'rb') as file:
        orders_dict = pickle.load(file)

    with open(f'../data/{timeframe}/recurrent_customers.pkl', 'rb') as file:
        customers_dict = pickle.load(file)

    results = {}
    for time_span in customers_dict:
        if time_span in orders_dict:
            customers_df = customers_dict[time_span]
            orders_df = orders_dict[time_span].drop_duplicates(subset='order_id')
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

def filter_and_count_promo_yes_no(timeframe, store_names, verticals):
    with open(f'../data/{timeframe}/orders.pkl', 'rb') as file:
        orders_dict = pickle.load(file)

    with open(f'../data/{timeframe}/recurrent_customers.pkl', 'rb') as file:
        customers_dict = pickle.load(file)

    results = {}
    for time_span in customers_dict:
        if time_span in orders_dict:
            customers_df = customers_dict[time_span]
            orders_df = orders_dict[time_span]

            n_orders_by_recurrent_customers = int(orders_df.drop_duplicates(subset='order_id')['customer_id'].isin(customers_df['customer_id']).sum())  # Because some orders might have 2 promos at the same time

            # Calculate the number of promo orders by recurrent customers
            promo_orders_df = orders_df[orders_df['discount_subtype'].notnull()]
            promo_orders_df = promo_orders_df.drop_duplicates(subset='order_id')
            n_promo_orders_by_recurrent_customers = int(promo_orders_df['customer_id'].isin(customers_df['customer_id']).sum())

            # Calculate the number of non-promo orders by recurrent customers
            non_promo_orders_df = orders_df[orders_df['discount_subtype'].isnull()]
            n_non_promo_orders_by_recurrent_customers = int(non_promo_orders_df['customer_id'].isin(customers_df['customer_id']).sum())

            # Calculate the percentages
            if n_orders_by_recurrent_customers > 0:
                promo_percentage = (n_promo_orders_by_recurrent_customers / n_orders_by_recurrent_customers) * 100
                non_promo_percentage = (n_non_promo_orders_by_recurrent_customers / n_orders_by_recurrent_customers) * 100
            else:
                promo_percentage = 0
                non_promo_percentage = 0

            # Store the results
            results[time_span] = {
                'total_orders': n_orders_by_recurrent_customers,
                'promo_orders': n_promo_orders_by_recurrent_customers,
                'non_promo_orders': n_non_promo_orders_by_recurrent_customers,
                'promo_percentage': promo_percentage,
                'non_promo_percentage': non_promo_percentage
            }

    return results

def filter_and_count_rc_orders_top_cities(timeframe, cities):
    with open(f'../data/{timeframe}/orders.pkl', 'rb') as file:
        orders_dict = pickle.load(file)

    with open(f'../data/{timeframe}/recurrent_customers.pkl', 'rb') as file:
        customers_dict = pickle.load(file)

    results = {}
    for time_span in customers_dict:
        if time_span in orders_dict:
            customers_df = customers_dict[time_span]
            orders_df = orders_dict[time_span].drop_duplicates(subset='order_id')
            n_orders_by_recurrent_customers = int(orders_df['customer_id'].isin(customers_df['customer_id']).sum())
            results[time_span] = {}
            results[time_span]['total'] = n_orders_by_recurrent_customers
            results[time_span]['rest'] = n_orders_by_recurrent_customers
            for city in cities:
                store_orders_df = orders_df[orders_df['order_city_code'] == city]
                n_store_orders_by_recurrent_customers = int(store_orders_df['customer_id'].isin(customers_df['customer_id']).sum())
                results[time_span][city] = n_store_orders_by_recurrent_customers
                results[time_span]['rest'] -= n_store_orders_by_recurrent_customers
    return results

def filter_and_count_rc_orders_prime_yes_no(timeframe, prime_list):
    with open(f'../data/{timeframe}/orders.pkl', 'rb') as file:
        orders_dict = pickle.load(file)

    with open(f'../data/{timeframe}/recurrent_customers.pkl', 'rb') as file:
        customers_dict = pickle.load(file)

    results = {}
    for time_span in customers_dict:
        if time_span in orders_dict:
            customers_df = customers_dict[time_span]
            orders_df = orders_dict[time_span].drop_duplicates(subset='order_id')
            n_orders_by_recurrent_customers = int(orders_df['customer_id'].isin(customers_df['customer_id']).sum())
            results[time_span] = {}
            results[time_span]['total'] = n_orders_by_recurrent_customers
            for bool in prime_list:
                store_orders_df = orders_df[orders_df['order_is_prime'] == bool]
                n_store_orders_by_recurrent_customers = int(store_orders_df['customer_id'].isin(customers_df['customer_id']).sum())
                results[time_span][bool] = n_store_orders_by_recurrent_customers
    return results