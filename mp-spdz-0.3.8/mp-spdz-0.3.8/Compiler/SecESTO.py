from oram import *
from sorting import *
INF = sint(9999)
'''
    vertex from 0 ...|v|
    origin from v0
    E Dst to Rcd should change vertex index
'''


def get_length(S, N):
    n = cint(0)

    @for_range(N)
    def _(i):
        @if_((S[i] != 0).bit_and(S[i] != INF).reveal())
        def _():
            n.update(n + 1)

    return n

def centrality(V_S,f,V,k):
    '''
        compute the group closeness centrality
    '''
    a=sfloat(0)
    b=sfloat(0)
    print_ln('V_s:%s,f:%s',V_S.reveal(),f.reveal())
    a.update(sfloat(V_S-k)/sfloat(f))
    b.update(sfloat(V_S-k)/sfloat(V-3))
    return sfloat(a*b)

def sort(aux,auv,V):
    aux1=sfix.Array(V)
    auv1=sint.Array(V)
    @for_range(V)
    def _(i):
        aux1[i]=aux[sint(i)]
        auv1[i]=auv[sint(i)]
    radix_sort(aux1,auv1)

    return auv1



def rdsum(S, n, Rcd, Ind, V):
    '''
    :param S: seed set
    :param n: seed set size
    :param Rcd: reachable and distance
    :param Ind: index
    :param V: vertex size
    :return: farness reachable Array D, |V_s|
    '''
    D = OptimalORAM(V)
    farness = sint(0)
    V_s = sint(0)
    pos = Ind[S[sint(0)]]
    i=sint(0)
    INF.update(V)
    @for_range(V)
    def _(i):
        D[sint(i)] = INF
    # Initialize finish
    @while_do(lambda:i.reveal()<n)
    def _():
        s_=S[i+1]
        flag=pos.equal(Ind[s_])
        i.update(i+flag)
        pp=Ind[s_]
        pos.update((pp-pos)*flag+pos)
        (rp,dp)=Rcd[pos]
        dp_=D[rp]
        sp=dp_.min(dp)
        D[rp]=sp
        pos.update(pos+1)
    @for_range(V)
    def _(i):
        flag=D[sint(i)]<INF
        farness.update(farness+flag*D[sint(i)])
        V_s.update(V_s+flag)
    
    return farness,D,V_s


def d_rdsum(S,D_,Rcd,Ind,V):
    Dt=sint.Matrix(1,V)
    Dx=sint.Matrix(1,V)
    Fs,D,VS=rdsum(S,2,Rcd,Ind,V)
    @for_range(V)
    def _(i):
        d_=D_[sint(i)]
        Dx[0][i]=D[sint(i)]
        Dt[0][i]=d_.equal(INF)
    fs=Dx.dot(Dt.transpose())
    return Fs,D,VS,fs[0][0]

def win_expand(W,w,Rcd,Ind,S,V,k):
    '''
    :param W: previous window
    :param w: previous window size
    :param Rcd: reachable and distance
    :param Ind: index
    :param S: seed set
    :param Ext: exist array
    :param V: vertex number
    :param k: seed set size
    :return: larger window W_
    '''
    aux=sfix.Array(V)
    auv=sint.Array(V)
    Wn=W
    wn=w
    n=regint(0)
    Ext=OptimalORAM(V)
    @for_range(w)
    def _(i):
        Ext[W[sint(i)]] = sint(1)
    @if_e(V>2*w)
    def _():
        @for_range(V)
        def _(i):
            print_ln('windows expand:%s current size:%s',i,w)
            maxc=sfix(0)
            @if_(Ext[i].equal(0).reveal())
            def _():
                S_=S
                @for_range(k)
                def _(j):
                    S_[j].update(sint(i))
                    f,d,Vs=rdsum(S,3,Rcd,Ind,V)
                    c_=centrality(Vs,f,V,k)
                    maxc.update(maxc.max(c_))
                aux[n]=maxc
                auv[n]=sint(i)
                n.update(n+1)
        radix_sort(aux,auv)
        print_ln('finish window size:%s sort',w)
        p=sint(w)
        #choose top-w vertexes add in W
        @for_range(V-1,w-1,-1)
        def _(j):
            nonlocal Wn
            Wn[p]=auv[j]
            p.update(p+1)
        wn.update(wn*2)
    @else_
    def _():
        p=sint(w)
        @for_range(V)
        def _(i):
            @if_(Ext[i].equal(0).reveal())
            def _():
                nonlocal Wn
                Wn[p]=sint(i)
                p.update(p+1)
        wn.update(V)
    return Wn,wn



def explore(W,wn,Rcd,Ind,w,V,Sp,cp):
    S=OptimalORAM(3)
    @for_range_opt(wn-2)
    def _(i):
        S[sint(0)]=W[sint(i)]
        print_ln('explore i:%s',i)
        f,D,Vs=rdsum(S,1,Rcd,Ind,V)
        del_up=sint(0)
        del_down=INF
        @for_range_opt(wn-1,w,-1)
        def _(j):
            S[sint(1)]=W[sint(j)]
            f_,D_,Vs_,fs_=d_rdsum(S,D,Rcd,Ind,V)
            c_up=centrality(Vs_+del_up,fs_+del_down,V,3)
            @if_((c_up>cp).reveal())
            def _():
                @for_range_opt(wn-1,w,-1)
                def _(l):
                    S[sint(2)]=W[sint(l)]
                    f__,D__,Vs__=rdsum(S,3,Rcd,Ind,V)
                    c_=centrality(Vs__,f__,V,3)
                    @if_((c_>cp).reveal())
                    def _():
                        @for_range(3)
                        def _(o):
                            Sp[sint(o)]=S[sint(o)]
                        cp.update(c_)
                        print_ln('current optimal centrality:%s',cp.reveal())
            del_up.update(del_up.max(Vs_-Vs))
            del_down.update(del_down.min(fs_-f))
    return Sp,cp




def find(Rcd, Ind, V,Sp):
    W = OptimalORAM(V)
    f, D, V_s = rdsum(Sp,3, Rcd, Ind,V)
    cp=centrality(V_s,f,V,3)
    print_ln('rsdum cp:%s',cp.reveal())
    #initialize W and ext
    @for_range(3)
    def _(i):
        temp = Sp[i]
        W[sint(i)] = temp

    w = regint(3)
    print_ln('Initialize finish')

    @while_do(lambda: w<V)
    def _():
        nonlocal W,Sp
        print_ln('start window expand currentsize:%s',w)
        W,wn=win_expand(W,w,Rcd,Ind,Sp,V,3)
        print_ln('window expand finish,current size:%s,previous size:%s',wn,w)
        print_ln('start explore')
        S,c=explore(W,wn,Rcd,Ind,w,V,Sp,cp)
        print_ln('explore finish')
        w.update(wn)
        Sp=S
        cp.update(c)
        @for_range(3)
        def _(k):
            print_ln('current SP:%s,cp:%s',Sp[k].reveal(),cp.reveal())

        # @for_range(wn)
        # def _(j):
        #     W[sint(j)]=wn[sint(j)]

    @for_range(3)
    def _(k):
        print_ln('optimal seed set:%s',Sp[k].reveal())
    print_ln('centrality:%s',cp.reveal())
