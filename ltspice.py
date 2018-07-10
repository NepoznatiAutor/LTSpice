import sys
import subprocess
import numpy as np
import re

class LTSpiceOperator:
    #-------------------------------------------------------------------
    def __init__(self, spice_executable, simulation_file='', include_file=''):
        # print(sys.platform())
        self.spice_executable   = spice_executable
        self.simulation_file    = simulation_file
        self.include_file       = include_file
        self.waveform_file      = ''.join([self.simulation_file[0:-3], 'raw'])
        self.log_file           = ''.join([self.simulation_file[0:-3], 'log'])

    #-------------------------------------------------------------------
    def run_simulation(self):
        shell_line = ' '.join(["wine", self.spice_executable, "-ascii", "-b", "-run", self.simulation_file])
        print(shell_line)
        try:
            subprocess.run(' '.join(["wine", self.spice_executable, "-ascii", "-b", "-run", self.simulation_file]), shell=True)
            return 0
        except Exception as e:
            print(e)
            print('failure to run')
            return -1

    #-------------------------------------------------------------------
    def read_number_of_variables(self):
        number_of_variables = 0
        with open(self.waveform_file, 'r') as f:
            for line in f:
                if line.startswith('No. Variables:'):
                    number_of_variables = int(line[14:-1]) # hardcoded for now
                    break
        return number_of_variables

    #-------------------------------------------------------------------
    def read_number_of_points(self):
        number_of_points = 0
        with open(self.waveform_file, 'r') as f:
            for line in f:
                if line.startswith('No. Points:'):
                    number_of_points = int(line[12:-1])
                    break
        return number_of_points

    #-------------------------------------------------------------------
    def read_waveform_points(self, number_of_points, number_of_variables):
        X = np.zeros([number_of_points, number_of_variables])
        with open(self.waveform_file, 'r') as f:
            ok_to_count = False
            variable_counter = 0
            point_counter = 0
            for line in f:
                # print(ok_to_count)
                # print(variable_counter, number_of_variables)
                # print(point_counter, number_of_points)

                if ok_to_count:

                    # the stupid-est and direct-est way of removing prefix numbers and tabs
                    # for conversion to float, behold its glory
                    if variable_counter == 0:
                        if   point_counter >= 1e6:      i, j = [ 9, -1]
                        elif point_counter >= 1e5:      i, j = [ 8, -1]
                        elif point_counter >= 1e4:      i, j = [ 7, -1]
                        elif point_counter >= 1e3:      i, j = [ 6, -1]
                        elif point_counter >= 1e2:      i, j = [ 5, -1]
                        elif point_counter >= 1e1:      i, j = [ 4, -1]
                        else:                           i, j = [ 3, -1]
                    else:
                        i, j = [1, -1]

                    # populate X, the data matrix, actually array of arrays
                    X[point_counter, variable_counter] = line[i:j]
                    variable_counter += 1
                    if variable_counter >= number_of_variables:
                        variable_counter = 0
                        point_counter += 1
                        if point_counter >= number_of_points:
                            ok_to_count = False
                            break
                if line.startswith('Values:'):
                    ok_to_count = True
        return X

    #-------------------------------------------------------------------
    def read_waveforms(self):
        with open(self.waveform_file, 'r') as f:

            number_of_variables = self.read_number_of_variables()
            number_of_points    = self.read_number_of_points()

            X = self.read_waveform_points(number_of_points, number_of_variables)
        return X

    #-------------------------------------------------------------------
    def read_measurement(self, string: str):
        pattern = r'[-+]?[0-9]+\.?[0-9]+[eE]?[-+]?[0-9]+?'
        with open(self.log_file, 'r') as f:
            for line in f:
                if line.startswith(string):
                    match_object = re.search(pattern, line)
                    return match_object.group()
        return None

    #-------------------------------------------------------------------
    def find_variable(self, variable: str):
        pattern = r'[\t]?[0-9]+[\t]?'
        with open(self.waveform_file, 'r') as f:
            for line in f:
                if line.startswith('Values:'):
                    return None
                elif variable not in line:
                    continue
                else:
                    match_object = re.match(pattern, line)
                    return int(match_object.group())
                
    #-------------------------------------------------------------------
    def write_parameters_to_include_file(self, parameters):
        include_file_lines = []
        for key in parameters.keys():
            file_line = ' '.join(['.param', key, str(parameters[key])])
            include_file_lines.append(file_line)
        
        include_file_lines.append(' '.join(['.meas', 'pin',  'avg', '-V(in)*I(Vin)']))
        include_file_lines.append(' '.join(['.meas', 'pout', 'avg', 'abs(V(o+,o-))*I(Vout)']))
        include_file_lines.append(' '.join(['.meas', 'psw',  'avg', 'V(in,s1)*Id(M1)+V(drv1,s1)*Ig(M1) + \
                                                                     V(s1,s2)*Id(M2)+V(drv2,s2)*Ig(M2) + \
                                                                     V(in,s3)*Id(M3)+V(drv3,s3)*Ig(M3) + \
                                                                     V(s3,s4)*Id(M4)+V(drv4,s4)*Ig(M4)']))
        include_file_lines.append(' '.join(['.meas', 'pind', 'avg', 'V(i+,o+)*I(L1)']))
        include_file_lines.append(' '.join(['.meas', 'vcpp', 'pp', 'V(o-,i-)']))
        # for line in include_file_lines:
            # print(line)

        with open(self.include_file, 'w+') as f:
            f.write('\n'.join(include_file_lines))

        return 0

#-------------------------------------------------------------------
def main():
    return 0

if __name__ == '__main__':
    main()