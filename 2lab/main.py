import itertools
import functools
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as PltPolygon
from matplotlib.collections import PatchCollection

def count_2D(start=(0, 0), step=(1, 0)):
    x, y = start
    dx, dy = step
    while True:
        yield (x, y)
        x += dx
        y += dy

def zip_polygons(*iterators):
    return map(lambda polys: sum(polys, ()), zip(*iterators))

def zip_tuple(*iterators):
    return map(tuple, zip(*iterators))

def gen_rectangle(width=1.0, height=1.0, start=(0, 0), step=(1.5, 0)):
    return map(lambda p: (
        (p[0], p[1]),
        (p[0] + width, p[1]),
        (p[0] + width, p[1] + height),
        (p[0], p[1] + height)
    ), count_2D(start, step))

def gen_triangle(base=1.0, height=1.0, start=(0, 0), step=(1.5, 0)):
    return map(lambda p: (
        (p[0], p[1]),
        (p[0] + base / 2, p[1] + height),
        (p[0] + base, p[1])
    ), count_2D(start, step))

def gen_hexagon(side=1.0, start=(0, 0), step=(2.0, 0)):
    h = math.sqrt(3) / 2 * side
    return map(lambda p: (
        (p[0] - side / 2, p[1] + h),
        (p[0] + side / 2, p[1] + h),
        (p[0] + side, p[1]),
        (p[0] + side / 2, p[1] - h),
        (p[0] - side / 2, p[1] - h),
        (p[0] - side, p[1])
    ), count_2D(start, step))

def tr_translate(poly, dx, dy):
    return tuple((x + dx, y + dy) for x, y in poly)

def tr_rotate(poly, angle_deg, center=(0, 0)):
    cx, cy = center
    rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    return tuple(
        (cx + (x - cx) * cos_a - (y - cy) * sin_a,
         cy + (x - cx) * sin_a + (y - cy) * cos_a)
        for x, y in poly
    )

def tr_symmetry(poly, center=(0, 0)):
    cx, cy = center
    return tuple((2 * cx - x, 2 * cy - y) for x, y in poly)

def tr_homothety(poly, k, center=(0, 0)):
    cx, cy = center
    return tuple((cx + k * (x - cx), cy + k * (y - cy)) for x, y in poly)

def dec_tr_translate(dx, dy):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return map(lambda p: tr_translate(p, dx, dy), func(*args, **kwargs))
        return wrapper
    return decorator

def _polygon_area(poly):
    x = [p[0] for p in poly]
    y = [p[1] for p in poly]
    return 0.5 * abs(sum(x[i] * y[i - 1] - x[i - 1] * y[i] for i in range(len(poly))))

def _edge_lengths(poly):
    return [math.hypot(poly[i][0] - poly[i - 1][0], poly[i][1] - poly[i - 1][1]) for i in range(len(poly))]

def flt_convex_polygon(poly):
    n = len(poly)
    if n < 3: return False
    def cross_product(p1, p2, p3):
        return (p2[0] - p1[0]) * (p3[1] - p2[1]) - (p2[1] - p1[1]) * (p3[0] - p2[0])
    signs = [cross_product(poly[i - 2], poly[i - 1], poly[i]) > 0 for i in range(n)]
    return all(signs) or not any(signs)

def flt_angle_point(poly, point, tol=1e-6):
    return any(math.isclose(v[0], point[0], abs_tol=tol) and math.isclose(v[1], point[1], abs_tol=tol) for v in poly)

def flt_square(poly, max_area):
    return _polygon_area(poly) < max_area

def flt_short_side(poly, max_length):
    return min(_edge_lengths(poly)) < max_length

def flt_point_inside(poly, point):
    x, y = point
    n = len(poly)
    inside = False
    p1x, p1y = poly[0]
    for i in range(n + 1):
        p2x, p2y = poly[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xints = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xints:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside and flt_convex_polygon(poly)

def flt_polygon_angles_inside(poly, test_poly):
    return any(flt_point_inside(poly, v) for v in test_poly) and flt_convex_polygon(poly)

def agr_area(polygons):
    return functools.reduce(lambda acc, poly: acc + _polygon_area(poly), polygons, 0)

def draw_polygons(poly_iters_with_titles, limit=7, figsize=(10, 8)):
    num_plots = len(poly_iters_with_titles)
    fig, axes = plt.subplots(num_plots, 1, figsize=figsize)
    if num_plots == 1:
        axes = [axes]
        
    for ax, (title, poly_iter) in zip(axes, poly_iters_with_titles):
        polygons = list(itertools.islice(poly_iter, limit))
        
        patches = [PltPolygon(poly, closed=True) for poly in polygons]
        p = PatchCollection(patches, alpha=0.3, edgecolor='black', facecolor='red')
        ax.add_collection(p)
        
        all_x = [x for poly in polygons for x, _ in poly]
        all_y = [y for poly in polygons for _, y in poly]
        if all_x and all_y:
            ax.set_xlim(min(all_x) - 0.5, max(all_x) + 0.5)
            ax.set_ylim(min(all_y) - 0.5, max(all_y) + 0.5)
            
        ax.set_title(title)
        ax.grid(True, linestyle='--', alpha=0.6)
        ax.set_aspect('equal')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    draw_polygons([
        ("Прямоугольники", gen_rectangle(width=1, height=1, start=(-4, 0), step=(1.2, 0))),
        ("Треугольники", gen_triangle(base=1, height=1, start=(-4, 0), step=(1.2, 0))),
        ("Шестиугольники", gen_hexagon(side=0.6, start=(-3.5, 0), step=(1.5, 0)))
    ], limit=7, figsize=(10, 6))

    r1 = map(lambda p: tr_rotate(p, 30, center=(0,0)), gen_rectangle(0.8, 0.4, (-3, -1), (0.9, 0)))
    r2 = map(lambda p: tr_rotate(p, 30, center=(0,0)), gen_rectangle(0.8, 0.4, (-3, -0.4), (0.9, 0)))
    r3 = map(lambda p: tr_rotate(p, 30, center=(0,0)), gen_rectangle(0.8, 0.4, (-3, 0.2), (0.9, 0)))
    
    ribbons = itertools.chain(
        itertools.islice(r1, 8),
        itertools.islice(r2, 8),
        itertools.islice(r3, 8)
    )
    t_up = gen_triangle(base=1.2, height=1.2, start=(-4, 0), step=(1.3, 0))
    t_down = gen_triangle(base=1.2, height=-1.2, start=(-4, 0), step=(1.3, 0))
    rhombuses = zip_polygons(t_up, t_down)

    draw_polygons([
        ("Три параллельные ленты", ribbons),
        ("Полигоны (Ромбы через zip_polygons)", rhombuses)
    ], limit=24, figsize=(8, 7))

    base_rects = gen_rectangle(width=0.6, height=0.4, start=(0, 0), step=(1, 0))
    filtered_rects = filter(lambda p: flt_square(p, max_area=0.5), base_rects)
    
    exact_six_figures = itertools.islice(filtered_rects, 6)
    draw_polygons([("Применение фильтра: ровно 6 фигур (Площадь < 0.5)", exact_six_figures)], limit=6, figsize=(10, 2))
