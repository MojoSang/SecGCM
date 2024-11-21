from Compiler.library import *
from Compiler.types import *
from Compiler.oram import *
from dijkstra import dijkstra
from Compiler.sqrt_oram import SqrtOram
from Compiler.gs import *


def centrality(u, n, M):
    # compute all u score
    dis=sint(0)  # 使用列表来包装 minn 的值
    minn = regint(99)
    @for_range(n.reveal())
    def _(i):
    	minn.update(99)
    	@if_(M[u.reveal()][i].reveal() < 99)
    	def _():
    	    @if_(M[u.reveal()][i].reveal() < minn)  # 使用 minn[0] 来引用 minn 的值
    	    def _():
    	        minn.update(M[u.reveal()][i].reveal())
    	        dis.update(dis+minn)	
    return cfix(n.reveal()) / cfix(dis.reveal())


def centralityS(S, Sn, n, M):
    # compute an array's centrality
    sumdist = sint(0)

    @for_range(Sn)
    def _(i):
        minn = sint(99)
        # x->y
        x = S[i].reveal()

        @for_range(n.reveal())
        def _(y):

            @if_(minn.greater_than(M[x][y]).reveal())
            def _():
                minn.update(M[x][y])

        sumdist.update(sumdist + minn)

    return cfix(n.reveal()) / cfix(sumdist.reveal())


#use dijkstra to get APSP
def djk_GetM(a,b):
    '''
    :param a: player0 graph
    :param b: player1 graph
    :return: M APSP V_index n
    '''

    an=a.sizes[0]
    bn=b.sizes[0]

    #initial ORAM to store edgelist
    e_index=OptimalORAM(34,entry_size=6)
    edges=OptimalORAM(an+bn+1,entry_size=(6,2,1))
    V_index=OptimalORAM(34,entry_size=6)
    #vertex number
    n=sint(0)
    #first edge ini
    edges[0]=(a[0][1].reveal(),a[0][2].reveal(),0)
    e_index[a[0][0].reveal()]=0
    print_ln('ORAM ini finish')
    @for_range(an)
    def _(i):
        @if_(contain(V_index,n,a[i][0])==0)
        def _():
            e_index[a[i][0].reveal()]=regint(i)
            V_index[n.reveal()]=a[i][0]
            n.update(n+1)
        edges[i]=(a[i][1].reveal(),a[i][2].reveal(),1)
    @for_range(bn)
    def _(i):
        @if_(contain(V_index,n,b[i][0])==0)
        def _():
            e_index[b[i][0].reveal()]=regint(i)
            V_index[n.reveal()]=b[i][0]
            n.update(n+1)
        edges[i]=(b[i][1].reveal(),b[i][2].reveal(),1)
    # the last point to itself
    edges[an+bn] = (b[bn - 1][0].reveal(), 0, 1)


    #OMatrix M
    M=OMatrix(34,34)
    @for_range(n.reveal())
    def _(i):
        source=V_index[i]
        res=dijkstra(source,edges,e_index,OptimalORAM)
        @for_range(n.reveal())
        def _(j):
                M[i][j]=res[j]
    # M=sint.Tensor([n.reveal(),n.reveal()])
    # @for_range(n.reveal())
    # def _(i):
    #     source=V_index[i]
    #     res=dijkstra(source, edges, e_index, OptimalORAM)
    #     M[i][:]=res[:]

    return M,V_index,n






# def contain(M, n, x):
#     found = regint(0)
#
#     @for_range(n.reveal())
#     def _(i):
#         @if_((M[i] == x).reveal())
#         def _():
#             found.update(1)
#             break_loop()
#
#     return found.reveal()

def contain(M, n, x):
    found = regint(0)
    @for_range(n.reveal())
    def _(i):
        @if_((M[i].equal(x)).reveal())
        def _():
            found.update(1)
            break_loop()

    return found.reveal()

# argmax
# def argmax(V_index, n, S, Sn, Score):
#     # n: sint
#     # Sn regint
#     # V_index,Score OptimalORAM
#     # S regint Array
#     maxscore = regint(0)
#     k = regint(0)
#
#     @for_range(n.reveal())
#     def _(i):
#         w = V_index[i].reveal()
#
#         @if_(contain(V_index, n, w))
#         def _():
#             @if_(contain(S, Sn, w) == 0)
#             def _():
#                 @if_(Score[w].reveal() > maxscore)
#                 def _():
#                     maxscore.update(Score[w].reveal())
#                     k.update(w)
#
#     return k.reveal()


def argmax(V_index, n, S, Sn, Score):
    # n: sint
    # Sn regint
    # V_index,Score OptimalORAM
    # S sint Array
    maxscore = sfix(0)
    k = regint(0)

    @for_range(n.reveal())
    def _(i):
        w = V_index[i].reveal()

        @if_(contain(V_index, n, w))
        def _():
            @if_(contain(S, Sn, w) == 0)
            def _():
                @if_(Score[w]>maxscore.reveal())
                def _():
                    maxscore.update(Score[w])
                    k.update(w)

    return k.reveal()

# f(S)
def mssp(S,n,M,mn):
    '''

    :param S: seed set
    :param n: seed set size
    :param M: all vertex pairs distance
    :return: farness(regint),D(regint tensor),vsk(regint)
    '''
    farness=regint(0)
    vs=sint.Array(mn)
    #vs_length
    vsk=regint(0)
    #S[n]
    #get all reachable vertex
    @for_range(n)
    def _(i):
        #M[S][m]
        @for_range(mn)
        def _(j):
            @if_(regint(M[S[i].reveal()][j].reveal()) < 99)
            def _():
                @if_(contain(vs,vsk,j)==0)
                def _():
                    vs[vsk]=sint(j)
                    vsk.update(vsk+1)
    D=regint.Tensor([mn,2])
    #compute farness from vs
    @for_range(vsk)
    def _(i):
        min=regint(99)

        #M[Sn][vs]
        @for_range(n)
        def _(j):
            @if_(min>regint(M[S[j].reveal()][vs[i].reveal()].reveal()))
            def _():
                min.update(regint(M[S[j].reveal()][vs[i].reveal()].reveal()))
        #D[][]
        #[v1,d]
        #[v2,d]
        #...
        D[i][0]=vs[i].reveal()
        D[i][1]=min
        farness.update(farness+min)
    return farness,D,vsk


def delt_mssp(S,Sn,S_,S_n,f_,D_,Dn,M):
    # S sint.Array
    # Sn S length
    # S_n S_ length
    # S_ sint.Array
    # f_ regint
    # D_ Tensor[n,2]
    f,D,Dn=mssp(S,Sn,M)
    fs_=regint(0)
    # fs' S-> Vs'
    #D'[:][0]=Vs'
    @for_range(Dn)
    def _(j):
        min=regint(99)
        @for_range(Sn)
        def _(i):
            @if_(min<M[S[i]][D_[j][0]].reveal())
            def _():
                min.update(M[S[i]][D_[j][0]].reveal())
        fs_.update(fs_+min)

    return f,D,Dn,fs_



# compute centrality
def c(D, f, k):
    return (cfix(D) - cfix(k)) / cfix(f)


#estimate the S centrality
def estimate_centrality(S):
    '''

    :param S:
    :return:
    '''
    pass

#get mincen in a shortlist
def Min(S,n):
    '''

    :param S: shortlist sint.Tensor[n,2] [v,cen]
    :param n: size regint
    :return: point to the min
    '''


    #traverse to get mincen
    t=regint(0)
    mincen=sfloat(99.999)
    @for_range(n)
    def _(i):
        mincen.update(min(mincen,S[i][1]))
        t.update(S[i][0].round_to_int().reveal())

    return t


#next window
def next_window(W,w,S,Sn,V,n):
    '''
    :param W: ORAM sint
    :param w: ORAM length
    :param S: Seed set sint
    :param Sn: Seed set size k
    :param V: V_index ORAM
    :param n: Vertex num sint
    :return: W a bigger window ORAM and its length

    from V add k vertex into W
    w get into 2w
    if |V-W|<k
        add all V-W into W
    thus we need to obtain an order called seed candidates
    it has phi seeds which is decided by user
    to creater this
    we rank all vertex outside the window  considering by
    vertex add in S+ and estimate centrality and then rank
    we get an order of short list
    some seeds

    for v in V-W
        for s in S+
         instead s by v
         compute its max centrality and record v centrality

    then we get v(V-M),maxcen
    matain a w-length shortlist
    if  |shortlist|<w
    add vertex and its maxcen
    once add a vertex into short list
    record the mincen in this shortlist
    if |shortlist|=w
    compare new vertex maxcen and the mincen
        if bigger permute the vertex and its maxcen
        refresh mincen and v
    '''

    #initial short list
    #[n,2]
    #[vi,maxcen(sfix)]
    short_list=sfloat.Tensor([w.reveal(),2])
    sln=regint(0)

    #traverse the v
    @for_range(n.reveal())
    def _(i):
        #find v in V-W
        maxcen=regint(0)
        @if_(contain(W,w,V[i])==0)
        def _():
            S_ = sint.Array(Sn)
            S_.assign(S)
            #traverse S+
            @for_range(Sn)
            def _(j):
                #permute s,v
                S_[j]=V[i]
                #estimate centrality
                estcen=estimate_centrality(S_)
                @if_(maxcen<estcen)
                def _():
                    #record maxcen according to its v
                    maxcen.update(estcen)
        #get v and its maxcen
        #add directly
        @if_e(sln<w.reveal())
        def _():
            short_list[sln][0]=sfloat(V[i])
            short_list[sln][1]=sfloat(maxcen)
            sln.update(sln+1)
        #find permute
        @else_
        def _():
            #n point to the v(short_list[n][0]),and the mincen(short_list[n][1])
            n=Min(short_list,sln)
            @if_(maxcen>short_list[n][1])
            def _():
                short_list[n][0]=V[i]
                short_list[n][1]=maxcen
        #get short list with sln-length,sln=w
    Wn=OptimalORAM(2*w)
    @for_range(w)
    def _(i):
        Wn[i]=W[i]
    Wn_len=regint(w)
    @for_range(sln)
    def _(i):
        Wn[w+i]=short_list[i][0]
        Wn_len.update(w+1)
    return Wn,Wn_len

















def explore(W,k,S_,n,i,f_,D_,D_n,w,c_p,M):
    # W ORAM sint
    # k regint
    # S_ sint.Array
    # n S_ length
    # i  regint
    # f_ regint
    # D_ Tensor[Dn,2] Dn:|Vs|
    # Dn n
    # w |W|
    # c_p regint
    # M pairs shortest distance
    S_n=regint(n)
    S_p=sint.Array(k)
    mo=OptimalORAM(5)
    mo.get_array().length
    @if_e(S_n=k)
    def _():
        #c'
        c_=c(D_n,f_,k)
        @if_(c_>c_p)
        def _():
            S_p.assign(S_)
            c_p=c_
            return S_p,c_p
    @else_
    def _():
        del_up=regint(0)
        del_low=regint(999)
        j=w
        @while_do(lambda:j>i)
        def _():
            @if_(k-S_n==1)
            def _():
                @if_(j<=w)
                def _():
                    return S_p,c_p
            S=S_
            #vj=W[j]  ??
            S[S_n]=W[j]
            Sn=S_n+1

            f,D,Dn,fs_=delt_mssp(S,Sn,S_,S_n,f_,D_,D_n,M)
            alpha=regint(k-Sn)
            V_=sint.Array(W-j)
            V_n=sint(0)
            @for_range(j+1,w)
            def _(x):
                V_[V_n.reveal()]=W[x]
            @if_(V_n.greater_equal(alpha).reveal())
            def _():
                @if_(V_n.equal(0).bit_or(c(Dn+alpha*del_up,f_+alpha*del_low,k)>c_p))
                def _():
                    explore(W,k,S,Sn,j+1,f,D,Dn,w,c_p,M)
            del_up.update(max(Dn-D_n,del_up))
            del_low.update(min(fs_-f_,del_low))






def test():
    M=SqrtOram(sint.Tensor([5,5]))
    m=sfix(66.6)
    s=m.round_nearest










