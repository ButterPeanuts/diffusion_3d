import sys, csv
import pprint
import numpy as np
import math

prefix = "Dispacement"
suffix = ".txt"
sweaped_file = "sweaped.csv"
heatcap_file = "Si_heatcap_100.txt"
conductivitycurve_file = "conductivity.csv"

#一つのdirectoryに対し, sweapを書き出す
def printsweap(directory):
	import os, csv
	
	filenames = os.listdir(directory)
	
	sweaplist = []
	for i in filenames:
		# print(i.removeprefix(prefix), i)
		if (i.removeprefix(prefix) != i):
			sweaplist.append([i, float((i.removeprefix(prefix)).removesuffix(suffix))])
	
	# print(sweaplist)
	sweaplist.sort(key=lambda x: x[1])
	with open(directory + "\sweap.csv", "w", newline="") as file:
		writer = csv.writer(file)
		writer.writerows(sweaplist)

#directoryのリストそれぞれに対しprintsweapする
def printsweaps_pwd(directories):
	for i in directories:
		printsweap(i)

#sweapedからdirectoryのリストを拾ってくる
def sweaped_directories(sweaped):
	import csv
	directories = None
	with open(sweaped) as file:
		read = csv.reader(file)
		directories = [i[0] for i in read]
	return directories

#一つのdirectoryに対し, Result(diffusion, conductivity)をそれぞれ書き込み, 最遅時間のconductivityを返す
def printResult(directory, heatcap):
	import csv
	with open(directory + "\sweap.csv") as file:
		read = csv.reader(file)
		filenames = [[i[0], float(i[1])] for i in read]
	
	diffusion = []
	conductivity = []
	for filename in filenames:
		#シミュレーション時間計算
		tsim = 10 ** filename[1]
		
		#numpy処理
		position = np.loadtxt(directory + "\\" + filename[0], delimiter=",")
		var = np.var(position, axis = 0)
		d3d = np.average(var) / 2 / tsim
		
		#リストへ
		diffusion.append([tsim, d3d])
		conductivity.append([tsim, d3d * heatcap])
	
	with open(directory + "\diffusion.csv", "w", newline="") as file:
		writer = csv.writer(file)
		writer.writerows(diffusion)
	with open(directory + "\conductivity.csv", "w", newline="") as file:
		writer = csv.writer(file)
		writer.writerows(conductivity)
	
	return conductivity[-1][1]

#directoryのリストそれぞれに対しprintResultし, 最遅時間のconductivityのリストを返す
def printResults_pwd(directories):
	heatcap_list = [[], []]
	with open(heatcap_file) as file:
		read = csv.reader(file)
		for i in read:
			heatcap_list[0].append(float(i[0]))
			heatcap_list[1].append(float(i[1]))
	from scipy.interpolate import interp1d
	heatcap = interp1d(heatcap_list[0], heatcap_list[1])
	
	conductivity_curve = []
	for i in directories:
		conductivity_curve.append([i, printResult(i, heatcap(float(i)))])
	
	return conductivity_curve

#最遅時間conductivityのリスト(シミュ結果のリスト)を書き出す
def print_conductivity_curve(conductivity_curve):
	with open(conductivitycurve_file, "w", newline="") as file:
		writer = csv.writer(file)
		writer.writerows(conductivity_curve)

directories = sweaped_directories(sweaped_file)
printsweaps_pwd(directories)
print_conductivity_curve(printResults_pwd(directories))
