"""
Script to perform a t-test on two (differentially private) sample means.
The standard deviations copied here are also differentially private.
"""
import json

# function to calculate test-statistic between two independent variables
# without necessarily using the true standard deviation of the data
def calculate_test_statistic(m1, m2, n1, n2, std1, std2, verbose=True):
    s_pooled = (std1 ** 2 / n1 + std2 ** 2 / n2) ** 0.5
    t_statistic = (m1 - m2) / s_pooled
    if verbose:
        print("Degrees of freedom: " + str(min(n1 - 1, n2 - 1)))
    return t_statistic


# read dp values from disk
with open('../../analysis/response_time_sentiment/dp_response_time_std.txt') as f:
    avg_sentiment_data = f.read()
f.close()
with open('../../analysis/response_time_sentiment/dp_count.txt') as f:
    count_data = f.read()
f.close()
with open('../../analysis/response_time_sentiment/dp_response_time_sentiment.txt') as f:
    std_data = f.read()
f.close()

# load json data as dictionaries
dp_avg = json.loads(avg_sentiment_data)
dp_count = json.loads(count_data)
dp_std = json.loads(std_data)

# time category variables are "1", "2", "3", "4", "5"
var_1 = "2"
var_2 = "5"
# calculate test statistic and display
dp_test_statistic = calculate_test_statistic(dp_avg[var_1], dp_avg[var_2], dp_count[var_1], dp_count[var_2], dp_std[var_1], dp_std[var_2])
print(dp_test_statistic)
