from . import drift_model
class RelaxModel(object):
    def __init__(self):
        pass

    def data_init():
        print(f"Relax data init from conf{drift_model.model_char}")
        drift_model.load_param()
        print("Relax data init finished")

    def distr(WriteDistr, T, N=-1):
        res = []
        for v in WriteDistr:
            res += drift_model.get_distribution(v, T, N)
        return res
