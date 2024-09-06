import numpy as np
import matplotlib.pyplot as plt

# Define the variables
CM = 1.283610478
iNC = 26906
Avg_LTO_NC = 9.759672326503
Total_investment = 126344

# Compute ROI for values of iNC ranging from 0 to the given iNC
inc_values = np.arange(0, iNC + 1)
roi_values = ((CM * inc_values * Avg_LTO_NC) + (iNC * CM))/ Total_investment

# Identify the first value of iNC that results in an ROI greater than 1
first_inc_greater_than_1 = np.argmax(roi_values > 1)

# Plot the ROI trend
plt.figure(figsize=(10, 6))
plt.plot(inc_values, roi_values, label='ROI')
plt.axvline(x=first_inc_greater_than_1, color='red', linestyle='--', label=f'First iNC ROI > 1: {first_inc_greater_than_1}')
plt.axvline(x=26906, color='black', linestyle='--', label=f'Considered iNC: 27148')
plt.xlabel('iNC')
plt.ylabel('ROI')
plt.title('ROI Trend for Different Values of iNC')
plt.legend()
plt.show()
