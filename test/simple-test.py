from pyschedule import Scenario, solvers

# the planning horizon has 10 periods
S = Scenario('household',horizon=10)

# two resources: Alice and Bob
Alice, Bob = S.Resource('Alice'), S.Resource('Bob')

# three tasks: cook, wash, and clean
cook = S.Task('cook',length=1,delay_cost=1)
wash = S.Task('wash',length=2,delay_cost=1)
clean = S.Task('clean',length=3,delay_cost=2)

# every task can be done either by Alice or Bob
cook += Alice | Bob
wash += Alice | Bob
clean += Alice | Bob

#print("\n##############################")
#print("Compute and print a schedule using CBC")
#solvers.mip.solve(S,kind='CBC', msg=True)
#print(S.solution())

print("\n##############################")
print("Compute and print a schedule using GLPK")
solvers.mip.solve(S,kind='GLPK', msg=True)
print(S.solution())
