import sys
sys.path.append('/geometric_lib')
import circle

with open('config.txt', 'r') as f:
    r = float(f.read().strip())

area = circle.area(r)
print(f"Площадь круга с радиусом {r} = {area}")