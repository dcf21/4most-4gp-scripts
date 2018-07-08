# -*- coding: utf-8 -*-

"""
A class for linearly interpolating [x,y] data sets. Can return either y(x), or solve for x(y)
"""


def sgn(x):
    """
    Return the sign of a floating-point number (-1 or 1; never 0)

    :param x:
        Input float
    :return:
        Sign of float (-1 or 1)
    """
    if x < 0.0:
        return -1.0
    else:
        return 1.0


def sort_on_first_item(a, b):
    """
    Helper to sort a list of lists into the order of the first list item.

    :param a:
        Comparison item A
    :param b:
        Comparison item B
    :return:
        Comparison integer
    """
    return int(sgn(a[0] - b[0]))


class LinearInterpolate:
    """
    A class for linearly interpolating [x,y] data sets. Can return either y(x), or solve for x(y)
    """

    def __init__(self, data_set):
        """
        Create linear interpolator.

        :param data_set:
            A list of [x,y] data points.
        """

        # Create a copy of the input list
        self.data_set = list(data_set)

        # Sort into order of ascending x
        self.data_set.sort(sort_on_first_item)

    def compute_x(self, y):
        """
        Compute the value(s) of x which gives a particular value of y in the linear interpolation. As there may
        be mulitple solutions, a list is returned.

        :param y:
            The value of the linearly interpolated function y(x) we are seeking to find x values for.
        :return:
            A list of solutions, which may have length zero, one, or more.
        """

        # If we have fewer than two data points, linear interpolation is impossible
        if len(self.data_set) < 2:
            return []

        output = []
        point_y_old = self.data_set[0][1]
        point_x_old = self.data_set[0][0]
        for point_x, point_y in self.data_set[1:]:
            if (point_y <= y) and (point_y_old > y):
                weight_a = abs(point_y - y)
                weight_b = abs(point_y_old - y)
                output.append((point_x_old * weight_a + point_x * weight_b) / (weight_a + weight_b))
            point_y_old = point_y
            point_x_old = point_x
        return output

    def compute_y(self, x):
        """
        Compute the value(s) of y(x) for some value of x, by linear interpolation.

        :param y:
            The value of the linearly interpolated function y(x) we are seeking to find x values for.
        :return:
            A value of y(x), or None if the supplied value of x is outside the range of the supplied data set.
        """

        # If we have fewer than two data points, linear interpolation is impossible
        if len(self.data_set) < 2:
            return None

        point_y_old = self.data_set[0][1]
        point_x_old = self.data_set[0][0]
        for point_x, point_y in self.data_set[1:]:
            if (point_x <= x) and (point_x_old > x):
                weight_a = abs(point_x - x)
                weight_b = abs(point_x_old - x)
                return (point_y_old * weight_a + point_y * weight_b) / (weight_a + weight_b)
            point_y_old = point_y
            point_x_old = point_x
        return None
