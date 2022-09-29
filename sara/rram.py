import numpy as np
import math
import scipy.interpolate
import scipy.integrate

import matplotlib.pyplot as plt
import units

#
class RRAMMacroModel:

    def __init__(self,variation=False):
        # estimate IV curves
        self.parameters = RRAMMacroModel.nominal_params()
        if variation:
            self.parameters = RRAMMacroModel.apply_process_variation(self.parameters)

        self.T = self.parameters["T0"]
        self.g = self.parameters["g0"]

    def cite(self):
        return ["Compact Modeling of RRAM Devices and Its Applications in 1T1R and 1S1R Array Design",
                "https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=7312469"]

    @staticmethod
    def nominal_params():
        return {
            "I0": 61.4 * units.uA,
            "V0": 0.43 * units.V,
            "beta": 1.25,
            "v0": 150 * units.m / units.s,
            "Ear": 1.500 * units.eV,
            "L": 5.0 * units.nm,
            "g_max": 1.7 * units.nm,
            "g_min": 0.1 * units.nm,
            "tau_th": 0.23 * units.ns,
            "g0": 0.275 * units.nm,
            "gamma0": 16.5,
            "g1": 1.0 * units.nm,
            "Eag": 1.501 * units.eV,
            "a0": 0.25 * units.nm,
            "T0": 298 * units.K,
            "Cth": 0.318 * units.fJ / units.K
        }

    @staticmethod
    def apply_process_variation(parameters):
        '''
        From the paper: "The 3σ/μ (3 standard deviation/mean) of I0, γ0, and v0 are 30%, 10%, and 10%, respectively"
        '''
        I0_nom = parameters["I0"]
        gamma0_nom = parameters["gamma0"]
        v0_nom = parameters["v0"]
        new_pars = dict(parameters)
        new_pars["I0"] = np.random.normal(I0_nom, I0_nom*(0.3)/3)
        new_pars["gamma0"] = np.random.normal(gamma0_nom, gamma0_nom*(0.1)/3)
        new_pars["v0"] = np.random.normal(gamma0_nom, v0_nom*(0.1)/3)
        return new_pars


    @staticmethod
    def ddt_model(parameters,time,_g,T,V,rvs):

        # g = gap distance, proportional resistance
        # dg_dt = gap growth speed
        # first term = oxygen vacancy generation
        # oxygen vacancy disssolution
        # Eag / Ear = activation energy for oxygen ions to migrate from one wall to another
        # If Eag != Ear then the filament will change even without a voltage application. (drift)
        # Eag is usually grater than Ear
        # L = oxide thickness
        # a0 = atom hopping distance
        # a0*qV/L energy barrier for raising / lowering neighboring oxygen vacancy
        # gamma dialectric property
        # v0, gamma0, beta, and g1 are fitting parameters
        # T0 = ambient temperature

        gamma0 = parameters["gamma0"]
        beta = parameters["beta"]
        g1 = parameters["g1"]
        v0 = parameters["v0"]
        Cth = parameters["Cth"]
        T0 = parameters["T0"]
        Eag = parameters["Eag"]
        Ear = parameters["Ear"]
        a0 = parameters["a0"]
        L = parameters["L"]
        gmin = parameters["g_min"]
        gmax = parameters["g_max"]

        tau_th = parameters["tau_th"]
        g = min(max(gmin,_g),gmax)
        #physics constants
        k = 1.3806488e-23*units.J/units.K
        q = 1.602e-19*units.J/units.eV
        #expressions
        gamma = gamma0 - beta*(g/g1)**3.0

        q_kT = q/(k*T)
        gamma_aL = gamma*a0/L*V

        I,R = RRAMMacroModel.cell_state(parameters,V,g)
        # functions

        #dist = math.exp(gamma_aL*q_kT*V)
        #term1 = math.exp(-q_kT*Eag)
        #term2= math.exp(-q_kT*Ear)
        log_term1 = (gamma_aL - Eag)*q_kT
        log_term2 = (-gamma_aL - Ear)*q_kT

        stoch_dg_dt = rvs[0](time)*(gmax-gmin)*0.0001
        dg_dt = -v0*(math.exp(log_term1) - math.exp(log_term2))
        dg_dt += stoch_dg_dt
        if(math.isnan(dg_dt)):
            print("log_term1: %f , exp(term) = %f" % (log_term1,math.exp(log_term1)))
            print("log_term2: %f , exp(term) = %f " % (log_term2, math.exp(log_term2)))
            subexpr = (math.exp(log_term1) - math.exp(log_term2))
            print("subexpr: %f" % subexpr)
            print("v0: %f" % v0)
            print("stoch: %f" % stoch_dg_dt)
            raise Exception("nan found")


        stoch_dT_dt = rvs[1](time)*(1)*0.01
        dT_dt = abs(V * I)/Cth - (float(T)-float(T0))/tau_th
        dT_dt += stoch_dT_dt

        assert(not math.isnan(dT_dt))
        # everything is per seconds
        return dg_dt, dT_dt


    @staticmethod
    def cell_state(parameters, V, g):
        I0 = parameters["I0"]
        g0 = parameters["g0"]
        V0 = parameters["V0"]
        t1 = math.exp(-g/g0)
        t2 = math.sinh(abs(V)/V0)
        I = I0*t1*t2
        if I == 0.0:
            return 0.0,math.inf
        R = V/I
        return I,R

    def set_ambient_temperature(self,temp_C):
        self.parameters["T0"] = temp_C + 273.15

    @property
    def R(self):
        I,R = RRAMMacroModel.cell_state(self.parameters, 0.3,self.g)
        return R

    def I(self,V):
        I,R = RRAMMacroModel.cell_state(self.parameters, V, self.g)
        return I

    def generate_noise(self,nsigs,times,npts):

        ts = np.linspace(min(times),max(times)*1.2,int(npts*1.2))
        rvs = {}
        for i in range(nsigs):
            vs = list(map(lambda i: np.random.normal(0,1), ts))
            rvs[i] = scipy.interpolate.interp1d(ts,vs,bounds_error=False,fill_value=0.0)
        return rvs

    def simulate(self,times,voltages):
        g = self.g
        T = self.T
        rvs = self.generate_noise(2,times,len(times)*5)

        def model_ddt(x,t,voltfn,rvs):
            g,T = x
            dg,dT = RRAMMacroModel.ddt_model(self.parameters,t,g,T,voltfn(t),rvs)
            return [dg,dT]

        voltfn = scipy.interpolate.interp1d(times,voltages,fill_value=0.0, bounds_error=False)
        x0 = [g,T]
        ys = scipy.integrate.odeint(model_ddt, x0, times,args=(voltfn,rvs,))

        #update value
        ylast = ys[-1]
        gnew,Tnew = ylast
        self.g = gnew
        self.T = Tnew

        return ys

class RRAMMemoryArray:


        def __init__(self, n, m, variation=False):
            self.n = n
            self.m = m
            self.cells = {}


            for i in range(self.n):
                for j in range(self.m):
                    self.cells[(i, j)] = RRAMMacroModel(variation=variation)

        def wait_cell(self,i,j,time):
            times = np.linspace(0,time,1000)
            voltages = [0.0]*len(times)
            self.cells[(i,j)].simulate(times,voltages)

        def wait(self,time):
            times = np.linspace(0,time,1000)
            voltages = [0.0]*len(times)

            for i in range(self.n):
                for j in range(self.m):
                    self.cells[(i,j)].simulate(times,voltages)

        def pulse(self,i,j,length,amplitude,duty_cycle,simulate_entire_array=False):
            cell = self.cells[(i,j)]
            total = length/duty_cycle
            delay = (total-length)/2
            times = np.linspace(0,total,1000)
            voltages = list(map(lambda t: amplitude if t >= delay and t <= delay+length else 0.0, times))
            cell.simulate(times,voltages)


            if simulate_entire_array:
                zero_voltages = [0.0]*len(times)
                for i2 in range(self.n):
                    for j2 in range(self.m):
                        if i != i2 and j != j2:
                            self.cells[(i2,j2)].simulate(times,zero_voltages)


            return cell.R


        def resistance(self, i, j):
            return self.cells[(i,j)].R

        def read(self,i,j,V):
            return self.cells[(i,j)].I(V)


class RRAMWriteAlgorithm:

    READ_VOLTAGE = 0.1*units.V
    WRITE_POS_VOLTAGE = 1.2*units.V
    WRITE_NEG_VOLTAGE = -1.0*units.V
    WRITE_DUTY_CYCLE=0.7
    WRITE_POS_PULSE_WIDTH = 10*units.ns
    WRITE_NEG_PULSE_WIDTH = 10*units.ns

    def __init__(self,memory_array):
        self.memory = memory_array


    def read(self,i,j):
        I = self.memory.read(i,j,
                                RRAMWriteAlgorithm.READ_VOLTAGE)
        return RRAMWriteAlgorithm.READ_VOLTAGE/I;

    def write(self,i,j,r,tol,max_cycles):
        resist = self.read(i,j)
        if (max_cycles) < 0:
            print("fail: resistance %f, target = %f +- %f" % (resist,r,tol))
            return False

        if resist <= r + tol and resist >= r-tol:
            print("success: resistance %f, target = %f +- %f" % (resist, r,tol))
            return True

        elif resist < r-tol:
            self.memory.pulse(i,j,amplitude=RRAMWriteAlgorithm.WRITE_NEG_VOLTAGE,
                              length=RRAMWriteAlgorithm.WRITE_NEG_PULSE_WIDTH,
                              duty_cycle=RRAMWriteAlgorithm.WRITE_DUTY_CYCLE)
        else:
            self.memory.pulse(i,j,amplitude=RRAMWriteAlgorithm.WRITE_POS_VOLTAGE,
                              length=RRAMWriteAlgorithm.WRITE_POS_PULSE_WIDTH,
                              duty_cycle=RRAMWriteAlgorithm.WRITE_DUTY_CYCLE)

        self.write(i,j,r=r,tol=tol,max_cycles=max_cycles-1)


def generate_ivcurve():
    mem = RRAMMemoryArray(10,10)
    wralgo = RRAMWriteAlgorithm(mem)
    #TODO
    i,j = 0,0
    r1 = 300*units.kOhms
    wralgo.write(i,j,300*units.kOhms, 1000, 25)


    #TODO
    r2 = 30*units.kOhms

def generate_resistance_distribution(r,tol):
    wralgo = RRAMWriteAlgorithm(RRAMMemoryArray(10,10))
    trials = 50
    i,j = 0,0
    niters = 50
    nbins = int(np.sqrt(niters))
    time_keys = ["0ms","10ms","100ms","1s","10s","300s"]
    rs = dict(map(lambda t: (str(t),[]), time_keys))
    for t in range(niters):
        print("trial %d started "% t)
        total_wait = 0.0
        if not wralgo.write(i,j,r=r,tol=tol,max_cycles=niters):
            continue

        read_r = wralgo.read(i,j)
        rs["0ms"].append(read_r)

        wralgo.memory.wait_cell(i,j,10*units.ms)
        read_r = wralgo.read(i,j)
        rs["10ms"].append(read_r)
        total_wait += 10*units.ms

        wralgo.memory.wait_cell(i,j,100*units.ms - total_wait)
        read_r = wralgo.read(i,j)
        rs["100ms"].append(read_r)
        total_wait += 100*units.ms

        wralgo.memory.wait_cell(i,j,1*units.s - total_wait)
        read_r = wralgo.read(i,j)
        rs["1s"].append(read_r)
        total_wait += 1*units.s


        wralgo.memory.wait_cell(i,j,10*units.s - total_wait)
        read_r = wralgo.read(i,j)
        rs["10s"].append(read_r)
        total_wait += 10*units.s

        wralgo.memory.wait_cell(i,j,300*units.s - total_wait)
        read_r = wralgo.read(i,j)
        rs["300s"].append(read_r)
        total_wait += 300*units.s


        print("trial %d completed "% t)

    plt.clf()
    npts = len(rs["10s"])
    ys = [0.0]*npts
    plt.scatter(rs["0ms"],ys,  alpha=0.5, label="0ms")
    ys = [1.0]*npts
    plt.scatter(rs["10ms"],ys,  alpha=0.5, label="10ms")
    ys = [2.0]*npts
    plt.scatter(rs["1s"],ys,  alpha=0.5, label="1s")
    ys = [3.0]*npts
    plt.scatter(rs["10s"],ys,  alpha=0.5, label="10s")
    plt.legend()
    plt.savefig("relaxation.png")

def test_write():
    wralgo = RRAMWriteAlgorithm(RRAMMemoryArray(10,10))

    i,j = 0,0
    print("resistance value: %d ohms" % wralgo.memory.resistance(i,j))

    wralgo.write(i,j,10000,1000,25)
    print("resistance value: %d ohms" % wralgo.memory.resistance(i,j))

    wralgo.write(i,j,1000,100,25)
    print("resistance value: %d ohms" % wralgo.memory.resistance(i,j))

#test_write()
#generate_ivcurve()

generate_resistance_distribution(10000, 1000)