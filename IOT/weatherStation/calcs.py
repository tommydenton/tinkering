from meteocalc import Temp, dew_point, heat_index

# create input temperature in different units
t = Temp(20, 'c')  # c - celsius, f - fahrenheit, k - kelvin
t2 = Temp(60, 'f')

# calculate Dew Point
dp = dew_point(temperature=t, humidity=56)

# calculate Heat Index
hi = heat_index(temperature=t2, humidity=42)

print('Dew Point in celsius:', dp.c)
print('Dew Point in fahrenheit:', dp.f)
print('Heat Index in kelvin:', hi.k)
