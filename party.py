from circuit import ALL_PARTIES, DEGREE
from modprime import *
from network import *
import functools

def split_share(share):
    '''
    Splits share into N_PARTIES shares. 
    '''
    # generate a random polynomial 
    polynomial = []
    
    # constant term is = share
    polynomial.append(share)

    for deg in range(DEGREE):
        polynomial.append(randint())

    print(polynomial)
    # allocate subshares for all parties
    subshares = {}
    for p in ALL_PARTIES:
        terms = [coeff * (p ** i) for i, coeff in enumerate(polynomial)]
        subshares[p] = summation(terms)

    return subshares

def lagrange_interp(subshares):
    '''
    Recombine subshares
    '''
    recomb_vector = {}

    # find recombination vector
    for p, _ in subshares.items():
        numer_list = []
        denom_list = []
        
        for other_p, _ in subshares.items():
            if other_p != p: 
                numer_list.append(other_p)
                denom_list.append(other_p - p)    

        numer = product(numer_list)
        denom = product(denom_list)

        recomb_vector[p] = div(numer, denom)

    terms = []

    # do lagrange interpolation
    for p, subshare in subshares.items():
        terms.append(recomb_vector[p] * subshare)

    share = summation(terms)

    return share

def evaluate_mul(a, b, gate_no, network):
    '''
    Evaluates single MUL gate
    '''
    share = mul(a,b)
    subshares = split_share(share)
    recievedshares = []

    for p in ALL_PARTIES:
        network.send_share(subshares[p], gate_no, p)
        recievedshares.append(network.recieve_share(p, gate_no))

    outputshare = lagrange_interp(recievedshares)

    return outputshare

def evaluate_add(a, b):
    '''
    Evaluates single ADD gate
    '''
    return add(a,b)

def evaluate_circuit():
    '''
    Evaluates whole circuit
    '''

def bgw_protocol(party_no, private_value, network):