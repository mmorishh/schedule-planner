import time

class IndependentSetSolver:
    def __init__(self, graph):
        self.graph = graph
        self.n = graph.n
        self.adj = graph.adj
        self.best = None
        self.best_k = self.n
        self.sets = []
        self.combinations = 0
        self.pruned = 0
    
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
    
    def _bron_kerbosch(self, r, p, x):
        if not p and not x:
            self.sets.append(list(r))
            return
        if not p:
            return
        
        pivot_set = set()
        for e in p:
            pivot_set.add(e)
        for e in x:
            pivot_set.add(e)
        pivot = list(pivot_set)[0] if pivot_set else None
        
        p_list = list(p)
        for v in p_list:
            if pivot and self.adj[v][pivot]:
                continue
            
            new_r = r.copy()
            new_r.add(v)
            
            new_p = set()
            for u in p:
                if self.adj[v][u]:
                    new_p.add(u)
            
            new_x = set()
            for u in x:
                if self.adj[v][u]:
                    new_x.add(u)
            
            self._bron_kerbosch(new_r, new_p, new_x)
            p.remove(v)
            x.add(v)
    
    def _find_sets(self):
        self.sets = []
        all_vertices = set(range(self.n))
        self._bron_kerbosch(set(), all_vertices, set())
        self.sets.sort(key=len, reverse=True)
        return self.sets
    
    def _cover(self, colors, used, idx):
        self.combinations += 1
        if used >= self.best_k:
            self.pruned += 1
            return False
        
        all_done = True
        for i in range(self.n):
            if colors[i] == -1:
                all_done = False
                break
        if all_done:
            if used < self.best_k:
                self.best_k = used
                self.best = colors.copy()
            return True
        
        if idx >= len(self.sets):
            return False
        
        current = self.sets[idx]
        can_use = True
        for v in current:
            if colors[v] != -1:
                can_use = False
                break
        
        if can_use:
            for v in current:
                colors[v] = used
            self._cover(colors, used + 1, idx + 1)
            for v in current:
                colors[v] = -1
        
        self._cover(colors, used, idx + 1)
        return False
    
    def solve(self):
        start = time.time()
        self.combinations = 0
        self.pruned = 0
        
        init = self._upper_bound()
        self.best_k = max(init) + 1
        self.best = init
        
        self._find_sets()
        colors = [-1] * self.n
        self._cover(colors, 0, 0)
        
        self.time = time.time() - start
        return self.best, self.best_k
    
    def get_statistics(self):
        return {
            "sets_found": len(self.sets),
            "combinations": self.combinations,
            "pruned": self.pruned,
            "time": round(self.time, 3)
        }