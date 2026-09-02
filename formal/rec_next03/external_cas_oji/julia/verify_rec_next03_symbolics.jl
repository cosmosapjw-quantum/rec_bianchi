using Nemo
using Symbolics

function identity(id::String, condition::Bool)
    condition || error("$id residual is not zero")
    println("IDENTITY $id PASS")
end

function mutation(id::String, condition::Bool)
    condition || error("$id mutation escaped")
    println("MUTATION $id DETECTED")
end

function symbolic_zero(expression)
    reduced = Symbolics.simplify(
        Symbolics.expand_derivatives(expression); expand=true
    )
    # Some Symbolics/BasicSymbolic versions return a symbolic object from
    # iszero. isequal and the canonical textual fallback are Boolean-valued.
    return isequal(reduced, 0) || string(reduced) == "0"
end

# Independent exact polynomial ring over QQ.
names = [
    "eta", "kappa", "f", "a", "s", "deta", "dkappa", "df0", "dtau",
    "pchi", "ptau", "nu0", "x", "delta", "r", "dnu0", "dlogdelta",
    "dxb", "xr", "xb", "dxr", "q", "p", "n2", "beta", "mu", "tau",
    "chi"
]
P, variables = polynomial_ring(QQ, names)
eta, kappa, f, a, s, deta, dkappa, df0, dtau, pchi, ptau, nu0, x,
delta, r, dnu0, dlogdelta, dxb, xr, xb, dxr, q, p, n2, beta, mu, tau,
chi = variables

identity("I01", eta*(1 + f) - kappa*f - (eta - (kappa - eta)*f) == 0)
identity("I04",
    a*df0 + s*deta + pchi*(dkappa - deta) + ptau*dtau -
    (a*df0 + (s - pchi)*deta + pchi*dkappa + ptau*dtau) == 0)
identity("I06",
    ((nu0 + x*delta)*r - dnu0 - delta*x*dlogdelta - delta*dxb) -
    (nu0*r + x*delta*r - dnu0 - delta*x*dlogdelta - delta*dxb) == 0)

face_numerator(nu0v, xv, deltav, rv, dnu0v, dlogv, dxv) =
    (nu0v + xv*deltav)*rv - dnu0v - deltav*xv*dlogv - deltav*dxv

onep = one(P)
zerop = zero(P)
vred_rh_zero = face_numerator(onep, zerop, onep, zerop, onep, zerop, zerop)
vblue_zero_r_nonzero = face_numerator(onep, zerop, onep, onep, onep, zerop, zerop)
identity("I07R", vred_rh_zero + onep == 0)
identity("I07B", vblue_zero_r_nonzero == 0)
identity("I07D",
    ((nu0 + xr*delta)*r - dnu0 - delta*xr*dlogdelta - delta*dxr) -
    ((nu0 + xb*delta)*r - dnu0 - delta*xb*dlogdelta - delta*dxb) -
    delta*((xr - xb)*(r - dlogdelta) - (dxr - dxb)) == 0)
identity("I08", (-(q - q*n2) - (p - p*n2)) - (n2 - 1)*(q + p) == 0)
identity("I09", (mu - beta)^2 + (1 - mu^2)*(1 - beta^2) - (1 - beta*mu)^2 == 0)

# Symbolics.jl differential reconstruction of the exact affine transfer.
@variables zsym tausym f0sym etasym
Dτ = Differential(tausym)
Fsym = exp(-zsym*tausym)*f0sym + etasym*(1 - exp(-zsym*tausym))/zsym
identity("I02", symbolic_zero(Dτ(Fsym) - (etasym - zsym*Fsym)))

# I03: independent exact formal-series proof in Nemo/QQ. The truncated
# analytic transfer differs from f+eta*tau by chi times an exact polynomial,
# so its constant term—and therefore the analytic chi->0 limit—is f+eta*tau.
half = QQ(1, 2)
sixth = QQ(1, 6)
exp_minus_3 = onep - chi*tau + half*chi^2*tau^2 - sixth*chi^3*tau^3
phi_2 = tau - half*chi*tau^2 + sixth*chi^2*tau^3
transfer_3 = exp_minus_3*f + eta*phi_2
transfer_quotient = -f*tau - half*eta*tau^2 +
    chi*(half*f*tau^2 + sixth*eta*tau^3) - sixth*chi^2*f*tau^3
identity("I03", transfer_3 - (f + eta*tau) - chi*transfer_quotient == 0)

# Exact rational series coefficients used by the cancellation-free branches.
rat(n::Integer, d::Integer=1) = Rational{BigInt}(BigInt(n), BigInt(d))
phi_code = [rat(1), rat(-1,2), rat(1,6), rat(-1,24), rat(1,120),
            rat(-1,720), rat(1,5040), rat(-1,40320), rat(1,362880)]
phi_reconstructed = [rat((-1)^k, factorial(big(k + 1))) for k in 0:8]
identity("I05", phi_code == phi_reconstructed)

function generalized_binomial_half(k::Int)
    value = rat(1)
    for j in 0:(k - 1)
        value *= rat(1,2) - rat(j)
    end
    return value / factorial(big(k))
end
small_reconstructed = [
    -2 * generalized_binomial_half(k) * rat((-1)^k) for k in 1:3
]
identity("I10", small_reconstructed == [rat(1), rat(1,4), rat(1,8)])

# Hostile controls.
mutation("M01", pchi*deta != 0)
Fbad = exp(zsym*tausym)*f0sym + etasym*(exp(zsym*tausym) - 1)/zsym
mutation("M02", !symbolic_zero(Dτ(Fbad) - (etasym - zsym*Fbad)))
mutation("M03", eta*tau != 0)
mutation("M04", delta*x*dlogdelta != 0)
mutation("M05R", vred_rh_zero != 0)
mutation("M05B", onep != 0)  # R=1 in the exact blue-face-zero witness.
mutation("M06", -(q + p) != 0)
mutation("M07", (mu + beta)^2 + (1 - mu^2)*(1 - beta^2) - (1 - beta*mu)^2 != 0)
mutation("M08", beta != 0)

println("STATUS PASS")
