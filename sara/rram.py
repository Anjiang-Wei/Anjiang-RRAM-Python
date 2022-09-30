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
            "Cth": 0.318 * units.fJ / units.K,
            "Vth":1.1 * units.V
        }

    @staticmethod
    def apply_process_variation(parameters):
        '''
        From the paper: "The 3σ/μ (3 standard deviation/mean) of I0, γ0, and v0 are 30%, 10%, and 10%, respectively"
        '''
        I0_nom = parameters["I0"]
        gamma0_nom = parameters["gamma0"]
        v0_nom = parameters["v0"]
        Vth_nom = parameters["Vth"]
        new_pars = dict(parameters)
        new_pars["I0"] = np.random.normal(I0_nom, I0_nom*(0.3)/3)
        new_pars["gamma0"] = np.random.normal(gamma0_nom, gamma0_nom*(0.1)/3)
        new_pars["v0"] = np.random.normal(gamma0_nom, v0_nom*(0.1)/3)
        new_pars["Vth"] = np.random.normal(Vth_nom, 0.1*units.V)
        return new_pars


    @staticmethod
    def ddt_model(parameters,time,_g,T,V,Vtrans,rvs):

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
        #g = min(max(0,_g),L)
        g = min(max(gmin,_g),gmax)
        #physics constants
        k = 1.3806488e-23*units.J/units.K
        # Volt = J/coulombs
        # eV = 1.6e-19 Joules
        q = 1.602e-19*units.J/units.eV

        #electrons in a coulomb
        elecs = 6.24e18

        #expressions
        gamma = gamma0 - beta*(g/g1)**3.0

        q_kT = q/(k*T)
        one_kT = 1.0/(k*T)
        gamma_aLV = gamma*a0/L*float(V)

        I,R = RRAMMacroModel.cell_state(parameters,VTrans=Vtrans,V=V,g=g)
        # functions

        #dist = math.exp(gamma_aL*q_kT*V)
        #term1 = math.exp(-q_kT*Eag)
        #term2= math.exp(-q_kT*Ear)
        log_term1 = (gamma_aLV*one_kT - Eag*one_kT)*q
        log_term2 = (-gamma_aLV*one_kT - Ear*one_kT)*q

        stoch_dg_dt = rvs[0](time)*(gmax-gmin)*0.001
        dg_dt = -v0*(math.exp(log_term1) - math.exp(log_term2))
        dg_dt += stoch_dg_dt
        if(math.isnan(dg_dt)):
            print("dgdt=%e g=%e log1=%e log2=%e aLV=%e" % (dg_dt, g, log_term1, log_term2,gamma_aLV))
            raise Exception("dg/dt is NAN")

        stoch_dT_dt = rvs[1](time)*1*0.001
        dT_dt = abs(V * I)/Cth - (float(T)-float(T0))/tau_th
        dT_dt += stoch_dT_dt

        #print("dgdt=%e g=%e log1=%e log2=%e aLV=%e" % (dg_dt, g, log_term1, log_term2, gamma_aLV))
        #print("   I=%e V=%e Vtrans=%f R=%f" % (I,V,Vtrans,R))
        #print("dTdt=%e g=%e T=%e I=%e V=%e" % (dT_dt, g, T, I, V))
        if(math.isnan(dT_dt)):
            print("dTdt=%e T=%e I=%e V=%e" %(dT_dt, T, I, V))
            raise Exception("dT/dt is NAN")
        # everything is per seconds
        return dg_dt, dT_dt


    @staticmethod
    def cell_state(parameters, VTrans, V, g):
        I0 = parameters["I0"]
        g0 = parameters["g0"]
        gmin = parameters["g_min"]
        gmax = parameters["g_max"]
        V0 = parameters["V0"]
        Vth = parameters["Vth"]
        # compute compliance current from voltage applied across a transistor

        assert(VTrans >= 0)
        if VTrans < Vth:
            CC = 0.0
        else:
            # figure 6
            VHold = VTrans - Vth
            I1 = 25*units.uA*(math.exp(4*VHold) - 1)
            I2 = 80*units.uA*(math.exp(70*(VHold-0.2)))-0.83*units.uA
            CC = max(I1+I2,0.0)
            CC = 10*units.uA
        #print("compliance current: V=%e I=%e" % (VTrans,CC))

        gnew = min(max(gmin,g),gmax)
        t1 = math.exp(-gnew/g0)
        t2 = math.sinh(V/V0)
        Inom =I0*t1*t2
        I = max(min(Inom, CC), -CC)

        if I == 0.0:
            return 0.0,math.inf
        R = V/I
        return I,R

    def set_ambient_temperature(self,temp_C):
        self.parameters["T0"] = temp_C + 273.15

    @property
    def R(self):
        I,R = RRAMMacroModel.cell_state(self.parameters, VTrans=3.0, V=0.1,g=self.g)
        return R

    def I(self,bl,wl,sl):
        I,R = RRAMMacroModel.cell_state(self.parameters, VTrans=wl,V=(bl-sl), g=self.g)
        return I

    def generate_noise(self,nsigs,times,npts):

        ts = np.linspace(min(times),max(times)*1.2,int(npts*1.2))
        rvs = {}
        for i in range(nsigs):
            vs = list(map(lambda i: np.random.normal(0,1), ts))
            rvs[i] = scipy.interpolate.interp1d(ts,vs,bounds_error=False,fill_value=0.0)
        return rvs

    def simulate(self,times,vdiff_voltages, vwl_voltages):
        g = self.g
        T = self.T
        rvs = self.generate_noise(2,times,len(times)*5)

        def model_ddt(x,t,diff_voltfn,th_voltfn, rvs):
            g,T = x
            dg,dT = RRAMMacroModel.ddt_model(self.parameters,t,g,T,
                                             V=diff_voltfn(t),
                                             Vtrans=th_voltfn(t), rvs=rvs)
            return [dg,dT]

        diff_voltfn = scipy.interpolate.interp1d(times,vdiff_voltages,fill_value=0.0, bounds_error=False)
        th_voltfn = scipy.interpolate.interp1d(times,vwl_voltages,fill_value=0.0, bounds_error=False)
        x0 = [g,T]
        ys = scipy.integrate.odeint(model_ddt, x0, times,args=(diff_voltfn,th_voltfn,rvs,))

        #update value
        ylast = ys[-1]
        gnew,Tnew = ylast
        self.g = gnew
        self.T = Tnew

        return ys

class RRAMMemoryArray:


        def __init__(self, n, m,  variation=False, simulate_entire_array=False):
            self.n = n
            self.m = m
            self.cells = {}
            self.simulate_entire_array = simulate_entire_array

            for i in range(self.n):
                for j in range(self.m):
                    self.cells[(i, j)] = RRAMMacroModel(variation=variation)

        def wait_cell(self,i,j,time):
            times = np.linspace(0,time,1000)
            voltages = [0.0]*len(times)
            vwl_voltages = [0.0]*len(times)
            self.cells[(i,j)].simulate(times,voltages,vwl_voltages)

        def wait(self,time):
            times = np.linspace(0,time,1000)
            voltages = [0.0]*len(times)

            for i in range(self.n):
                for j in range(self.m):
                    self.cells[(i,j)].simulate(times,voltages)

        def wordline_bitline_sourceline(self, wl, bl, sl):
            V = bl - sl
            CC = wl

        def pulse(self,i,j,wl,sl,bl,time,wait=1*units.ns):
            def gen_pulse(t,val):
                if t > time + wait/2:
                    return 0.0
                elif t > wait/2:
                    return val
                else:
                    return 0.0


            total_time = time+wait
            npts = int(1000/(1*units.ns)*total_time)

            times = np.linspace(0,total_time,npts)

            sgn = -1.0 if bl < sl else 1.0
            assert(wl > 0)
            vdiff_voltages = list(map(lambda t: sgn*gen_pulse(t, val=abs(bl-sl)), times))
            vth_voltages = list(map(lambda t: gen_pulse(t, val=wl), times))

            cell = self.cells[(i,j)]
            cell.simulate(times,vdiff_voltages=vdiff_voltages, vwl_voltages=vth_voltages)



        def resistance(self, i, j):
            return self.cells[(i,j)].R

        def read(self,i,j,wl,bl,sl):
            return self.cells[(i,j)].I(bl=bl,sl=sl,wl=wl)


class RRAMWriteAlgorithm:



    RESET_VBL = 0.0*units.V
    RESET_VSL = 1.55*units.V
    RESET_VWL = 3.0*units.V
    RESET_PULSE_WIDTH = 9.5*units.ns

    #decrease resistance
    SET_VBL = 1.55*units.V
    SET_VSL = 0.0*units.V
    # should be ~0.1 volts above the nominal threshhold voltage.
    SET_VWL = 1.4*units.V
    SET_PULSE_WIDTH = 9.5*units.ns

    READ_VBL = 0.1*units.V
    READ_VSL=0*units.V
    READ_VWL = 3*units.V

    FINE_THRESH=10000

    def __init__(self,memory_array):
        self.memory = memory_array


    def read_current(self,i,j):
        I = self.memory.read(i,j,
                             wl=RRAMWriteAlgorithm.READ_VWL,
                             bl=RRAMWriteAlgorithm.READ_VBL,
                             sl=RRAMWriteAlgorithm.READ_VSL
                             )
        return I


    def read(self,i,j):
        I = self.read_current(i,j)
        if I == 0.0:
            return math.inf
        return (RRAMWriteAlgorithm.READ_VBL - RRAMWriteAlgorithm.READ_VSL)/I

    def RESET(self, i,j, fine=False):
        print("reset / increase resistance fine=%s" % fine)
        scf = 0.5 if fine else 1.0
        self.memory.pulse(i, j,
                          wl=RRAMWriteAlgorithm.RESET_VWL,
                          bl=RRAMWriteAlgorithm.RESET_VBL,
                          sl=RRAMWriteAlgorithm.RESET_VSL,
                          time=RRAMWriteAlgorithm.RESET_PULSE_WIDTH*scf,
                          wait=RRAMWriteAlgorithm.RESET_PULSE_WIDTH/2.0*scf)

    def SET(self, i,j, fine=False):
        print("set / decrease resistance fine=%s" % fine)
        scf = 0.5 if fine else 1.0
        self.memory.pulse(i, j,
                          wl=RRAMWriteAlgorithm.SET_VWL,
                          bl=RRAMWriteAlgorithm.SET_VBL,
                          sl=RRAMWriteAlgorithm.SET_VSL,
                          time=RRAMWriteAlgorithm.SET_PULSE_WIDTH*scf,
                          wait=RRAMWriteAlgorithm.SET_PULSE_WIDTH/2.0*scf)

        pass


    def write(self,i,j,r,tol,max_cycles):
        resist = self.read(i,j)
        if (max_cycles) < 0:
            print("fail: resistance %f, target = %f +- %f" % (resist,r,tol))
            return False

        if resist <= r + tol and resist >= r-tol:
            print("success: resistance %f, target = %f +- %f" % (resist, r,tol))
            return True

        print("debug: resistance %f, target = %f +- %f" % (resist, r, tol))
        thresh = RRAMWriteAlgorithm.FINE_THRESH
        if resist < r - tol:
            #print("RESET: increase resistance!")
            self.RESET(i,j,fine=(abs(resist - (r - tol)) < thresh))

        elif resist > r + tol:
            #print("SET: decrease resistance!")
            self.SET(i,j,fine=(abs(resist - (r + tol)) < thresh))
        else:
            raise NotImplementedError

        self.write(i,j,r=r,tol=tol,max_cycles=max_cycles-1)


def generate_ivcurve():
    mem = RRAMMemoryArray(10,10)
    wralgo = RRAMWriteAlgorithm(mem)
    #TODO
    i,j = 0,0
    vs = []
    Is = []
    wralgo.write(i,j,300*units.kOhms, 10000,25)


    plt.clf()
    plt.scatter(vs,Is)
    plt.savefig("IV.png")


    return
    #r1 = 300*units.kOhms
    #wralgo.write(i,j,300*units.kOhms, 1000, 25)



def generate_resistance_distribution(r,tol):
    wralgo = RRAMWriteAlgorithm(RRAMMemoryArray(10,10,variation=True))
    trials = 50
    i,j = 0,0
    niters = 50
    time_keys = ["0ms","10ms","100ms","1s","10s","100s"]
    rs = dict(map(lambda t: (str(t),[]), time_keys))
    for t in range(niters):
        print("trial %d started "% t)
        total_wait = 0.0
        if not wralgo.write(i,j,r=r,tol=tol,max_cycles=niters):
            continue

        read_r = wralgo.read(i,j)
        rs["0ms"].append(read_r)

        print("wait 10ms")
        wralgo.memory.wait_cell(i,j,10*units.ms)
        read_r = wralgo.read(i,j)
        rs["10ms"].append(read_r)
        total_wait += 10*units.ms

        print("wait 100ms")
        wralgo.memory.wait_cell(i,j,100*units.ms - total_wait)
        read_r = wralgo.read(i,j)
        rs["100ms"].append(read_r)
        total_wait += 100*units.ms

        print("wait 1s")
        wralgo.memory.wait_cell(i,j,1*units.s - total_wait)
        read_r = wralgo.read(i,j)
        rs["1s"].append(read_r)
        total_wait += 1*units.s


        print("wait 10s")
        wralgo.memory.wait_cell(i,j,10*units.s - total_wait)
        read_r = wralgo.read(i,j)
        rs["10s"].append(read_r)
        total_wait += 10*units.s

        print("wait 100s")
        wralgo.memory.wait_cell(i,j,100*units.s - total_wait)
        read_r = wralgo.read(i,j)
        rs["100s"].append(read_r)
        total_wait += 100*units.s


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
    ys = [4.0] * npts
    plt.scatter(rs["100s"], ys, alpha=0.5, label="100s")

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

def R_distr(r,tol=100,relax_time=1,trials=100, write_max_cycle=50):
    wralgo = RRAMWriteAlgorithm(RRAMMemoryArray(10,10,variation=True))
    i,j = 0,0
    niters = trials
    time_keys = ["1s"]
    rs = dict(map(lambda t: (str(t),[]), time_keys))
    for t in range(niters):
        # print("trial %d started "% t)
        total_wait = 0.0
        if not wralgo.write(i,j,r=r,tol=tol,max_cycles=write_max_cycle):
            continue
        wralgo.memory.wait_cell(i,j,1*units.s - total_wait)
        read_r = wralgo.read(i,j)
        rs["1s"].append(read_r)
        total_wait += 1*units.s
    return rs["1s"]

#test_write()
#generate_ivcurve()
#generate_ivcurve()
# generate_resistance_distribution(100000, 10000)
if __name__ == "__main__":
    print(R_distr(10000,500))
