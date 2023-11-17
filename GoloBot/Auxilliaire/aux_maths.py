def factorielle(n):
    if n < 0:
        raise Exception
    if n == 0 or n == 1:
        return 1
    return n * factorielle(n - 1)


def arrangement(k, n):
    if k > n:
        return 0
    a = 1
    for i in range(n, k, -1):
        a *= i
    return a


def parmi(k, n):
    if n - k < k:
        return parmi(n - k, n)
    if k == 0:
        return 1
    if k == 1:
        return n
    return arrangement(k, n) // factorielle(k)


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
