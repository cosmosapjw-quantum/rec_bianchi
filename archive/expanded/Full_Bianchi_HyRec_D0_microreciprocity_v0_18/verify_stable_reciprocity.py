import mpmath as mp
mp.mp.dps=80

def log_s(Q,dE,beta,mass):
    return (mp.mpf('0.5')*mp.log(beta*mass/(2*mp.pi))-mp.log(Q)
            -beta*mass*(dE-Q**2/(2*mass))**2/(2*Q**2))
Q=mp.mpf('1.1e-26'); dE=mp.mpf('2.9e-23')
beta=mp.mpf('2.41432350534664e19'); mass=mp.mpf('1.673532840653473e-27')
f=log_s(Q,dE,beta,mass)
r_direct=log_s(Q,-dE,beta,mass)
r_stable=f-beta*dE
assert abs(r_direct-r_stable)<mp.mpf('1e-60')
print('stable DSF reciprocity: PASS')
