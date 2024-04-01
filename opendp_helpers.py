"""
Foundational transformation and measurement constructors.
"""
from opendp.transformations import make_split_dataframe, make_select_column
from opendp.transformations import then_cast_default, then_clamp, then_resize, then_mean, then_sum
from opendp.transformations import then_count
from opendp.measurements import then_laplace
from opendp.mod import enable_features, binary_search_param
from opendp.accuracy import laplacian_scale_to_accuracy
from opendp.measurements import then_base_laplace
from opendp.domains import atom_domain
enable_features("contrib")


"""
Function to calibrate Laplacian noise scale to a given privacy budget.
Output: a private measurement function.
"""
def make_meas(transformation, budget=0.5, max_contributions=1, alpha=0.05, verbose=True):
    # instantiate lambda function
    make_chain = lambda s: transformation >> then_laplace(s)
    # use OpenDP's built-in binary_search_param() function to find correct scale
    scale = binary_search_param(make_chain, d_in=max_contributions, d_out=budget)
    # create the measurement using the lambda function
    measurement = make_chain(scale)
    # calculate the measurement's corresponding accuracy
    accuracy = laplacian_scale_to_accuracy(scale, alpha)
    # verbose output
    if verbose:
        print("*"*40)
        print("New scale for measurement: " + str(scale))
        print(f"When the laplace scale is {scale}, "
         f"the DP estimate differs from the true value by no more than {accuracy} "
         f"at a statistical significance level alpha of {alpha}, "
         f"or with (1 - {alpha})100% = {(1 - alpha) * 100}% confidence.")
        print('epsilon with scale ' + str(scale) + ': ' + str(measurement.map(d_in=max_contributions)))
    return measurement


# create a column transformation
def create_col_trans(col_name, col_type, metadata):
    col_trans = (
        make_split_dataframe(separator=",", col_names=metadata["column_names"]) >>
        make_select_column(col_name, col_type)
    )
    return col_trans


# create a counting transformation
def create_count_trans(col_trans):
    count_trans = (
        # chain an input column transformation with a counting function
        col_trans >>
        then_count()
        )
    return count_trans


# create a sum transformation
def create_sum_trans(length_bounds, col_trans):
    sum_trans = (
        # chain an input column transformation with a sum function
        col_trans >>
        then_cast_default(float) >>
        # clamp the data to given bounds
        then_clamp(bounds=length_bounds) >>
        then_sum()
        )
    return sum_trans


# create a mean transformation
def create_mean_trans(length_bounds, dp_count, col_trans, constant=None):
    mean_trans = (
        # chain an input column transformation with a mean function
        col_trans >>
        then_cast_default(float) >>
        # clamp the data to given bounds
        then_clamp(bounds=length_bounds) >>
        # resize the dataset according to the private count of elements
        then_resize(size=dp_count, constant=constant) >>
        then_mean()
        )
    return mean_trans
