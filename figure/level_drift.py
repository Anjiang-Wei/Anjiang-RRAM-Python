import matplotlib.pyplot as plt

our_res =  {4: 0.002,
 5:  0.004,
 6: 0.005,
 7: 0.011428571428571429,
 8: 0.0175,
 9: 0.01888888888888889,
 10: 0.05,
 11: 0.04181818181818182,
 12: 0.06583333333333333,
 13: 0.07307692307692308,
 14: 0.08142857142857143,
 15: 0.10133333333333333,
 16: 0.121875}

sba_res = {4: 0.0925,
 5: 0.1,
 6: 0.09,
 7: 0.08857142857142856,
 8: 0.1111111111111111,
 9: 0.1388888888888889,
 10: 0.12,
 11: 0.10727272727272727,
 12: 0.13333333333333333,
 13: 0.16076923076923078,
 14: 0.14857142857142858,
 15: 0.18,
 16: 0.184375}



x = [i for i in range(4, 17)]

our = [our_res[k] for k in x]
sba = [sba_res[k] for k in x]


plt.plot(x, our, "-x", linewidth=3.0, label="QAlloc")
plt.plot(x, sba, "-o", linewidth=3.0, label="sba")

plt.xlabel('Number of Levels', fontsize=20)
plt.ylabel('Level Drift Probability', fontsize=20)

plt.rcParams.update({'font.size': 20})

# parameters = {'axes.labelsize': 20,
#           'axes.titlesize': 20}
# plt.rcParams.update(parameters)
plt.xticks(fontsize=15)
plt.yticks(fontsize=15)


plt.legend()
plt.show()
