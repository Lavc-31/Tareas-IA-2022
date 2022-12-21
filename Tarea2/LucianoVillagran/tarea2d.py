#!/usr/bin/env python

from ukf import UKF
import csv
import numpy as np
import math
import matplotlib.pyplot as plt

def iterate_x(x_in, timestep, inputs):
    '''this function is based on the x_dot and can be nonlinear as needed'''
    ret = np.zeros(len(x_in))
    ret[0] = x_in[0] + timestep * x_in[3] * math.cos(x_in[2])
    ret[1] = x_in[1] + timestep * x_in[3] * math.sin(x_in[2])
    ret[2] = x_in[2] + timestep * x_in[4]
    ret[3] = x_in[3] + timestep * x_in[5]
    ret[4] = x_in[4]
    ret[5] = x_in[5]
    return ret


def main():
    np.set_printoptions(precision=3)

    # Process Noise
    q = np.eye(6)
    q[0][0] = 0.0002
    q[1][1] = 0.0002
    q[2][2] = 0.0008
    q[3][3] = 0.005
    q[4][4] = 0.005
    q[5][5] = 0.005

    # create measurement noise covariance matrices
    r_imu = np.zeros([2, 2])
    r_imu[0][0] = 0.02
    r_imu[1][1] = 0.06

    r_compass = np.zeros([1, 1])
    r_compass[0][0] = 0.04

    r_encoder = np.zeros([1, 1])
    r_encoder[0][0] = 0.002

    # pass all the parameters into the UKF!
    # number of state variables, process noise, initial state, initial covariance, three tuning parameters, and the iterate function
    state_estimator = UKF(6, q, np.zeros(6), 0.0002*np.eye(6), 0.04, 0.0, 2.0, iterate_x)

    with open('datos.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)

        t = np.linspace(1, 6, 6)
        last_time = 0
        # read data
        for row in reader:
            row = [float(x) for x in row]

            cur_time = row[0]
            d_time = cur_time - last_time
            real_state = np.array([row[i] for i in [5, 6, 4, 3, 2, 1]])

            # create an array for the data from each sensor
            compass_hdg = row[9]
            compass_data = np.array([2*compass_hdg])

            encoder_vel = row[10]
            encoder_data = np.array([2*encoder_vel])

            imu_accel = row[7]
            imu_yaw_rate = row[8]
            imu_data = np.array([2*imu_yaw_rate, 2*imu_accel])

            last_time = cur_time

            # prediction is pretty simple
            state_estimator.predict(d_time)

            # updating isn't bad either
            # remember that the updated states should be zero-indexed
            # the states should also be in the order of the noise and data matrices
            state_estimator.update([4, 5], imu_data, r_imu)
            state_estimator.update([2], compass_data, r_compass)
            state_estimator.update([3], encoder_vel, r_encoder)

            print ("--------------------------------------------------------")
            print ("Real state: ", real_state)
            print ("Estimated state: ", state_estimator.get_state())
            print ("Difference: ", real_state - state_estimator.get_state())

            plt.figure(1)
            plt.plot(t,real_state)
            plt.xlabel("Factores de estado")
            plt.ylabel("Valores de cada factor")
            plt.title('48 Trayectorias reales, cambios en el ruido del modelo')
            plt.show()
            plt.savefig("real-d.png")
            
            plt.figure(2)
            plt.plot(t,state_estimator.get_state())
            plt.xlabel("Factores de estado")
            plt.ylabel("Valores de cada factor")
            plt.title('48 Trayectorias estimadas, cambios en el ruido del modelo')
            plt.show()
            plt.savefig("estimado-d.png")

if __name__ == "__main__":
    main()