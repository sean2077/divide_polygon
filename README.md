# divide_polygon

A python implement for dividing polygon algorithm.

```py
def divide_polygon(
    poly: List[Point], n: int, idx: int, tolerance=1e-12, in_place=False
):
    """Divede polygon with parallel lines

    Args:
        poly (List[Point]): counterclockwise polygon with edge p[0]p[-1] on y axis.
        n (int): divisor
        idx (int): edge (p[idx-1]p[idx]) sepcified to parallel with.
        tolerance (float, optional): tolerance, expressed as polygon area percentage. Defaults to 1e-12.
        in_place (bool, optional): whether to operate in place.

    Returns:
        [type]: [description]
    """
```

## Effect Picture

divide into 2 parts:
![divide_2](./images/divide_2.png)
divide into 3 parts:
![divide_3](./images/divide_3.png)
divide into 4 parts:
![divide_4](./images/divide_4.png)
divide into 5 parts:
![divide_5](./images/divide_5.png)
