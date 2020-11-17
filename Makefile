# secure multi-party computation, semi-honest case, distributed, v1
# naranker dulay, dept of computing, imperial college, october 2020
# tuck hong (tkh2017) and preet lalli (pl1516)

PYTHON = python3

default:
	${PYTHON} mpc.py

sort:
	${PYTHON} mpc.py | sort

clean:
	rm -rf __pycache__ 

rmold:
	rm -i *~ 

pkill:
	pkill -9 -f MPC_PROCESS

output-only: 
	${PYTHON} mpc.py | sort | grep 'final output\|ANSWER\|CIRCUIT'