1;

function require_zero(id, expression)
  reduced = simplify(expression);
  if (!isequal(reduced, sym(0)))
    error("%s residual is not zero: %s", id, char(reduced));
  endif
  fprintf("IDENTITY %s PASS\n", id);
endfunction

function require_nonzero(id, expression)
  reduced = simplify(expression);
  if (isequal(reduced, sym(0)))
    error("%s mutation escaped", id);
  endif
  fprintf("MUTATION %s DETECTED\n", id);
endfunction

pkg load symbolic;

syms f eta kappa f0 tau chi df0 deta dkappa dtau real;

% I01: exact affine source identity.
require_zero("I01", eta*(1 + f) - kappa*f - (eta - (kappa - eta)*f));

% I02-I04: exact constant-pair transfer and analytic JVP.
A = exp(-chi*tau);
S = (1 - A)/chi;
F = A*f0 + eta*S;
require_zero("I02", diff(F, tau) - (eta - chi*F));
require_zero("I03", limit(F, chi, 0) - (f0 + eta*tau));
S_chi = diff(S, chi);
chi_partial = -tau*A*f0 + eta*S_chi;
tau_partial = -chi*A*f0 + eta*A;
jvp_direct = diff(F, f0)*df0 + diff(F, eta)*deta + ...
             diff(F, chi)*(dkappa - deta) + diff(F, tau)*dtau;
jvp_code = A*df0 + S*deta + chi_partial*(dkappa - deta) + ...
           tau_partial*dtau;
require_zero("I04", jvp_direct - jvp_code);

% I05: cancellation-free source-factor series through x^8.
syms z real;
phi = (1 - exp(-z))/z;
phi_expected = 1 - z/2 + z^2/6 - z^3/24 + z^4/120 - z^5/720 + ...
               z^6/5040 - z^7/40320 + z^8/362880;
% Octave symbolic's order is one past the largest retained exponent.
require_zero("I05", taylor(phi, z, 0, 'order', 9) - phi_expected);

% I06: moving Doppler-coordinate chain rule.
syms nu0 x Delta R dnu0 dlogDelta dxb real;
nu = nu0 + x*Delta;
dnu = nu*R;
dDelta = Delta*dlogDelta;
dx_direct = (dnu - dnu0)/Delta - (nu - nu0)*dDelta/Delta^2 - dxb;
dx_code = ((nu0 + x*Delta)*R - dnu0)/Delta - x*dlogDelta - dxb;
require_zero("I06", dx_direct - dx_code);

% I07H/I07R/I07B/I07D/I07J: separate event functions and rank.
syms xr xb dxr real;
vred_num = (nu0 + xr*Delta)*R - dnu0 - Delta*xr*dlogDelta - Delta*dxr;
vblue_num = (nu0 + xb*Delta)*R - dnu0 - Delta*xb*dlogDelta - Delta*dxb;

red_at_hubble_zero = subs(vred_num, ...
  [nu0, xr, Delta, R, dnu0, dlogDelta, dxr], ...
  [1, 0, 1, 0, 1, 0, 0]);
blue_at_hubble_zero = subs(vblue_num, ...
  [nu0, xb, Delta, R, dnu0, dlogDelta, dxb], ...
  [1, 0, 1, 0, 1, 0, 1]);
hubble_zero_witness = [sym(0), red_at_hubble_zero, blue_at_hubble_zero];
require_zero("I07H", hubble_zero_witness(1)^2 + ...
  (hubble_zero_witness(2) + 1)^2 + (hubble_zero_witness(3) + 2)^2);

red_at_red_zero = subs(vred_num, ...
  [nu0, xr, Delta, R, dnu0, dlogDelta, dxr], ...
  [1, 0, 1, 1, 1, 0, 0]);
blue_at_red_zero = subs(vblue_num, ...
  [nu0, xb, Delta, R, dnu0, dlogDelta, dxb], ...
  [1, 0, 1, 1, 1, 0, -1]);
red_zero_witness = [sym(1), red_at_red_zero, blue_at_red_zero];
require_zero("I07R", (red_zero_witness(1) - 1)^2 + ...
  red_zero_witness(2)^2 + (red_zero_witness(3) - 1)^2);

red_at_blue_zero = subs(vred_num, ...
  [nu0, xr, Delta, R, dnu0, dlogDelta, dxr], ...
  [1, 0, 1, 1, 1, 0, -1]);
blue_at_blue_zero = subs(vblue_num, ...
  [nu0, xb, Delta, R, dnu0, dlogDelta, dxb], ...
  [1, 0, 1, 1, 1, 0, 0]);
blue_zero_witness = [sym(1), red_at_blue_zero, blue_at_blue_zero];
require_zero("I07B", (blue_zero_witness(1) - 1)^2 + ...
  (blue_zero_witness(2) - 1)^2 + blue_zero_witness(3)^2);

face_difference = Delta*((xr - xb)*(R - dlogDelta) - (dxr - dxb));
require_zero("I07D", (vred_num - vblue_num) - face_difference);

event_jacobian = [sym(1), sym(0), sym(0); ...
                  nu0 + Delta*xr, -Delta, sym(0); ...
                  nu0 + Delta*xb, sym(0), -Delta];
require_zero("I07J", det(event_jacobian) - Delta^2);

% I08: projection form of the normal-frame direction flow is tangent.
syms n2 q p real;
projection_dot = -(q - q*n2) - (p - p*n2);
require_zero("I08", projection_dot - (n2 - 1)*(q + p));

% I09: denominator-cleared axial aberration norm identity.
syms beta mu real;
aberration_numerator = (mu - beta)^2 + (1 - mu^2)*(1 - beta^2) - ...
                       (1 - beta*mu)^2;
require_zero("I09", aberration_numerator);

% I10: exact small-beta identity-branch error series.
small_error = 2*beta/(1 + sqrt(1 - beta^2));
small_expected = beta + beta^3/4 + beta^5/8;
require_zero("I10", taylor(small_error, beta, 0, 'order', 7) - small_expected);

% Hostile controls. Each event mutation uses the reconstructed event functions
% or Jacobian; no renamed numeric-constant check is admitted.
require_nonzero("M01", chi_partial*deta);
F_bad = exp(chi*tau)*f0 + eta*(exp(chi*tau) - 1)/chi;
require_nonzero("M02", diff(F_bad, tau) - (eta - chi*F_bad));
require_nonzero("M03", eta*tau);
require_nonzero("M04", x*dlogDelta);
require_nonzero("M05H", R - vred_num);
require_nonzero("M05R", vred_num - vblue_num);
require_nonzero("M05B", vblue_num - R);
mutated_difference_residual = (vred_num - vblue_num) - ...
  Delta*((xr - xb)*(R - dlogDelta));
require_nonzero("M05D", mutated_difference_residual);
mutated_event_jacobian = [event_jacobian(1, :); ...
                          event_jacobian(2, :); ...
                          event_jacobian(2, :)];
require_nonzero("M05J", det(mutated_event_jacobian) - Delta^2);
require_nonzero("M06", -(q + p));
wrong_aberration = (mu + beta)^2 + (1 - mu^2)*(1 - beta^2) - ...
                    (1 - beta*mu)^2;
require_nonzero("M07", wrong_aberration);
require_nonzero("M08", small_error);

fprintf("STATUS PASS\n");
