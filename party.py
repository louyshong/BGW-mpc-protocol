from circuit import *
from modprime import *
from network import *
import functools
from log import * 

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
    receivedshares = {}

    for p in ALL_PARTIES:
        network.send_share(subshares[p], gate_no, p)
        receivedshares[p] = network.receive_share(p, gate_no)

    outputshare = lagrange_interp(receivedshares)

    return outputshare

def evaluate_div(a, party_no, gate_no, network):
    '''
    Evaluates single DIV by party_no gate
    '''
    share = div(a,party_no)
    subshares = split_share(share)
    receivedshares = {}

    for p in ALL_PARTIES:
        network.send_share(subshares[p], gate_no, p)
        receivedshares[p] = network.receive_share(p, gate_no)

    outputshare = lagrange_interp(receivedshares)

    return outputshare

def evaluate_add(a, b):
    '''
    Evaluates single ADD gate
    '''
    return add(a,b)

def evaluate_circuit(party_no, network):
    '''
    Evaluates whole circuit
    '''
    gate_inputs = {i: {k: None for k in range(1,3)} for i in range(1, N_GATES + 2)}

    for g, (kind, output_gate, input_index) in GATES.items() :

        if kind == INP:
            result = network.receive_share(g, g)

        elif kind == ADD:
            result = evaluate_add(gate_inputs[g][1], gate_inputs[g][2])

        elif kind == MUL:
            result = evaluate_mul(gate_inputs[g][1], gate_inputs[g][2], g, network)

        elif kind == DIV:
            result = evaluate_div(gate_inputs[g][1], party_no, g, network)
        
        gate_inputs[output_gate][input_index]= result

    return result

def bgw_protocol(party_no, private_value, network):

    # split and distribute shares to all parties (including self)
    subshares = split_share(private_value)

    for p in ALL_PARTIES: 
        # assuming each party has an INP gate with 
        # the same party_no
        network.send_share(subshares[p], party_no, p)

    # evaluate circuit
    output = evaluate_circuit(party_no, network)

    # broadcast circuit output to all parties (including self)
    # N_GATES + 2 is the circuit output wire
    for p in ALL_PARTIES: 
        network.send_share(output, N_GATES + 1, p)

    # receive outputs from all parties (including self)
    suboutputs = {}

    for p in ALL_PARTIES: 
        suboutputs[p] = network.receive_share(p, N_GATES + 1)

    # combine outputs 
    output = lagrange_interp(suboutputs)
    
    write(output)