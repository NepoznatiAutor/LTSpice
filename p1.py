##!/usr/bin/python3
import matplotlib.pyplot as plt
import numpy as np
import ltspice
tau = np.pi*2


def set_parameters():
    # simulation parameters are given as a dictionary
    # some parameters depend on other parameters, so I had to feed them in separately
    # looks ugly but works
    parameters = dict(
        fo      = 1.60e6,
        fs      = 2.00e6,
        dt      = 20e-9,
        Zo      = 10,
        Vin     = 250,
        Vout    = 24,
        n       = 9,
        Vgp     = 10,
        Vgn     = 0,
        Rg      = 5,
        Rgoff   = 1,
        Rshort  = 1e-6,
    )
    parameters['RLs']   = 0.01 + 0.01 * (parameters['Zo']*np.sqrt(parameters['fs']/parameters['fo']))
    parameters['Ztx']   = parameters['Zo'] * 1000
    parameters['Ltx1']  = parameters['Ztx'] / (tau * parameters['fo'])
    parameters['Ltx2']  = parameters['Ltx1'] / parameters['n']**2
    if 1 == 0:
        parameters['Vin'] = 400
        parameters['dt']  = 30e-9
        parameters['fs']  = 5e6
    return parameters


def main():

    spice_executable    = r"~/.wine/drive_c/Program\ Files/LTC/LTspiceXVII/XVIIx64.exe"
    simulation_file     = "bla.asc"
    include_file        = "bla.txt"

    parameters = set_parameters()
    
    # here the simulation is invoked - everything thankfully fits in neat class method calls
    lts = ltspice.LTSpiceOperator(spice_executable, simulation_file, include_file)
    lts.write_parameters_to_include_file(parameters)
    simulation_successful = lts.run_simulation()

    if simulation_successful == 0:
        X = lts.read_waveforms()
        # todo: create a measurement dictionary maybe?
        if 1 == 1:
            VCpp        = np.round(float(lts.read_measurement('vcpp')), decimals=1)
            Pin         = np.round(float(lts.read_measurement('pin')),  decimals=1)
            Pout        = np.round(float(lts.read_measurement('pout')), decimals=1)
            Ploss_sw    = np.round(float(lts.read_measurement('psw')),  decimals=2)
            Ploss_ind   = np.round(float(lts.read_measurement('pind')), decimals=2)
            eff         = np.round(Pout/Pin*100,                        decimals=2)

            print('VCpp       =', VCpp,      'V')
            print('Pin        =', Pin,       'W')
            print('Pout       =', Pout,      'W')
            print('Ploss_sw   =', Ploss_sw,  'W')
            print('Ploss_ind  =', Ploss_ind, 'W')
            print('efficiency =', eff,       '%')

        # identification of waveforms, which one is which
        # I have to make this a little easier to handle
        t       = X[:,0]*parameters['fs']
        Vi      = X[:,lts.find_variable('V(i+)')]-X[:,lts.find_variable('V(i-)')]
        Vr      = X[:,lts.find_variable('V(o+)')]-X[:,lts.find_variable('V(o-)')]
        Vg1     = X[:,lts.find_variable('V(g1)')]-X[:,lts.find_variable('V(s1)')]
        Vg2     = X[:,lts.find_variable('V(g2)')]-X[:,lts.find_variable('V(s2)')]
        Iin     = X[:,lts.find_variable('I(L1)')]
        Isw     = X[:,lts.find_variable('Id(M1)')]
        Id      = X[:,lts.find_variable('I(Dr1)')]
    
    if simulation_successful == 0:
        # plotting, dark_background because I like that, f- off
        if 1 == 1:
            plt.style.use('dark_background')
            plt.figure(1)
            plt.subplot(4, 2, 1), plt.plot(t, Vg1,  color='red'), plt.grid('on', linestyle='--', color='grey')
            plt.subplot(4, 2, 3), plt.plot(t, Vg2,  color='red'), plt.grid('on', linestyle='--', color='grey')
            plt.subplot(4, 2, 5), plt.plot(t, Vi,   color='red'), plt.grid('on', linestyle='--', color='grey')
            plt.subplot(4, 2, 7), plt.plot(t, Vr,   color='red'), plt.grid('on', linestyle='--', color='grey')
            plt.subplot(4, 2, 2), plt.plot(t, Iin,  color='red'), plt.grid('on', linestyle='--', color='grey')
            plt.subplot(4, 2, 4), plt.plot(t, Isw,  color='red'), plt.grid('on', linestyle='--', color='grey')
            plt.subplot(4, 2, 6), plt.plot(t, Id,   color='red'), plt.grid('on', linestyle='--', color='grey')
            plt.show()

        return 0
    else:
        return -1


if __name__ == '__main__':
    main()
             