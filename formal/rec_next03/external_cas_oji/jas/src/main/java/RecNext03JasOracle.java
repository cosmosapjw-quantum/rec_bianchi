import edu.jas.arith.BigRational;
import edu.jas.poly.GenPolynomial;
import edu.jas.poly.GenPolynomialRing;

/** Exact polynomial oracle for REC-NEXT-03 formula contracts. */
public final class RecNext03JasOracle {
    private static final String[] VARIABLES = {
        "eta", "kappa", "f", "a", "s", "deta", "dkappa", "df0", "dtau",
        "pchi", "ptau", "nu0", "x", "delta", "r", "dnu0", "dlogdelta",
        "dxb", "xr", "xb", "dxr", "q", "p", "n2", "beta", "mu", "tau"
    };

    private static final GenPolynomialRing<BigRational> RING =
        new GenPolynomialRing<>(new BigRational(1), VARIABLES);

    private RecNext03JasOracle() {}

    private static GenPolynomial<BigRational> polynomial(String expression) {
        return RING.parse(expression);
    }

    private static void identity(String id, String expression) {
        GenPolynomial<BigRational> value = polynomial(expression);
        if (!value.isZERO()) {
            throw new IllegalStateException(id + " residual is nonzero: " + value);
        }
        System.out.println("IDENTITY " + id + " PASS");
    }

    private static void mutation(String id, String expression) {
        GenPolynomial<BigRational> value = polynomial(expression);
        if (value.isZERO()) {
            throw new IllegalStateException(id + " mutation escaped");
        }
        System.out.println("MUTATION " + id + " DETECTED");
    }

    public static void main(String[] args) {
        identity("I01",
            "eta*(1+f)-kappa*f-(eta-(kappa-eta)*f)");

        identity("I04",
            "a*df0+s*deta+pchi*(dkappa-deta)+ptau*dtau"
            + "-(a*df0+(s-pchi)*deta+pchi*dkappa+ptau*dtau)");

        identity("I06",
            "((nu0+x*delta)*r-dnu0-delta*x*dlogdelta-delta*dxb)"
            + "-(nu0*r+x*delta*r-dnu0-delta*x*dlogdelta-delta*dxb)");

        identity("I07",
            "((nu0+xr*delta)*r-dnu0-delta*xr*dlogdelta-delta*dxr)"
            + "-((nu0+xb*delta)*r-dnu0-delta*xb*dlogdelta-delta*dxb)"
            + "-delta*((xr-xb)*(r-dlogdelta)-(dxr-dxb))");

        identity("I08",
            "(-(q-q*n2)-(p-p*n2))-((n2-1)*(q+p))");

        identity("I09",
            "(mu-beta)^2+(1-mu^2)*(1-beta^2)-(1-beta*mu)^2");

        mutation("M01", "pchi*deta");
        mutation("M03", "eta*tau");
        mutation("M04", "delta*x*dlogdelta");
        mutation("M05", "1");
        mutation("M06", "-(q+p)");
        mutation("M07",
            "(mu+beta)^2+(1-mu^2)*(1-beta^2)-(1-beta*mu)^2");
        mutation("M08", "beta");

        System.out.println("STATUS PASS");
    }
}
