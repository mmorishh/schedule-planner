import time

class BrownAlgorithm:
    def __init__(self, graph):
        self.graph = graph
        self.n = graph.n
        self.adj = graph.adj
        self.best = None
        self.best_k = self.n
        self.nodes = 0
        self.clique = []
    
    def _find_clique(self):
        order = []
        for i in range(self.n):
            order.append((self.graph.degree(i), i))
        order.sort(reverse=True)
        
        clique = []
        for deg, v in order:
            ok = True
            for u in clique:
                if not self.adj[v][u]:
                    ok = False
                    break
            if ok:
                clique.append(v)
        return clique
    
    def _bound(self, remaining, colors):
        if not remaining:
            return 0
        used_colors = 0
        for i in range(self.n):
            if colors[i] != -1:
                used_colors += 1
        
        max_deg = 0
        for v in remaining:
            cnt = 0
            for u in remaining:
                if v != u and self.adj[v][u]:
                    cnt += 1
            if cnt > max_deg:
                max_deg = cnt
        
        b1 = max_deg + 1
        b2 = len(self.clique)
        b3 = used_colors + 1
        return max(b1, b2, b3)
    
    def _select(self, colors):
        best = -1
        best_score = -1
        for v in range(self.n):
            if colors[v] == -1:
                cnt = 0
                for u in self.graph.neighbors(v):
                    if colors[u] != -1:
                        cnt += 1
                if cnt > best_score:
                    best_score = cnt
                    best = v
        return best
    
    def _search(self, colors, k, bound):
        self.nodes += 1
        if k + bound >= self.best_k:
            return
        
        v = self._select(colors)
        if v == -1:
            if k < self.best_k:
                self.best_k = k
                self.best = colors.copy()
            return
        
        remaining = []
        for i in range(self.n):
            if colors[i] == -1 and i != v:
                remaining.append(i)
        
        forbidden = set()
        for u in self.graph.neighbors(v):
            if colors[u] != -1:
                forbidden.add(colors[u])
        
        for c in range(k):
            if c not in forbidden:
                colors[v] = c
                nb = self._bound(remaining, colors)
                self._search(colors, k, nb)
                colors[v] = -1
                if self.best_k == bound:
                    return
        
        if k + 1 < self.best_k:
            colors[v] = k
            nb = self._bound(remaining, colors)
            self._search(colors, k + 1, nb)
            colors[v] = -1
    
    def solve(self):
        start = time.time()
        self.nodes = 0
        self.clique = self._find_clique()
        bound = len(self.clique)
    
        colors = [-1] * self.n
        for i, v in enumerate(self.clique):
            colors[v] = i
    
        remaining = []
        for i in range(self.n):
            if colors[i] == -1:
                remaining.append(i)
    
        self.best = None
        self.best_k = self.n
    
        self._search(colors, bound, self._bound(remaining, colors))
    
        # Если не нашли решение, возвращаем хотя бы жадное
        if self.best is None:
            from algorithms.branch_bound import BranchBoundSolver
            fallback = BranchBoundSolver(self.graph)
            self.best, self.best_k = fallback.solve()
    
        self.time = time.time() - start
        return self.best, self.best_k
    
    def get_statistics(self):
        return {
            "nodes": self.nodes,
            "clique_size": len(self.clique),
            "time": round(self.time, 3)
        }