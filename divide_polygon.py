"""
Author       : zhangxianbing
Date         : 2021-01-11 09:01:15
LastEditors  : zhangxianbing
LastEditTime : 2021-01-11 14:42:51
Description  : Divide polygon
"""

from math import sqrt
from typing import List


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"({self.x:.2f}, {self.y:.2f})"


def _cross_point(p1: Point, p2: Point, x):
    y = (p2.y - p1.y) / (p2.x - p1.x) * (x - p1.x) + p1.y
    return Point(x, y)


def _sep_polygon_lines(p: List[Point]):
    t, b = -1, 0
    rt = p[t]  # right top point
    rb = p[b]  # right bottom point
    lt = rt  # left top point
    lb = rb  # left bottom point
    lines = []
    while True:
        if p[t - 1].x < p[b + 1].x:
            rt = p[t - 1]
            rb = _cross_point(lb, p[b + 1], p[t - 1].x)
            t = t - 1
        elif p[t - 1].x > p[b + 1].x:
            rt = _cross_point(lt, p[t - 1], p[b + 1].x)
            rb = p[b + 1]
            b = b + 1
        else:
            rt = p[t - 1]
            rb = p[b + 1]
            t = t - 1
            b = b + 1
        if rt.y < rb.y:
            break
        lines.append(((rb, rt)))
        lt = rt
        lb = rb
    return lines


def _eval_polygon_area(p: List[Point]):
    """evaluate area of a polygon using shoelace formula."""
    area = 0.0
    n = len(p)
    j = n - 1
    for i in range(0, n):
        area += (p[j].x + p[i].x) * (p[j].y - p[i].y)
        j = i

    return abs(area / 2.0)


def _eval_trapezoid_area(l1: List[Point], l2: List[Point]):
    a = l1[1].y - l1[0].y
    b = l2[1].y - l2[0].y
    h = l2[0].x - l1[0].x
    return (a + b) * h / 2.0


def _sep_trapeziod_area(l1: List[Point], l2: List[Point], A):
    a = l1[1].y - l1[0].y
    b = l2[1].y - l2[0].y
    h = l2[0].x - l1[0].x
    S = (a + b) * h / 2.0
    if a == b:
        lmd = A / (S - A)
    else:
        c = sqrt(a ** 2 + (A / S) * (b ** 2 - a ** 2))
        lmd = (c - a) / (b - c)
    return (l1[0].x + lmd * l2[0].x) / (1 + lmd)


def divide_polygon(p: List[Point], n: int, tolerance=1e-12):
    """Divede polygon with parallel lines

    Args:
        p (List[Point]): counterclockwise polygon with edge p[0]p[-1] on y axis.
        n (int): divisor
        tolerance (float, optional): tolerance, expressed as polygon area percentage. Defaults to 1e-12.

    Returns:
        [type]: [description]
    """
    res = []
    sep_lines = _sep_polygon_lines(p)
    area = _eval_polygon_area(p)
    tol_area = area * tolerance
    des_area = area / n
    cur_area = 0.0
    left_line = (p[0], p[-1])
    i = 0

    while i < len(sep_lines) and len(res) < n - 1:
        right_line = sep_lines[i]
        trap_area = _eval_trapezoid_area(left_line, right_line)
        delta_area = des_area - (trap_area + cur_area)

        if delta_area > tol_area:
            left_line = right_line
            cur_area += trap_area
            i += 1

        elif delta_area < tol_area:
            x = _sep_trapeziod_area(left_line, right_line, des_area - cur_area)
            bott = _cross_point(left_line[0], right_line[0], x)
            top = _cross_point(left_line[1], right_line[1], x)
            left_line = (bott, top)
            res.append(left_line)
            cur_area = 0.0

        elif abs(delta_area) <= tol_area:
            left_line = right_line
            res.append(left_line)
            cur_area = 0.0
            i += 1

    return res


if __name__ == "__main__":
    p1 = [
        Point(0, 0),
        Point(0.5, -1),
        Point(1.5, -1.5),
        Point(2.5, -1.5),
        Point(3.5, -1),
        Point(3.5, 3),
        Point(2.5, 3.5),
        Point(1, 3),
        Point(0, 1),
    ]
    # print(_sep_polygon_lines(polygon))

    # print(_eval_polygon_area([Point(0, 1), Point(2, 3), Point(4, 7)]))

    # print(
    #     _sep_trapeziod_area(
    #         [Point(0.0, 0.0), Point(0.0, 1.0)],
    #         [Point(1.0, 0.00), Point(1.0, 1.00)],
    #         0.5,
    #     )
    # )
    for i in range(2, 10):
        print(divide_polygon(p1, i))
