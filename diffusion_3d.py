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
def printsweap(directory: str) -> None:
	"""directory中にある, 変位ファイルの情報を書き出す
		directoryのパスで示されるディレクトリーの中のファイルのうち,
		変位ファイル(後述の規則に従うファイル名を持つ)に当たるものを検知し, その情報をdirectory下の"sweap.csv"に書き出す
		
		変位ファイルはシミュレーター(https://github.com/ButterPeanuts/Research_mod2)の粒子位置を記録したもの
		1行に1つの粒子について記述, 1列目から順にx座標, y座標, z座標
		
		変位ファイルのファイル名は以下のような命名規則がある
		prefix + str(log_10(t_sim)) + suffix
		2024/02/13現在, prefixは"Dispacement", suffixは".txt"
		また, t_simはシミュレーション開始から変位ファイル記録までに(シミュレーション空間において)経過した時間(単位[s]を省略)
		
		prefixは"Displacement", suffixは".csv"とすべきであるが, ミスでこうなっている だれかなおして
		
		sweap.csvの構成は1行に1つの変位ファイルについて記述, 1列目はファイル名, 2列目はlog_10(t_sim)
		また, 出力時にlog_10(t_sim)の昇順(つまりt_simの昇順)にソートする
		
		Args:
			directory (str): 情報書き出し対象のディレクトリー
		
		Example:
			>>> # これは実際のファイル構成とは違う
			>>> import os
			>>> os.listdir("example")
				["Dispacement-8.txt", "Dispacement-7.txt"]
			>>> printsweap("example")
			>>> os.listdir("example")
				["Dispacement-8.txt", "Dispacement-7.txt", "sweap.csv"]
			>>> # sweap.csvの中身
			>>> # -8,Dispacement-8.txt
			>>> # -7,Dispacement-7.txt
		
		Note:
			[急募]いちいちsweap.csvに書き出す理由
		
		Todo:
			* flake8的には最初の行のosとcsvを両方インポートするのがNGらしいので分けたほうがいいかも
			* sweaplistをsweap.csvに書き出すのではなくそのままreturnすれば良いのでは感がある
	"""
	import os, csv
	
	#directoryの中にある全ファイルをListとして取得
	filenames = os.listdir(directory)  # type: List[str]
	
	#sweap.csvに書く内容を入れるList
	sweaplist = []  # type: List[str]
	
	for i in filenames:
		# prefixを消せない(ファイル名にprefixがついてない)なら飛ばす
		if (i.removeprefix(prefix) != i):
			# [i, iからprefixとsuffix消してfloatに変換したもの(log_10(t_sim))]をsweaplistに入れる
			sweaplist.append([i, float((i.removeprefix(prefix)).removesuffix(suffix))])
	
	# sweaplistをlog_10(t_sim)昇順にソート
	sweaplist.sort(key=lambda x: x[1])
	
	# directory内にsweap.csvを作ってsweaplistを書き出す
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
