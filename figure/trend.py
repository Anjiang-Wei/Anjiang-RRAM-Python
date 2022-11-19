   
import matplotlib.pyplot as plt
import numpy as np

our_res = \
{4: 0.005376344086021501,
 5: 0.027732279760340383,
 6: 0.03679837591602295,
 7: 0.050520354710731415,
 8: 0.07136630250665339}
sba_res = \
{4: 0.01853476639613949,
 5: 0.04037113402061856,
 6: 0.03758010209623112,
 7: 0.08822923108637395,
 8: 0.11275252525252524}
sba_our_search = \
{4: 0.03063854407742478,
 5: 0.034060606060606055,
 6: 0.051132146600509486,
 7: 0.0716536667264551,
 8: 0.08731699201419699}
sba_our_search_mean = \
{4: 0.010101010101010083,
 5: 0.028634546602146017,
 6: 0.048749999999999995,
 7: 0.061630213093291704,
 8: 0.10434661891471461}



x = [i for i in range(4, 9)]

our = [our_res[k] for k in x]
sba = [sba_res[k] for k in x]
sba_better_search = [sba_our_search[k] for k in x]
sba_better_search_mean = [sba_our_search_mean[k] for k in x]

plt.figure(figsize=[15, 8], dpi=400)

plt.plot(x, our, "-x", color ='lightgreen', linewidth=3.0, label="dala")
plt.plot(x, sba, "-o", color = 'chocolate', linewidth=3.0, label="sba")
plt.plot(x, sba_better_search, "-.", color = 'gold', linewidth=3.0, label="dala-sigma")
plt.plot(x, sba_better_search_mean, ":", color = 'skyblue', linewidth=3.0, label="dala-norm")

plt.xlabel('Number of Levels', fontsize=25)
plt.ylabel('Level Drift Probability', fontsize=25)

plt.rcParams.update({'font.size': 25})

# parameters = {'axes.labelsize': 20,
#           'axes.titlesize': 20}
# plt.rcParams.update(parameters)
plt.xticks(np.arange(4, 9), [str(i) for i in x], fontsize=20)
plt.yticks(fontsize=20)


plt.legend()

# plt.show()
plt.savefig('trend_compare.png', bbox_inches='tight')

# todo: bar plot
