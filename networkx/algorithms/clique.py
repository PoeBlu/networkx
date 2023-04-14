"""Functions for finding and manipulating cliques.

Finding the largest clique in a graph is NP-complete problem, so most of
these algorithms have an exponential running time; for more information,
see the Wikipedia article on the clique problem [1]_.

.. [1] clique problem:: https://en.wikipedia.org/wiki/Clique_problem

"""
from collections import deque
from itertools import chain
from itertools import combinations
from itertools import islice
import networkx as nx
from networkx.utils import not_implemented_for

__all__ = ['find_cliques', 'find_cliques_recursive', 'make_max_clique_graph',
           'make_clique_bipartite', 'graph_clique_number',
           'graph_number_of_cliques', 'node_clique_number',
           'number_of_cliques', 'cliques_containing_node',
           'enumerate_all_cliques']


@not_implemented_for('directed')
def enumerate_all_cliques(G):
    """Returns all cliques in an undirected graph.

    This function returns an iterator over cliques, each of which is a
    list of nodes. The iteration is ordered by cardinality of the
    cliques: first all cliques of size one, then all cliques of size
    two, etc.

    Parameters
    ----------
    G : NetworkX graph
        An undirected graph.

    Returns
    -------
    iterator
        An iterator over cliques, each of which is a list of nodes in
        `G`. The cliques are ordered according to size.

    Notes
    -----
    To obtain a list of all cliques, use
    `list(enumerate_all_cliques(G))`. However, be aware that in the
    worst-case, the length of this list can be exponential in the number
    of nodes in the graph (for example, when the graph is the complete
    graph). This function avoids storing all cliques in memory by only
    keeping current candidate node lists in memory during its search.

    The implementation is adapted from the algorithm by Zhang, et
    al. (2005) [1]_ to output all cliques discovered.

    This algorithm ignores self-loops and parallel edges, since cliques
    are not conventionally defined with such edges.

    References
    ----------
    .. [1] Yun Zhang, Abu-Khzam, F.N., Baldwin, N.E., Chesler, E.J.,
           Langston, M.A., Samatova, N.F.,
           "Genome-Scale Computational Approaches to Memory-Intensive
           Applications in Systems Biology".
           *Supercomputing*, 2005. Proceedings of the ACM/IEEE SC 2005
           Conference, pp. 12, 12--18 Nov. 2005.
           <https://doi.org/10.1109/SC.2005.29>.

    """
    index = {}
    nbrs = {}
    for u in G:
        index[u] = len(index)
        # Neighbors of u that appear after u in the iteration order of G.
        nbrs[u] = {v for v in G[u] if v not in index}

    queue = deque(([u], sorted(nbrs[u], key=index.__getitem__)) for u in G)
    # Loop invariants:
    # 1. len(base) is nondecreasing.
    # 2. (base + cnbrs) is sorted with respect to the iteration order of G.
    # 3. cnbrs is a set of common neighbors of nodes in base.
    while queue:
        base, cnbrs = map(list, queue.popleft())
        yield base
        for i, u in enumerate(cnbrs):
            # Use generators to reduce memory consumption.
            queue.append((chain(base, [u]),
                          filter(nbrs[u].__contains__,
                                 islice(cnbrs, i + 1, None))))


@not_implemented_for('directed')
def find_cliques(G):
    """Returns all maximal cliques in an undirected graph.

    For each node *v*, a *maximal clique for v* is a largest complete
    subgraph containing *v*. The largest maximal clique is sometimes
    called the *maximum clique*.

    This function returns an iterator over cliques, each of which is a
    list of nodes. It is an iterative implementation, so should not
    suffer from recursion depth issues.

    Parameters
    ----------
    G : NetworkX graph
        An undirected graph.

    Returns
    -------
    iterator
        An iterator over maximal cliques, each of which is a list of
        nodes in `G`. The order of cliques is arbitrary.

    See Also
    --------
    find_cliques_recursive
        A recursive version of the same algorithm.

    Notes
    -----
    To obtain a list of all maximal cliques, use
    `list(find_cliques(G))`. However, be aware that in the worst-case,
    the length of this list can be exponential in the number of nodes in
    the graph. This function avoids storing all cliques in memory by
    only keeping current candidate node lists in memory during its search.

    This implementation is based on the algorithm published by Bron and
    Kerbosch (1973) [1]_, as adapted by Tomita, Tanaka and Takahashi
    (2006) [2]_ and discussed in Cazals and Karande (2008) [3]_. It
    essentially unrolls the recursion used in the references to avoid
    issues of recursion stack depth (for a recursive implementation, see
    :func:`find_cliques_recursive`).

    This algorithm ignores self-loops and parallel edges, since cliques
    are not conventionally defined with such edges.

    References
    ----------
    .. [1] Bron, C. and Kerbosch, J.
       "Algorithm 457: finding all cliques of an undirected graph".
       *Communications of the ACM* 16, 9 (Sep. 1973), 575--577.
       <http://portal.acm.org/citation.cfm?doid=362342.362367>

    .. [2] Etsuji Tomita, Akira Tanaka, Haruhisa Takahashi,
       "The worst-case time complexity for generating all maximal
       cliques and computational experiments",
       *Theoretical Computer Science*, Volume 363, Issue 1,
       Computing and Combinatorics,
       10th Annual International Conference on
       Computing and Combinatorics (COCOON 2004), 25 October 2006, Pages 28--42
       <https://doi.org/10.1016/j.tcs.2006.06.015>

    .. [3] F. Cazals, C. Karande,
       "A note on the problem of reporting maximal cliques",
       *Theoretical Computer Science*,
       Volume 407, Issues 1--3, 6 November 2008, Pages 564--568,
       <https://doi.org/10.1016/j.tcs.2008.05.010>

    """
    if len(G) == 0:
        return

    adj = {u: {v for v in G[u] if v != u} for u in G}
    Q = [None]

    subg = set(G)
    cand = set(G)
    u = max(subg, key=lambda u: len(cand & adj[u]))
    ext_u = cand - adj[u]
    stack = []

    try:
        while True:
            if ext_u:
                q = ext_u.pop()
                cand.remove(q)
                Q[-1] = q
                adj_q = adj[q]
                if subg_q := subg & adj_q:
                    if cand_q := cand & adj_q:
                        stack.append((subg, cand, ext_u))
                        Q.append(None)
                        subg = subg_q
                        cand = cand_q
                        u = max(subg, key=lambda u: len(cand & adj[u]))
                        ext_u = cand - adj[u]
                else:
                    yield Q[:]
            else:
                Q.pop()
                subg, cand, ext_u = stack.pop()
    except IndexError:
        pass


# TODO Should this also be not implemented for directed graphs?
def find_cliques_recursive(G):
    """Returns all maximal cliques in a graph.

    For each node *v*, a *maximal clique for v* is a largest complete
    subgraph containing *v*. The largest maximal clique is sometimes
    called the *maximum clique*.

    This function returns an iterator over cliques, each of which is a
    list of nodes. It is a recursive implementation, so may suffer from
    recursion depth issues.

    Parameters
    ----------
    G : NetworkX graph

    Returns
    -------
    iterator
        An iterator over maximal cliques, each of which is a list of
        nodes in `G`. The order of cliques is arbitrary.

    See Also
    --------
    find_cliques
        An iterative version of the same algorithm.

    Notes
    -----
    To obtain a list of all maximal cliques, use
    `list(find_cliques_recursive(G))`. However, be aware that in the
    worst-case, the length of this list can be exponential in the number
    of nodes in the graph. This function avoids storing all cliques in memory
    by only keeping current candidate node lists in memory during its search.

    This implementation is based on the algorithm published by Bron and
    Kerbosch (1973) [1]_, as adapted by Tomita, Tanaka and Takahashi
    (2006) [2]_ and discussed in Cazals and Karande (2008) [3]_. For a
    non-recursive implementation, see :func:`find_cliques`.

    This algorithm ignores self-loops and parallel edges, since cliques
    are not conventionally defined with such edges.

    References
    ----------
    .. [1] Bron, C. and Kerbosch, J.
       "Algorithm 457: finding all cliques of an undirected graph".
       *Communications of the ACM* 16, 9 (Sep. 1973), 575--577.
       <http://portal.acm.org/citation.cfm?doid=362342.362367>

    .. [2] Etsuji Tomita, Akira Tanaka, Haruhisa Takahashi,
       "The worst-case time complexity for generating all maximal
       cliques and computational experiments",
       *Theoretical Computer Science*, Volume 363, Issue 1,
       Computing and Combinatorics,
       10th Annual International Conference on
       Computing and Combinatorics (COCOON 2004), 25 October 2006, Pages 28--42
       <https://doi.org/10.1016/j.tcs.2006.06.015>

    .. [3] F. Cazals, C. Karande,
       "A note on the problem of reporting maximal cliques",
       *Theoretical Computer Science*,
       Volume 407, Issues 1--3, 6 November 2008, Pages 564--568,
       <https://doi.org/10.1016/j.tcs.2008.05.010>

    """
    if len(G) == 0:
        return iter([])

    adj = {u: {v for v in G[u] if v != u} for u in G}
    Q = []

    def expand(subg, cand):
        u = max(subg, key=lambda u: len(cand & adj[u]))
        for q in cand - adj[u]:
            cand.remove(q)
            Q.append(q)
            adj_q = adj[q]
            subg_q = subg & adj_q
            if not subg_q:
                yield Q[:]
            else:
                cand_q = cand & adj_q
                if cand_q:
                    yield from expand(subg_q, cand_q)
            Q.pop()

    return expand(set(G), set(G))


def make_max_clique_graph(G, create_using=None):
    """Returns the maximal clique graph of the given graph.

    The nodes of the maximal clique graph of `G` are the cliques of
    `G` and an edge joins two cliques if the cliques are not disjoint.

    Parameters
    ----------
    G : NetworkX graph

    create_using : NetworkX graph constructor, optional (default=nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    NetworkX graph
        A graph whose nodes are the cliques of `G` and whose edges
        join two cliques if they are not disjoint.

    Notes
    -----
    This function behaves like the following code::

        import networkx as nx
        G = nx.make_clique_bipartite(G)
        cliques = [v for v in G.nodes() if G.nodes[v]['bipartite'] == 0]
        G = nx.bipartite.project(G, cliques)
        G = nx.relabel_nodes(G, {-v: v - 1 for v in G})

    It should be faster, though, since it skips all the intermediate
    steps.

    """
    B = G.__class__() if create_using is None else nx.empty_graph(0, create_using)
    cliques = list(enumerate(set(c) for c in find_cliques(G)))
    # Add a numbered node for each clique.
    B.add_nodes_from(i for i, c in cliques)
    # Join cliques by an edge if they share a node.
    clique_pairs = combinations(cliques, 2)
    B.add_edges_from((i, j) for (i, c1), (j, c2) in clique_pairs if c1 & c2)
    return B


def make_clique_bipartite(G, fpos=None, create_using=None, name=None):
    """Returns the bipartite clique graph corresponding to `G`.

    In the returned bipartite graph, the "bottom" nodes are the nodes of
    `G` and the "top" nodes represent the maximal cliques of `G`.
    There is an edge from node *v* to clique *C* in the returned graph
    if and only if *v* is an element of *C*.

    Parameters
    ----------
    G : NetworkX graph
        An undirected graph.

    fpos : bool
        If True or not None, the returned graph will have an
        additional attribute, `pos`, a dictionary mapping node to
        position in the Euclidean plane.

    create_using : NetworkX graph constructor, optional (default=nx.Graph)
       Graph type to create. If graph instance, then cleared before populated.

    Returns
    -------
    NetworkX graph
        A bipartite graph whose "bottom" set is the nodes of the graph
        `G`, whose "top" set is the cliques of `G`, and whose edges
        join nodes of `G` to the cliques that contain them.

        The nodes of the graph `G` have the node attribute
        'bipartite' set to 1 and the nodes representing cliques
        have the node attribute 'bipartite' set to 0, as is the
        convention for bipartite graphs in NetworkX.

    """
    B = nx.empty_graph(0, create_using)
    B.clear()
    # The "bottom" nodes in the bipartite graph are the nodes of the
    # original graph, G.
    B.add_nodes_from(G, bipartite=1)
    for i, cl in enumerate(find_cliques(G)):
        # The "top" nodes in the bipartite graph are the cliques. These
        # nodes get negative numbers as labels.
        name = -i - 1
        B.add_node(name, bipartite=0)
        B.add_edges_from((v, name) for v in cl)
    return B


def graph_clique_number(G, cliques=None):
    """Returns the clique number of the graph.

    The *clique number* of a graph is the size of the largest clique in
    the graph.

    Parameters
    ----------
    G : NetworkX graph
        An undirected graph.

    cliques : list
        A list of cliques, each of which is itself a list of nodes. If
        not specified, the list of all cliques will be computed, as by
        :func:`find_cliques`.

    Returns
    -------
    int
        The size of the largest clique in `G`.

    Notes
    -----
    You should provide `cliques` if you have already computed the list
    of maximal cliques, in order to avoid an exponential time search for
    maximal cliques.

    """
    if cliques is None:
        cliques = find_cliques(G)
    return 0 if len(G.nodes) < 1 else max([len(c) for c in cliques] or [1])


def graph_number_of_cliques(G, cliques=None):
    """Returns the number of maximal cliques in the graph.

    Parameters
    ----------
    G : NetworkX graph
        An undirected graph.

    cliques : list
        A list of cliques, each of which is itself a list of nodes. If
        not specified, the list of all cliques will be computed, as by
        :func:`find_cliques`.

    Returns
    -------
    int
        The number of maximal cliques in `G`.

    Notes
    -----
    You should provide `cliques` if you have already computed the list
    of maximal cliques, in order to avoid an exponential time search for
    maximal cliques.

    """
    if cliques is None:
        cliques = list(find_cliques(G))
    return len(cliques)


def node_clique_number(G, nodes=None, cliques=None):
    """ Returns the size of the largest maximal clique containing
    each given node.

    Returns a single or list depending on input nodes.
    Optional list of cliques can be input if already computed.
    """
    if cliques is None:
        if nodes is not None:
            # Use ego_graph to decrease size of graph
            if isinstance(nodes, list):
                d = {}
                for n in nodes:
                    H = nx.ego_graph(G, n)
                    d[n] = max((len(c) for c in find_cliques(H)))
            else:
                H = nx.ego_graph(G, nodes)
                d = max((len(c) for c in find_cliques(H)))
            return d
        # nodes is None--find all cliques
        cliques = list(find_cliques(G))

    if nodes is None:
        nodes = list(G.nodes())   # none, get entire graph

    if not isinstance(nodes, list):   # check for a list
        v = nodes
        # assume it is a single value
        d = max(len(c) for c in cliques if v in c)
    else:
        d = {v: max(len(c) for c in cliques if v in c) for v in nodes}
    return d

    # if nodes is None:                 # none, use entire graph
    #     nodes=G.nodes()
    # elif  not isinstance(nodes, list):    # check for a list
    #     nodes=[nodes]             # assume it is a single value

    # if cliques is None:
    #     cliques=list(find_cliques(G))
    # d={}
    # for v in nodes:
    #     d[v]=max([len(c) for c in cliques if v in c])

    # if nodes in G:
    #     return d[v] #return single value
    # return d


def number_of_cliques(G, nodes=None, cliques=None):
    """Returns the number of maximal cliques for each node.

    Returns a single or list depending on input nodes.
    Optional list of cliques can be input if already computed.
    """
    if cliques is None:
        cliques = list(find_cliques(G))

    if nodes is None:
        nodes = list(G.nodes())   # none, get entire graph

    if isinstance(nodes, list):
        return {v: len([1 for c in cliques if v in c]) for v in nodes}
    v = nodes
        # assume it is a single value
    return len([1 for c in cliques if v in c])


def cliques_containing_node(G, nodes=None, cliques=None):
    """Returns a list of cliques containing the given node.

    Returns a single list or list of lists depending on input nodes.
    Optional list of cliques can be input if already computed.
    """
    if cliques is None:
        cliques = list(find_cliques(G))

    if nodes is None:
        nodes = list(G.nodes())   # none, get entire graph

    if isinstance(nodes, list):
        return {v: [c for c in cliques if v in c] for v in nodes}
    v = nodes
        # assume it is a single value
    return [c for c in cliques if v in c]
