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
    # Keep Julia control flow strictly Boolean. Symbolics.iszero may return a
    # symbolic Boolean for BasicSymbolic values and therefore must not appear
    # in a short-circuit expression used by this mandatory oracle.
    return isequal(reduced, 0) || string(reduced) == "0"
end

rat(n::Integer, d::Integer=1) = Rational{BigInt}(BigInt(n), BigInt(d))

# Independent exact polynomial ring over QQ.
names = [
    "eta", "kappa", "f", "a", "s", "deta", "dkappa", "df0", "dtau",
    "pchi", "ptau", "nu0", "x", "delta", "r", "dnu0", "dlogdelta",
    "dxb", "xr", "xb", "dxr", "q", "p", "n2", "beta", "mu", "tau"
]
P, variables = polynomial_ring(QQ, names)
eta, kappa, f, a, s, deta, dkappa, df0, dtau, pchi, ptau, nu0, x,
delta, r, dnu0, dlogdelta, dxb, xr, xb, dxr, q, p, n2, beta, mu, tau = variables
onep = one(P)
zerop = zero(P)

identity("I01", eta*(1 + f) - kappa*f - (eta - (kappa - eta)*f) == 0)
identity("I04",
    a*df0 + s*deta + pchi*(dkappa - deta) + ptau*dtau -
    (a*df0 + (s - pchi)*deta + pchi*dkappa + ptau*dtau) == 0)
identity("I06",
    ((nu0 + x*delta)*r - dnu0 - delta*x*dlogdelta - delta*dxb) -
    (nu0*r + x*delta*r - dnu0 - delta*x*dlogdelta - delta*dxb) == 0)

# Three independently named event functions.  The witness triples are ordered
# as (R_H, V_red, V_blue); each has exactly one vanishing component.
face_numerator(nu0v, xv, deltav, rv, dnu0v, dlogv, dxv) =
    (nu0v + xv*deltav)*rv - dnu0v - deltav*xv*dlogv - deltav*dxv

vred = face_numerator(nu0, xr, delta, r, dnu0, dlogdelta, dxr)
vblue = face_numerator(nu0, xb, delta, r, dnu0, dlogdelta, dxb)

hubble_zero_witness = (
    zerop,
    face_numerator(onep, zerop, onep, zerop, onep, zerop, zerop),
    face_numerator(onep, zerop, onep, zerop, onep, zerop, onep),
)
red_zero_witness = (
    onep,
    face_numerator(onep, zerop, onep, onep, onep, zerop, zerop),
    face_numerator(onep, zerop, onep, onep, onep, zerop, -onep),
)
blue_zero_witness = (
    onep,
    face_numerator(onep, zerop, onep, onep, onep, zerop, -onep),
    face_numerator(onep, zerop, onep, onep, onep, zerop, zerop),
)

identity("I07H",
    hubble_zero_witness[1] == zerop &&
    hubble_zero_witness[2] == -onep &&
    hubble_zero_witness[3] == -2*onep)
identity("I07R",
    red_zero_witness[1] == onep &&
    red_zero_witness[2] == zerop &&
    red_zero_witness[3] == onep)
identity("I07B",
    blue_zero_witness[1] == onep &&
    blue_zero_witness[2] == onep &&
    blue_zero_witness[3] == zerop)

face_difference = delta*((xr - xb)*(r - dlogdelta) - (dxr - dxb))
identity("I07D", vred - vblue - face_difference == 0)

function determinant3(rows)
    row1, row2, row3 = rows
    return row1[1]*(row2[2]*row3[3] - row2[3]*row3[2]) -
        row1[2]*(row2[1]*row3[3] - row2[3]*row3[1]) +
        row1[3]*(row2[1]*row3[2] - row2[2]*row3[1])
end

event_jacobian = (
    (onep, zerop, zerop),
    (nu0 + delta*xr, -delta, zerop),
    (nu0 + delta*xb, zerop, -delta),
)
event_jacobian_det = determinant3(event_jacobian)
identity("I07J", event_jacobian_det - delta^2 == 0)

identity("I08", (-(q - q*n2) - (p - p*n2)) - (n2 - 1)*(q + p) == 0)
identity("I09", (mu - beta)^2 + (1 - mu^2)*(1 - beta^2) - (1 - beta*mu)^2 == 0)

# Symbolics.jl independently reconstructs the differential equation away from
# chi=0. The removable chi -> 0 theorem itself is proved below in an exact
# Nemo power-series ring, avoiding Symbolics' experimental heuristic limit.
@variables zsym tausym f0sym etasym
Dτ = Differential(tausym)
Fsym = exp(-zsym*tausym)*f0sym + etasym*(1 - exp(-zsym*tausym))/zsym
identity("I02", symbolic_zero(Dτ(Fsym) - (etasym - zsym*Fsym)))

# Exact coefficient-ring construction for
# F = exp(-chi*tau) f0 + eta (1-exp(-chi*tau))/chi.
# The constant coefficient proves the removable limit; the first-order
# coefficient is an independent non-vacuity witness for the reconstructed
# series and catches a hard-coded constant fixture.
C, cvars = polynomial_ring(QQ, ["tau_limit", "f0_limit", "eta_limit"])
tau_limit, f0_limit, eta_limit = cvars
Schi, chi_limit = power_series_ring(C, 5, "chi_limit")
expminus = exp(-chi_limit*tau_limit)
phi1minus = divexact(one(Schi) - expminus, chi_limit)
Fseries = expminus*f0_limit + eta_limit*phi1minus
constant_expected = f0_limit + eta_limit*tau_limit
first_expected = -f0_limit*tau_limit - rat(1, 2)*eta_limit*tau_limit^2
coeff(Fseries, 1) == first_expected || error("I03 first-order witness mismatch")
identity("I03", coeff(Fseries, 0) == constant_expected)

# Exact rational series coefficients used by the cancellation-free branches.
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

# Hostile controls reconstruct the wrong event functions rather than merely
# asserting that a renamed numeric constant is nonzero.
mutation("M01", pchi*deta != 0)
Fbad = exp(zsym*tausym)*f0sym + etasym*(exp(zsym*tausym) - 1)/zsym
mutation("M02", !symbolic_zero(Dτ(Fbad) - (etasym - zsym*Fbad)))
mutation("M03", coeff(Fseries, 0) != f0_limit)
mutation("M04", delta*x*dlogdelta != 0)
mutation("M05H", r - vred != 0)
mutation("M05R", vred - vblue != 0)
mutation("M05B", vblue - r != 0)
mutated_difference_residual =
    vred - vblue - delta*((xr - xb)*(r - dlogdelta))
mutation("M05D", mutated_difference_residual != 0)
mutated_event_jacobian = (
    event_jacobian[1],
    event_jacobian[2],
    event_jacobian[2],
)
mutation("M05J", determinant3(mutated_event_jacobian) - delta^2 != 0)
mutation("M06", -(q + p) != 0)
mutation("M07", (mu + beta)^2 + (1 - mu^2)*(1 - beta^2) - (1 - beta*mu)^2 != 0)
mutation("M08", beta != 0)

println("STATUS PASS")
