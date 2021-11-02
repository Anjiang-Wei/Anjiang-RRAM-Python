from scheme.level import Level
from models.write import WriteModel
from models.relax import RelaxModel

def non_overlapping_levels(levels):
    raise NotImplemented


def level_inference(Rmin, Rmax, Wmin, Wmax, Nctr, Nrad, T, BER):
    '''
    Rmin, Rmax: set by hardware constraints
    Wmin, Wmax: write width
    Nctr: how many write center values to try in [Rmin, Rmax]
    Nrad: how many write width values to try in [Wmin, Wmax]
    T: time for relaxation
    BER: bit error rate specification
    '''
    levels = []
    for Wctr in range(Rmin, Rmax, (Rmax-Rmin)/Nctr):
        for Wrad in range(Wmin, Wmax, (Wmax-Wmin)/Nrad):
            # run monte carlo simulation based on measurement data
            Sim_Write_N = 1000
            Read_Write_N = 1000
            WriteDistr = WriteModel(Wctr-Wrad, Wctr+Wrad)
            RelaxDistr = RelaxModel(WriteDistr, T)
            Rlow, Rhigh = getReadRange(RelaxDistr, BER)
            levels.append(Level(Rlow, Rhigh, Wctr-Wrad, Wctr+Wrad, prob=BER))
    return non_overlapping_levels(levels)
