# secure multi-party computation, semi-honest case, distributed, v1
# naranker dulay, dept of computing, imperial college, october 2020
# tuck hong (tkh2017) and preet lalli (pl1516)

# Circuit below to evalute
CIRCUIT = 1

# Gate types
INP, ADD, MUL, DIV = (0,1,2,3)

# Define MPC Function as an addition/multiplication circuit. INPut gates 
# precede ADD/MUL gates. ADD/MUL gates are defined in evaluation order. 
# By convention the final wire is considerd the circuit's output wire.

if CIRCUIT == 1: 	# example in Smart
  # ___________________________________________________________________________
  # polynomial prime - further primes at bottom of file
  PRIME  = 101
  # degree of polynominal - T in slides
  DEGREE = 2

  PRIVATE_VALUES = {1:20, 2:40, 3:21, 4:31, 5:1, 6:71}

  def function(x):	# function being evaluated by parties
    return (x[1]*x[2] + x[3]*x[4] + x[5]*x[6]) % PRIME

  GATES = {
    1:  (INP, 7,1),
    2:  (INP, 7,2),
    3:  (INP, 8,1),
    4:  (INP, 8,2),
    5:  (INP, 9,1),
    6:  (INP, 9,2),
    7:  (MUL, 10,1),
    8:  (MUL, 10,2),
    9:  (MUL, 11,1),
    10: (ADD, 11,2),
    11: (ADD, 12,1),  	# (12,1) is circuit output wire
  }

elif CIRCUIT == 2:	# factorial tree for 2^n parties
  # ___________________________________________________________________________
  # polynomial prime - further primes at bottom of file
  PRIME = 100_003
  # PRIME = 1_000_000_007
  # PRIME = 35742549198872617291353508656626642567  # Large Bell prime

  # degree of polynominal - T in slides
  DEGREE = 2

  INPUTS = 2 ** 3
  PRIVATE_VALUES = {k: k for k in range(1, INPUTS+1)}

  def function(x):	# function being evaluated by parties
    product = 1
    for value in x.values(): product = (product * value) % PRIME
    return product

  GATES = {}

  def tree(next_gate, n_gates):
    global GATES
    if n_gates >= 1:
      kind = INP if next_gate == 1 else MUL
      output_gate = next_gate + n_gates
      last_gate = output_gate - 1
      for g in range(next_gate, output_gate, 2):
        GATES[g]   = (kind, output_gate, 1)
        if g < last_gate:
          GATES[g+1] = (kind, output_gate, 2)
        output_gate += 1
      tree(next_gate + n_gates, n_gates // 2)

  tree(1, INPUTS)

# ___________________________________________________________________________
elif CIRCUIT == 3:	# add your circuit(s) here

  # polynomial prime - further primes at bottom of file
  PRIME  = 101
  # degree of polynominal - T in slides
  DEGREE = 2

  PRIVATE_VALUES = {1:4, 2:5, 3:3, 4:2, 5:7, 6:3}

  def function(x):	# function being evaluated by parties
    # these functions are copied from modprime.py
    # to prevent circular import issue
    def inv(a):
      return pow(a, PRIME-2, PRIME)

    def mul(a, b):
      return (a * b) % PRIME
  
    def div(a, b):
      return mul(a, inv(b))

    return (div((x[1] + x[2] + x[3] + x[4] + x[5] + x[6]), 6)) % PRIME

  GATES = {
    1:  (INP, 7, 1),
    2:  (INP, 7, 2),
    3:  (INP, 8, 2),
    4:  (INP, 9, 2),
    5:  (INP, 10, 2),
    6:  (INP, 11, 2),
    7:  (ADD, 8, 1),
    8:  (ADD, 9, 1),
    9:  (ADD, 10, 1),
    10: (ADD, 11, 1),
    11: (ADD, 12, 1),
    12: (DIV, 13, 1)
  }

# ___________________________________________________________________________

# true function result - used to check result from MPC circuit
FUNCTION_RESULT = function(PRIVATE_VALUES)

N_GATES     = len(GATES)
N_PARTIES   = len(PRIVATE_VALUES)
ALL_PARTIES = range(1, N_PARTIES+1)
ALL_DEGREES = range(1, DEGREE+1)

assert PRIME > N_PARTIES, "Prime > N failed :-("
assert 2*DEGREE < N_PARTIES, "2T < N failed :-("

# Various Primes 
# PRIME = 11
# PRIME = 101
# PRIME = 1_009
# PRIME = 10_007
# PRIME = 100_003
# PRIME = 1_000_003 
# PRIME = 1_000_000_007
# PRIME = 35742549198872617291353508656626642567  # Large Bell prime


