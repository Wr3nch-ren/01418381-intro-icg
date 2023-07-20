import numpy as np

P = np.array((1, 2, 0), dtype=np.float32)

Q = np.array((3, 4, 1), dtype=np.float32)

P-Q

Q-P

np.linalg.norm(P-Q)

np.linalg.norm(Q-P)

U = np.array((1, 0, 0), dtype=np.float32)

V = np.array((0, 1, 0), dtype=np.float32)

R = P-Q

S = 10 * U

T = R

print(" T  =", T)

T = T / np.linalg.norm(T)

print("|T| =", T)

print("U dot V =", np.dot(U, V))

print("U dot V =", U.dot(V))

from math import acos, pi

print("acos(U dot V) =", acos(U.dot(V)))

print("         pi/2 =", pi/2)

print("U x V =", np.cross(U, V))

print("V x U =", np.cross(V, U))