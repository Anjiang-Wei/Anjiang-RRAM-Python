from . import drift_model
class RelaxModel(object):
    def __init__(self):
        pass

    def data_init():
        print(f"Relax data init from conf{drift_model.model_char}")
        drift_model.load_param()
        print("Relax data init finished")
    
    def distr(WriteDistr, T, N):
        res = []
        for v in WriteDistr:
            for i in range(N):
                res.append(drift_model.drift(v, T))
        return res
