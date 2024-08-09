import extract_data, filter_and_count, plot

timeframe = 'monthly'
n_periods = 3
store_names = ["McDonald's", 'KFC']
verticals = ['QCommerce']

#extract_data.process_queries(timeframe, n_periods)
results = filter_and_count.filter_and_count_rc_orders(store_names, verticals)
plot.plot_results(results, timeframe)
