# tuck hong (tkh2017) and preet lalli (pl1516)

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

    message = str(share)

    for deg in range(DEGREE):
        rand_coeff = randint()
        polynomial.append(rand_coeff)
        message += ' + ' + str(rand_coeff) + 'x^' + str(deg + 1)

    write('Random polynomial: ' + message)

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

    return share, recomb_vector

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

    outputshare, _ = lagrange_interp(receivedshares)

    write('Received shares are: ' + str(receivedshares))

    return outputshare

def evaluate_div(a, gate_no, network):
    '''
    Evaluates single DIV by N_PARTIES gate
    '''
    share = div(a, N_PARTIES)
    subshares = split_share(share)
    receivedshares = {}

    for p in ALL_PARTIES:
        network.send_share(subshares[p], gate_no, p)
        receivedshares[p] = network.receive_share(p, gate_no)

    outputshare, _ = lagrange_interp(receivedshares)

    write('Received shares are: ' + str(receivedshares))

    return outputshare

def evaluate_add(a, b):
    '''
    Evaluates single ADD gate
    ''' 
    return add(a,b)

def evaluate_circuit(network):
    '''
    Evaluates whole circuit
    '''
    gate_inputs = {i: {k: None for k in range(1,3)} for i in range(1, N_GATES + 2)}

    # for logging
    input_shares = {}

    for g, (kind, output_gate, input_index) in GATES.items() :

        if kind == INP:
            result = network.receive_share(g, g)
            input_shares[g] = result

            # add to log once all input shares have been received
            if g == N_PARTIES: 
                write('Received shares are: ' + str(input_shares))

        elif kind == ADD:
            result = evaluate_add(gate_inputs[g][1], gate_inputs[g][2])
            write('ADD result is: ' + str(result))

        elif kind == MUL:
            write('Evaluating MUL gate')
            result = evaluate_mul(gate_inputs[g][1], gate_inputs[g][2], g, network)
            write('MUL result is: ' + str(result))

        elif kind == DIV:
            write('Evaluating DIV gate')
            result = evaluate_div(gate_inputs[g][1], g, network)
            write('DIV result is: ' + str(result))
        
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
    output = evaluate_circuit(network)

    # broadcast circuit output to all parties (including self)
    # N_GATES + 2 is the circuit output wire
    for p in ALL_PARTIES: 
        network.send_share(output, N_GATES + 1, p)

    # receive outputs from all parties (including self)
    suboutputs = {}

    for p in ALL_PARTIES: 
        suboutputs[p] = network.receive_share(p, N_GATES + 1)

    write('Received output shares are: ' + str(suboutputs))

    # combine outputs 
    output, recomb_vector = lagrange_interp(suboutputs)

    write('The recombination vector is: ' + str(recomb_vector))
    write('The final output is: ' + str(output))
