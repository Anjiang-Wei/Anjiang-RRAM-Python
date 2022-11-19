   
import matplotlib.pyplot as plt
import numpy as np

our_res = {4: 0.005555555555555556,
    5: 0.02643171806167401,
    6: 0.036020583190394515,
    7: 0.050381679389312976,
    8: 0.0624048706240487
}

# Worst error:
# {4: 0.024038461538461564,
# 5: 0.0794117647058824,
# 6: 0.08970588235294119,
# 7: 0.12637362637362637,
# 8: 0.21701388888888884}

sba_res = {4: 0.018229166666666668,
    5: 0.04024144869215292,
    6: 0.03741496598639456,
    7: 0.08759124087591241,
    8: 0.11253196930946291
}
# Worst error:
# {4: 0.05718085106382975,
# 5: 0.08499999999999996,
# 6: 0.09343434343434343,
# 7: 0.1515151515151515, 
# 8: 0.25631313131313127}

# SBA (only model variance) with our searching algorithm
sba_our_search = {4: 0.030690537084398978,
    5: 0.03406813627254509,
    6: 0.05123674911660778,
    7: 0.07163742690058479,
    8: 0.08740359897172237
}
# Worst error:
# {4: 0.08545918367346939,
# 5: 0.06000000000000005,
# 6: 0.11855670103092786,
# 7: 0.13888888888888884,
# 8: 0.20280612244897955}


# sba(model both mean+sigma) + our searching algorithm
sba_our_search_mean={4: 0.01015228426395939,
    5: 0.029535864978902954,
    6: 0.04655172413793104,
    7: 0.061746987951807226,
    8: 0.10353866317169069
}
# Worst error:
# {4: 0.03409090909090906,
# 5: 0.061224489795918324,
# 6: 0.08906250000000004,
# 7: 0.18170103092783507,
# 8: 0.20876288659793818}


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
Error ratio compared to SBA: [0.30476190476190473, 0.6568281938325992, 0.9627319507250898, 0.5751908396946565, 0.5545523730455237]
Reduction in error ratio w.r.t. SBA: [69.52380952380952, 34.31718061674008, 3.7268049274910244, 42.48091603053435, 44.54476269544762]
Average Reduction in error ratio 38.91869475880452
'''
 
# Set position of bar on X axis
br1 = np.arange(len(dala))
br2 = [x + barWidth for x in br1]
br3 = [x + barWidth for x in br2]

plt.figure(dpi=90)
 
# Make the plot
plt.bar(br1, dala, # color ='r',
        width = barWidth,
        edgecolor ='grey', label ='dala')
plt.bar(br2, dala_sig, #color ='g',
        hatch='/', width = barWidth,
        edgecolor ='grey', label ='dala-sigma')
plt.bar(br3, dala_norm, #color ='b',
        hatch='-', width = barWidth,
        edgecolor ='grey', label ='dala-norm')
 
# Adding Xticks
plt.xlabel('Number of Levels', fontsize=25)
plt.ylabel('Relative Level Drift Error w.r.t. SBA', fontsize=25)
plt.xticks([r + barWidth for r in range(len(dala))], [str(i) for i in range(4, 9)], fontsize=20)
plt.yticks(fontsize=20)

plt.rcParams.update({'font.size': 25})

plt.axhline(1.0, linestyle="--", linewidth=4, color='b')
plt.text(-0.3, 1.03, "sba", size=25) #, bbox=dict(alpha=0.2))

plt.legend()
plt.show()

# write 1s in experiment setup
# 3) ping Sara
# 4) compute BER, confusion matrix, machine learning example
# 5) Akash's distribution normality test
