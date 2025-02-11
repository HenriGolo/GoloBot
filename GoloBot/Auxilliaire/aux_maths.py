def produit(*args, init=1):
    res = init
    for i in args:
        res *= i
    return res


def factorielle(n):
    if n < 0:
        raise Exception
    if n in (0, 1):
        return 1
    return n * factorielle(n - 1)


# n! / (n-k)!
def arrangement(k, n):
    return produit(*[n - i for i in range(k)])


# n! / (k! * (n-k)!)
def parmi(k, n):
    if 1 in [k, n-k]:
        return n
    return parmi(k-1, n-1) + parmi(k, n-1)


# VAR uniforme sur [|1,n|]
class Uniforme:
    def __init__(self, n):
        self.n = n

    # P(X=k), préciser k sert pas à grand-chose
    def proba(self, k: int = 0):
        return 1 / self.n

    # P(X<=k)
    def proba_inf(self, k):
        return k / self.n

    # P(X>=k)
    def proba_sup(self, k):
        return (self.n - k) / self.n


# VAR binomiale, taille n, paramètre p
class Binomiale:
    def __init__(self, n, p):
        self.n = n
        self.p = p

    # P(X=k)
    def proba(self, k: int):
        pa = parmi(k, self.n)
        p = self.p ** k
        q = (1 - self.p) ** (self.n - k)
        return pa * p * q

    # P(X<=k)
    def proba_inf(self, k):
        # k plus proche de la fin que du début
        if 2 * k > self.n:
            return 1 - self.proba_sup(k + 1)
        return sum([self.proba(i) for i in range(k + 1)])

    # P(X>=k)
    def proba_sup(self, k):
        # k plus proche du début que de la fin
        if 2 * k < self.n:
            return 1 - self.proba_inf(k - 1)
        return sum([self.proba(i) for i in range(k, self.n + 1)])
