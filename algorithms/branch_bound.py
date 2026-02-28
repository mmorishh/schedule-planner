import time

class BranchBoundSolver:
    def __init__(self, graph):
        self.graph = graph
        self.n = graph.n
        self.adj = graph.adj
        self.best = None
        self.best_k = self.n
        self.nodes = 0
        self.cut = 0
        self.cache = {}

    def _upper_bound(self):
        colors = [-1] * self.n
        order = []
        for i in range(self.n):
            order.append((self.graph.degree(i), i))
        order.sort(reverse=True)

        for deg, v in order:
            used = []
            for u in self.graph.neighbors(v):
                if colors[u] != -1:
                    used.append(colors[u])
            used_set = set(used)
            c = 0
            while c in used_set:
                c += 1
            colors[v] = c
        return colors
    
    def _clique_bound(self, remaining):
        if not remaining:
            return 0
        key = str(sorted(remaining))
        if key in self.cache:
            return self.cache[key]
        
        clique = []
        for v in remaining:
            ok = True
            for u in clique:
                if not self.adj[v][u]:
                    ok = False
                    break
            if ok:
                clique.append(v)
        
        res = len(clique)
        self.cache[key] = res
        return res
    
    def _select(self, colors):
        best = -1
        best_score = -1
        for v in range(self.n):
            if colors[v] == -1:
                cnt = 0
                for u in self.graph.neighbors(v):
                    if colors[u] != -1:
                        cnt += 1
                score = self.graph.degree(v) * 2 + cnt
                if score > best_score:
                    best_score = score
                    best = v
        return best
    
    def _search(self, colors, k, bound):
        self.nodes += 1
        if k + bound >= self.best_k:
            self.cut += 1
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
        
        for c in range(k):
            safe = True
            for u in self.graph.neighbors(v):
                if colors[u] == c:
                    safe = False
                    break
            if safe:
                colors[v] = c
                nb = self._clique_bound(remaining)
                self._search(colors, k, nb)
                colors[v] = -1
                if self.best_k == bound:
                    return
        
        if k + 1 < self.best_k:
            colors[v] = k
            nb = self._clique_bound(remaining)
            self._search(colors, k + 1, nb)
            colors[v] = -1
    
    def solve(self):
        start = time.time()
        self.nodes = 0
        self.cut = 0
        self.cache = {}
        
        init = self._upper_bound()
        self.best_k = max(init) + 1
        self.best = init
        
        all_vertices = list(range(self.n))
        bound = self._clique_bound(all_vertices)
        colors = [-1] * self.n
        self._search(colors, 0, bound)
        
        self.time = time.time() - start
        return self.best, self.best_k
    
    def get_statistics(self):
        return {
            "nodes": self.nodes,
            "cuts": self.cut,
            "cache_size": len(self.cache),
            "time": round(self.time, 3)
        }