   
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


# set width of bar
barWidth = 0.25
# fig = plt.subplots(figsize =(12, 8))
 
# set height of bar
dala = [our_res[i] / sba_res[i] for i in range(4, 9)]
dala_sig = [sba_our_search[i] / sba_res[i] for i in range(4, 9)]
dala_norm = [sba_our_search_mean[i] / sba_res[i] for i in range(4, 9)]

print("Error ratio compared to SBA:", dala)
data_reduction_error_perc = [(sba_res[i] - our_res[i]) / sba_res[i] * 100 for i in range(4, 9)]
print("Reduction in error ratio w.r.t. SBA:", data_reduction_error_perc)
print("Average Reduction in error ratio", sum(data_reduction_error_perc) / len(data_reduction_error_perc))
'''
Error ratio compared to SBA: [0.29006807914996496, 0.6869333852791157, 0.979198401904114, 0.5726033661256029, 0.6329463783344847]
Reduction in error ratio w.r.t. SBA: [70.9931920850035, 31.306661472088432, 2.0801598095886042, 42.739663387439705, 36.70536216655152]
Average Reduction in error ratio 36.76500778413435
'''
 
# Set position of bar on X axis
br1 = np.arange(len(dala))
br2 = [x + barWidth for x in br1]
br3 = [x + barWidth for x in br2]

plt.figure(figsize=[15, 8], dpi=400)
 
# Make the plot
plt.bar(br1, dala, color ='lightgreen',
        width = barWidth, 
        edgecolor ='grey',
        label ='dala')
plt.bar(br2, dala_sig, color ='gold',
        hatch='/', width = barWidth,
        edgecolor ='grey',
        label ='dala-sigma')
plt.bar(br3, dala_norm, color ='skyblue',
        hatch='-', width = barWidth,
        edgecolor ='grey',
        label ='dala-norm')
 
# Adding Xticks
plt.xlabel('Number of Levels', fontsize=25)
plt.ylabel('Relative Level Drift Error w.r.t. SBA', fontsize=25)
plt.xticks([r + barWidth for r in range(len(dala))], [str(i) for i in range(4, 9)], fontsize=20)
plt.yticks(fontsize=20)

plt.rcParams.update({'font.size': 25})

plt.axhline(1.0, linestyle="--", linewidth=4, color='black')
plt.text(-0.3, 1.03, "sba", size=25) #, bbox=dict(alpha=0.2))

plt.legend()
# plt.show()
plt.savefig('bar_compare.png', bbox_inches='tight')

# write 1s in experiment setup
# 3) ping Sara
# 4) compute BER, confusion matrix, machine learning example
# 5) Akash's distribution normality test
