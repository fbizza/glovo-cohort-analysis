import extract_data, filter_and_count, plot

timeframe = 'weekly'
n_periods = 13
cities = ['WAW', 'KRA', 'LOD', 'GDN', 'WRO', 'POZ']

#extract_data.process_queries(timeframe, n_periods)
results = filter_and_count.filter_and_count_rc_orders_top_cities(timeframe, cities)
plot.plot_results(results, timeframe, save_plot=True, show_plot=True, print_results_to_console=True)