#! /usr/bin/python
import sys
sys.path += ['../src','src']
import pyschedule

# get input size
n = 15

S = pyschedule.Scenario('n_queens_type_scheduling',horizon=n)
R = { i : S.Resource('R_%i'%i) for i in range(n) } #resources
T = { (i,j) : S.Task('T_%i_%i'%(i,j)) for i in range(n) for j in range(n) } #tasks

# precedence constrains
S += [ T[i,j-1] < T[i,j] for i in range(n) for j in range(1,n) ]

# resource assignment modulo n
for j in range(n):
    for i in range(n):
        T[(i+j) % n,j] += R[i]

if pyschedule.solvers.mip.solve(S,msg=False,kind='CBC'):
    import getopt
    opts, _ = getopt.getopt(sys.argv[1:], 't:', ['test'])
    if ('--test','') in opts:
        print('test passed')
    else:
        pyschedule.plotters.matplotlib.plot(S,color_prec_groups=False)
else:
    print('no solution found')
