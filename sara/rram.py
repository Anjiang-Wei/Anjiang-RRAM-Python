import numpy as np
import math
import scipy.interpolate
import scipy.integrate

import units

#
class RRAMMacroModel(mem.CellMacroModel):

    def __init__(self):
        # estimate IV curves
        self.parameters = RRAMMacroModel.nominal_params()
        #RRAMMacroModel.apply_process_variation(self.parameters)

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
        raise NotImplementedError

    @staticmethod
    def ddt_model(parameters,_g,T,V):

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
        dg_dt = -v0*(math.exp(log_term1) - math.exp(log_term2))
        dT_dt = abs(V * I)/Cth - (float(T)-float(T0))/tau_th
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

    def simulate(self,times,voltages):
        g = self.g
        T = self.T

        def model_ddt(x,t,voltfn):
            g,T = x
            dg,dT = RRAMMacroModel.ddt_model(self.parameters, g,T,voltfn(t))
            return [dg,dT]

        voltfn = scipy.interpolate.interp1d(times,voltages,fill_value=0.0, bounds_error=False)
        x0 = [g,T]
        ys = scipy.integrate.odeint(model_ddt, x0, times,args=(voltfn,))

        #update value
        ylast = ys[-1]
        gnew,Tnew = ylast
        self.g = gnew
        self.T = Tnew

        return ys

class RRAMMemoryArray:


        def __init__(self, n, m):
            self.n = n
            self.m = m
            self.cells = {}


            for i in range(self.n):
                for j in range(self.m):
                    self.cells[(i, j)] = RRAMMacroModel()


        def pulse(self,i,j,length,amplitude,duty_cycle):
            cell = self.cells[(i,j)]
            total = length/duty_cycle
            delay = (total-length)/2
            times = np.linspace(0,total,1000)
            voltages = list(map(lambda t: amplitude if t >= delay and t <= delay+length else 0.0, times))
            cell.simulate(times,voltages)
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
        if (max_cycles) < 0:
            return

        resist = self.read(i,j)
        print("%d,%d : %s (%s)" % (i,j,resist, self.memory.resistance(i,j)))
        if resist <= r + tol and resist >= r-tol:
            return

        elif resist < r-tol:
            self.memory.pulse(i,j,amplitude=RRAMWriteAlgorithm.WRITE_NEG_VOLTAGE,
                              length=RRAMWriteAlgorithm.WRITE_NEG_PULSE_WIDTH,
                              duty_cycle=RRAMWriteAlgorithm.WRITE_DUTY_CYCLE)
            print("write neg")
        else:
            self.memory.pulse(i,j,amplitude=RRAMWriteAlgorithm.WRITE_POS_VOLTAGE,
                              length=RRAMWriteAlgorithm.WRITE_POS_PULSE_WIDTH,
                              duty_cycle=RRAMWriteAlgorithm.WRITE_DUTY_CYCLE)
            print("write pos")

        self.write(i,j,r,tol,max_cycles-1)


def generate_ivcurve():
    mem = RRAMMemoryArray(10,10)
    wralgo = RRAMWriteAlgorithm(mem)
    #TODO
    i,j = 0,0
    r1 = 300*units.kOhms
    wralgo.write(i,j,300*units.kOhms, 1000, 25)


    #TODO
    r2 = 30*units.kOhms


def test_write():
    wralgo = RRAMWriteAlgorithm(RRAMMemoryArray(10,10))

    i,j = 0,0
    print("resistance value: %d ohms" % wralgo.memory.resistance(i,j))

    wralgo.write(i,j,10000,1000,25)
    print("resistance value: %d ohms" % wralgo.memory.resistance(i,j))

    wralgo.write(i,j,1000,100,25)
    print("resistance value: %d ohms" % wralgo.memory.resistance(i,j))

test_write()
generate_ivcurve()
