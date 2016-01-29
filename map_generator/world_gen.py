import itertools
import random
import math
import noise
import numpy as np
from PIL import Image
from PIL import ImageColor
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

class Hypsography(object):

	xp = [0.0, 0.01, 0.02, 0.06, 0.1, 0.15, 0.2, 0.25, 0.3, 0.31, 0.33, 0.35,
		0.4, 0.45, 0.5, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.97, 0.98,
		0.99, 1.0]

	fp = [1.0, 0.76, 0.66, 0.61, 0.58, 0.57, 0.56, 0.56, 0.56, 0.55, 0.54, 0.53,
		0.47, 0.43, 0.4, 0.37, 0.35, 0.34, 0.34, 0.33, 0.33, 0.32, 0.3, 0.28,
		0.24, 0.15, 0.0]

	@classmethod
	def simplex_to_uniform(cls, values):
		sigma = 0.26
		range_x = 1.4
		for i in range(len(values)):
			values[i] = math.erf((values[i] / range_x) / sigma)
			values[i] = -0.5 * values[i] + 0.5
		return values

	@classmethod
	def height_from_simplex(cls, values):
		values = cls.simplex_to_uniform(values)
		values = np.interp(values, cls.xp, cls.fp)
		return values


class Map2D(object):

	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.map_list = [0] * (self.width * self.height)

	def is_on_map(self, x, y):
		return x >= 0 and x < self.width and y >= 0 and y < self.height

	def i_is_on_map(self, i):
		return i >= 0 and i < len(self.map_list)

	def coords_to_i(self, x, y):
		return y * self.width + x

	def i_to_coorsds(self, i):
		return (i % self.width, i // self.height)

	def get_pixel(self, x, y):
		assert self.is_on_map(x, y), 'coordinates out of bounds'
		return self.map_list[self.coords_to_i(x, y)]

	def set_pixel(self, x, y, value):
		assert self.is_on_map(x, y), 'coordinates out of bounds'
		self.map_list[self.coords_to_i(x, y)] = value

	def inc_pixel(self, x, y, value):
		assert self.is_on_map(x, y), 'coordinates out of bounds'
		self.map_list[self.coords_to_i(x, y)] += value

	def surrounding_indeces(self, i):
		surrounding = [
			i + self.width,
			i - self.width,
			i + 1,
			i - 1
		]
		return [j for j in surrounding if self.i_is_on_map(j)]


class HeightMap(Map2D):

	def __init__(self, width, height):
		super(HeightMap, self).__init__(width, height)

	def generate(self):
		for x in range(self.width):
			for y in range(self.height):
				nx = x / 600
				ny = y / 600
				simplex = noise.snoise2(nx, ny, octaves=4, persistence=0.5, lacunarity=2.0)
				self.set_pixel(x, y, simplex)
		self.map_list = Hypsography.height_from_simplex(self.map_list)

	def plot_histogram(self):
		n, bins, patches = plt.hist(self.map_list, 100, normed=1, facecolor='green',
			alpha=0.5)
		plt.xlabel('Height')
		plt.ylabel('Probability')
		plt.show()

	def height_to_rgb(self, height):
		return (int(height * 255), int(height * 255), int(height * 255))

	def as_rgb(self):
		return [self.height_to_rgb(h) for h in self.map_list]

	def render(self):
		image = Image.new('RGB', (self.width, self.height))
		image.putdata(self.as_rgb())
		image.save('height.png')


class WaterMap(Map2D):

	def __init__(self, width, height):
		super(WaterMap, self).__init__(width, height)

	def rain(self, count):
		for i in range(count):
			x = random.randint(0, self.width - 1)
			y = random.randint(0, self.height - 1)
			self.inc_pixel(x, y, 50.0)

	def flow_water(self, height_map):
		new_list = list(self.map_list)
		for i, water in enumerate(self.map_list):
			if water == 0.0:
				continue
			diffs = []
			for j in self.surrounding_indeces(i):
				diff = (height_map.map_list[i] + self.map_list[i] -
					(height_map.map_list[j] + self.map_list[j]))
				if diff <= 0:
					diff = 0
				diffs.append(diff)
			diff_sum = sum(diffs)
			flow = []
			if diff_sum > 0:
				flow = [diff / diff_sum for diff in diffs]
			else:
				flow = [0 for diff in diffs]
			new_list[i] -= diff_sum
			for k, j in enumerate(self.surrounding_indeces(i)):
				new_list[j] += flow[k]
		self.map_list = new_list

	def generate(self, height_map):
		for i in range(20):
			print(i)
			self.rain(1000)
			self.flow_water(height_map)

	def water_to_rgb(self, water):
		return (int(water * 255), 0, int(water * 255))

	def as_rgb(self):
		return [self.water_to_rgb(w) for w in self.map_list]

	def render(self):
		image = Image.new('RGB', (self.width, self.height))
		image.putdata(self.as_rgb())
		image.save('water.png')


class World(object):

	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.height_map = HeightMap(width, height)
		self.water_map = WaterMap(width, height)

	def generate(self, seed=None):
		random.seed(seed)
		self.height_map.generate()
		self.water_map.generate(self.height_map)

def main():
	world = World(1000, 1000)
	world.generate()
	print('height')
	world.height_map.render()
	print('water')
	world.water_map.render()
	#world.height_map.plot_histogram()

if __name__ == '__main__':
	main()
