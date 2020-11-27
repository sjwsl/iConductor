N = int(1e3 + 10)
len1, len2 = 20, 20


class Node:
    def __init__(self):
        self.L = 0
        self.R = 0
        self.V = []


class SegTree:

    def __init__(self):
        self.T = []
        self.A = []
        for _ in range(N):
            n = Node()
            self.T.append(n)

    def init(self, p, L, R):
        self.T[p].L = L
        self.T[p].R = R
        if L == R:
            return
        mid = (L + R) // 2
        self.init(p * 2, L, mid)
        self.init(p * 2 + 1, mid + 1, R)

    def insert(self, p, L, R, x):
        # print(self.T[p].L, self.T[p].R, self.T[p].V)
        self.T[p].V.append(x)
        if L <= self.T[p].L and R >= self.T[p].R:
            return
        mid = (self.T[p].L + self.T[p].R) // 2
        if L <= mid:
            self.insert(p * 2, L, R, x)
        if R > mid:
            self.insert(p * 2 + 1, L, R, x)

    def build(self, dic):
        self.init(1, 0, 180)
        for x in list(dic):
            L = max(0, dic[x][0] - len1)
            R = min(180, dic[x][0] + len1)
            # print(x, L, R)
            self.insert(1, L, R, x)
            self.query(L, R)
        print(self.A)

    def query(self, L, R):
        self.A = []
        self.query_func(1, L, R)
        self.A = list(set(self.A))

    def query_func(self, p, L, R):
        if L <= self.T[p].L and R >= self.T[p].R:
            for x in self.T[p].V:
                self.A.append(x)
            return
        mid = (self.T[p].L + self.T[p].R) // 2
        if L <= mid:
            self.query_func(p * 2, L, R)
        if R > mid:
            self.query_func(p * 2 + 1, L, R)
