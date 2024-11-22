from Compiler.library import *
from Compiler.types import *
from sqrt_oram import *


def contain(M, n, x):
    '''
    x in M?
    :param M: Array or matrix sint
    :param n: length sint
    :param x: var
    :return: 1 yes or 0 no
    '''
    # found flag
    found = sint(0)

    @if_e(isinstance(M, Array))
    def _():
        @for_range(n.reveal())
        def _(i):
            @if_(M[i].equal(x).reveal())
            def _():
                found.update(sint(1))
                break_loop()

    @else_
    def _():
        @if_e(isinstance(M, SqrtOram))
        def _():
            @for_range(n.reveal())
            def _(i):
                @if_(M[i].equal(x).reveal())
                def _():
                    found.update(sint(1))
                    break_loop()

        @else_
        def _():
            print(333)

    return found.reveal()


def mssp(S, Sn, M, n, V):
    '''
    :param S: seed set sint.Array
    :param Sn: seed set size sint
    :param M: APSP OMatrix sint
    :param n: vertexnumber regint
    :param V: V_index sint.Array
    :return: f:farness, D: {(v,d(s,v))}, Dn:|Vs|
    '''
    farness = sint(0)
    Vs = sint.Array(n)
    Vs_len = sint(0)

    # get all reachable vertex from S by M
    # traverse all s in S
    @for_range(Sn.reveal())
    def _(i):
        @for_range(n)
        def _(j):
            # <99 has path; contain prevent repeat
            @if_(M[S[i].reveal()][V[j].reveal()].less_than(99).bit_and(contain(Vs, Vs_len, V[j]) == 0).reveal())
            def _():
                # store vertex and store Vj
                Vs[Vs_len.reveal()] = V[j]
                Vs_len.update(Vs_len + 1)

    # got all reachable vertex in Vs and length Vs_len

    # store s->v and dist [[v1,dv1],[v2,dv2]...]
    D = sint.Tensor([34, 2])

    @for_range(Vs_len.reveal())
    def _(j):
        # for each v find min dist from S
        # refresh min
        minn = sint(99)  # record the min dist

        @for_range(Sn.reveal())
        def _(i):
            # M[i][j]= s->v dist
            # @if_(min.greater_than(M[Sn[i].reveal()][Vs[j].reveal()]))
            # def _():
            minn.update(minn.min(M[S[i].reveal()][Vs[j].reveal()]))

        # got one vertex dist from s
        # store v and dist
        D[j][0] = Vs[j]
        D[j][1] = minn
        # compute sum farness
        farness.update(farness + minn)

        # got D,farness

    return farness, D, Vs_len


def del_mssp(S, Sn, S_, f_, D_, D_n, M, n, V):
    '''
    :param S: recent level seedset
    :param Sn: recent seed set size
    :param S_: previous seed set
    :param D_: previous seed set reachable vertex set
    :param M: APSP Matrix
    :param n: vertex num
    :param V: V_index
    :return: f recent farness, D recent reachable set, fs estimate up
    '''
    f, D, Dn = mssp(S, Sn, M, n, V)
    fs_ = sint(0)

    # D_ sint.Tensor:[v,d(s',v)] Dn size
    @for_range(Sn.reveal())
    def _(x):
        # for each refresh a min farness
        minn = sint(99)

        @for_range(D_n.reveal())
        def _(y):
            minn.update(minn.min(M[S[x].reveal()][D_[y][0].reveal()]))

        fs_.update(fs_ + minn)

    return f, D, Dn, fs_


def centrality(Vs_len, f, k, n):
    '''
    :param Vs_len: reachable set length sint
    :param f: farness sint
    :param k: k regint
    :param n: all vertex num regint
    :return:centrality sfix
    '''
    # print_ln('centrality:%s,%s,%s,%s',Vs_len.reveal(),f.reveal(),k,n)
    a = sfloat(0)  # fenzi
    b = sfloat(0)  # fenmu
    a = (Vs_len - k) * (Vs_len - k)
    b = f * (n - k)
    return a / b


def estic(S, Sn, n, M, V):
    '''
    :param S: Seed set sint.Array
    :param Sn: Seed set size sint
    :param n: all vertex num regint
    :param M: APSP OMatrix sint
    :param V: V_index sint.Array
    :return:estic sfix
    '''
    sumdist = sint(0)

    @for_range(Sn.reveal())
    def _(i):
        # refresh minn
        minn = sint(99)

        # find min d(s,v)
        @for_range(n)
        def _(j):
            minn.update(minn.min(M[S[i].reveal()][V[j].reveal()]))

        # update
        sumdist.update(sumdist + minn)

    return sfix(n) / sfix(sumdist.reveal())


def test(W, w):
    # wn=sint(0)
    # Wn=SqrtOram(sint.Tensor([34,1]))
    @while_do(lambda: w.less_than(10).reveal())
    def _():
        nonlocal W, w
        Wn, wn = bigger(W, w)
        W = Wn
        w.update(wn)
        print_ln('%s', w.reveal())

    @for_range(w.reveal())
    def _(i):
        print_ln('%s', W[sint(i)].reveal())


def bigger(W, w):
    Wn = SqrtOram(sint.Tensor([34, 1]))
    wn = 2 * w

    @for_range(w.reveal())
    def _(i):
        Wn[sint(i)] = W[sint(i)]

    @for_range(w.reveal())
    def _(i):
        Wn[sint(w + i)] = W[sint(i)]

    return Wn, wn


def next_window(W, w, S, Sn, V, n, M):
    '''
    :param W: previous window SqrtOram[sint]=sint
    :param w: now window size sint
    :param S: seed set sint.Array
    :param Sn: recent S size sint
    :param V: V_index sint.Array
    :param n: V_index length
    :param M: APSP Matrix OMatrix sint
    :return: larger window Wn(SqrtOram); Wn_len new window size sint
    '''

    # get a shortlist to store candidate seeds
    # shortlist [[v1,c(s+v1)],[v2,c(s+v2)]...]
    shortlist = sfix.Tensor([34, 2])
    sln = sint(0)  # store recent shortlist size

    # treverse v in V
    @for_range(n)
    def _(i):
        maxcen = sfix(0)  # record the maxcen after S-{s]+vi

        # find vertex in V-w
        @if_(contain(W, w, V[i]) == 0)
        def _():
            # new temper S_ means S-{s}+{vi}
            S_ = sint.Array(3)
            S_.assign(S)

            # some seed selection strategy
            @for_range(3)
            def _(j):
                S_[j].update(V[i])  # S-{s}+{vi}
                # estimate its cen
                estcen = estic(S, Sn, n, M, V)
                maxcen.update(maxcen.max(estcen))

            # got vi maxcen
            # store in a shortlist only not in W will store
            # if shortlist not full
            @if_e(sln.less_than(w).reveal())
            def _():
                shortlist[sln.reveal()][0] = sfix(V[i])
                shortlist[sln.reveal()][1] = maxcen
                sln.update(sln + 1)

            # if shotlist has full
            # find the min and update
            @else_
            def _():
                # find the minn
                n = sint(0)
                mincen = sfix(99)

                @for_range(sln.reveal())
                def _(k):
                    @if_(mincen.reveal() > shortlist[k][1].reveal())
                    def _():
                        n.update(k)
                        mincen.update(shortlist[k][1])

                # got the minn shortlist in n
                @if_(maxcen.reveal() > shortlist[n.reveal()][1].reveal())
                def _():
                    shortlist[n.reveal()][0] = V[i]
                    shortlist[n.reveal()][1] = maxcen

    # got a shortlist with size of w or min(|W|,|V-W|)
    print_ln('got a shortlist')

    # Wn = SqrtOram(sint.Tensor([34, 1]))
    # wn=regint(0)
    # # copy previous window
    # @for_range(w.reveal())
    # def _(i):
    #     Wn[i] =W[i]
    # wn.update(w.reveal())
    # @for_range(sln.reveal())
    # def _(i):
    #     # nonlocal Wn,wn
    #     Wn[wn] = sint(shortlist[i][0])
    #     wn.update(wn + 1)

    Wn = sint.Array(34)
    wn = regint(0)

    @for_range(w.reveal())
    def _(i):
        Wn[i] = W[i]

    wn.update(w.reveal())

    @for_range(sln.reveal())
    def _(i):
        Wn[wn] = sint(shortlist[i][0])
        wn.update(wn + 1)

    # @for_range(wn.reveal())
    # def _(i):
    #     print_ln('%s',Wn[i].reveal())
    return Wn, wn


global W
# W = SqrtOram(sint.Tensor([34, 1]))
W = sint.Array(34)
global w
w = sint(3)


def find(M, V, n, S_star, C_star, k):
    '''
    :param M: OMatrix APSP M[regint][regint]=sint
    :param V: V_index sint.Array
    :param n: vertex num regint
    :param S_star: optimal seed set sint.Array
    :param  C_star: centrality of optimal seed set sfix
    :param k: k regint
    :return: S+, C+
    '''

    # k=1
    # @for_range(n)
    # def _(i):
    #     S_=sint.Array(1)
    #     S_[0]=V[i]
    #     f,D,Dn=mssp(S_,sint(1),M,n,V)
    #     C_=centrality(Dn,f,k,n)
    #     C_star.update(C_.max(C_star))
    # print_ln('k=1,cen:%s',C_star.reveal())

    # k=2
    # @for_range(n-1)
    # def _(i):
    #     @for_range(i+1,n)
    #     def _(j):
    #         S_=sint.Array(2)
    #         S_[0]=V[i]
    #         S_[1]=V[j]
    #         f,D,Dn=mssp(S_,sint(2),M,n,V)
    #         C_=centrality(Dn,f,k,n)
    #         C_star.update(C_.max(C_star))
    # print_ln('k=2,cen%s',C_star.reveal())

    # k=3
    # init window

    k = 3

    @for_range(k)
    def _(i):
        W[i] = S_star[i]

    @while_do(lambda: w.less_than(n).reveal())
    def _():
        global W, w
        # print_ln('explore_before:W')

        # @for_range(w.reveal())
        # def _(i):
        #     global W
        #     print_ln('%s', W[i].reveal())

        print_ln('w:%s', w.reveal())
        pre_w = sint(0)
        pre_w.update(w)
        Wn, wn = next_window(W, w, S_star, sint(3), V, n, M)
        print_ln('next fini,wn:%s', wn.reveal())

        # z=regint(0)
        # @while_do(lambda:z<wn.reveal())
        # def _():
        #     print_ln('wn:%s:%s',z,Wn[z].reveal())
        #     z.update(z+1)
        @for_range(wn.reveal())
        def _(i):
            print_ln('%s', Wn[i].reveal())
            W[i] = Wn[i]

        w.update(wn)
        # print_ln('explore_after:W')

        # @for_range(w.reveal())
        # def _(i):
        #     print_ln('%s', W[i].reveal())
        #
        # print_ln('w:%s,pre_w:%s', w.reveal(), pre_w.reveal())
        print_ln('next window')

        # recursive to find precise

        @for_range(1, (w - k + 1).reveal())
        def _(a):
            print_ln('a:%s', a)
            # global w, pre_w
            Sa = sint.Array(1)
            Sa[0] = W[a]  # only one seed
            fa, Da, Dan = mssp(Sa, sint(1), M, n, V)
            b = regint(w.reveal() - 1)  # seconde seed

            @while_do(lambda: b >= a + 1)
            def _():
                # global b, w, fa, Da, Dan

                @if_(b > pre_w.reveal())
                def _():
                    print_ln('b:%s', b)
                    S = sint.Array(1)
                    S[0] = W[b]
                    Sb = Sa.concat(S)
                    # got {va,vb}
                    # level b up and down
                    del_up_b = sint(0)
                    del_down_b = sint(999)
                    fb, Db, Dbn, fs_ = del_mssp(Sb, sint(2), Sa, fa, Da, Dan, M, n, V)
                    alphab = regint(1)

                    @if_(centrality(Dbn + alphab * del_up_b, fb + alphab * del_down_b, k, n).reveal() > C_star.reveal())
                    def _():
                        c = regint(w.reveal())

                        @while_do(lambda: c > b + 1)
                        def _():
                            S_ = sint.Array(1)
                            S_[0] = W[c]
                            Sc = Sb.concat(S_)
                            fc, Dc, Dcn = mssp(Sc, sint(3), M, n, V)
                            C_ = centrality(fc, Dcn, k, n)

                            @if_(C_.reveal() > C_star.reveal())
                            def _():
                                C_star.update(C_)

                            c.update(c - 1)

                    del_up_b.update(del_up_b.max(Dbn - Dan))
                    del_down_b.update(del_down_b.min(fs_ - fa))

                b.update(b - 1)
    print_ln('k=3,cen:%s',C_star.reveal())

    a=sfix.Matrix(3,5)
    b=sfix.Matrix(5,5)
    a.mul(b)

    # k=4
    #
    # k = 4
    #
    # @for_range(k)
    # def _(i):
    #     W[i] = S_star[i]
    #
    # @while_do((lambda: w.less_than(n).reveal()))
    # def _():
    #     global W, w
    #     pre_w = sint(0)
    #     pre_w.update(w)
    #     Wn, wn = next_window(W, w, S_star, sint(4), V, n, M)
    #
    #     @for_range(wn.reveal())
    #     def _(i):
    #         W[i] = Wn[i]
    #
    #     w.update(wn)
    #
    #     @for_range(1, (w - k + 1).reveal())
    #     def _(a):
    #         Sa = sint.Array(1)
    #         Sa[0] = W[a]
    #         fa, Da, Dan = mssp(Sa, sint(1), M, n, V)
    #         b = regint(w.reveal() - 1)
    #
    #         @while_do(lambda: b >= a + 1)
    #         def _():
    #             @if_(b > pre_w.reveal())
    #             def _():
    #                 S = sint.Array(1)
    #                 S[0] = W[b]
    #                 Sb = Sa.concat(S)
    #                 del_up_b = sint(0)
    #                 del_down_b = sint(999)
    #                 fb, Db, Dbn, fsb_ = del_mssp(Sb, sint(2), Sa, fa, Da, Dan, M, n, V)
    #                 alphab = regint(2)
    #
    #                 @if_(centrality(Dbn + alphab * del_up_b, fb + alphab * del_down_b, k, n).reveal() > C_star.reveal())
    #                 def _():
    #                     c = regint(w.reveal() - 2)
    #
    #                     @while_do(lambda: c >= b + 1)
    #                     def _():
    #                         @if_(c > pre_w.reveal())
    #                         def _():
    #                             S = sint.Array(1)
    #                             S[0] = W[c]
    #                             Sc = Sb.concat(S)
    #                             del_up_c = sint(0)
    #                             del_down_c = sint(999)
    #                             fc, Dc, Dcn, fsc_ = del_mssp(Sc, sint(3), Sb, fb, Db, Dbn, M, n, V)
    #                             alphac = regint(1)
    #
    #                             @if_(centrality(Dcn + alphac * del_up_c, fc + alphac * del_down_c, k,
    #                                             n).reveal() > C_star.reveal())
    #                             def _():
    #                                 d = regint(w.reveal() - 3)
    #
    #                                 @while_do(lambda: d >= c + 1)
    #                                 def _():
    #                                     S_ = sint.Array(1)
    #                                     S_[0] = W[d]
    #                                     Sd = Sc.concat(S_)
    #                                     fd, Dd, Ddn = mssp(Sd, sint(4), M, n, V)
    #                                     C_ = centrality(fd, Ddn, k, n)
    #
    #                                     @if_(C_.reveal() > C_star.reveal())
    #                                     def _():
    #                                         C_star.update(C_)
    #
    #                                     d.update(d - 1)
    #
    #                             del_up_c.update(del_up_c.max(Dcn - Dbn))
    #                             del_down_c.update(del_down_c.min(fsc_ - fb))
    #
    #                         c.update(c - 1)
    #
    #                 del_up_b.update(del_up_b.max(Dbn - Dan))
    #                 del_down_b.update(del_down_b.min(fsb_ - fa))
    #
    #             b.update(b - 1)
    #
    # print_ln('k=4 cen:%s', C_star.reveal())


    #k=5

    # k=5
    # @for_range(k)
    # def _(i):
    #     W[i]=S_star[i]
    #
    # @while_do(lambda: w.less_than(n).reveal())
    # def _():
    #     global W,w
    #
    #     pre_w=sint(0)
    #     pre_w.update(w)
    #     Wn,wn=next_window(W,w,S_star,sint(5),V,n,M)
    #
    #     @for_range(wn.reveal())
    #     def _(i):
    #         W[i]=Wn[i]
    #     w.update(wn)
    #
    #     @for_range(1,(w-k+1).reveal())
    #     def _(a):
    #         Sa=sint.Array(1)
    #         Sa[0]=W[a]
    #         fa,Da,Dan=mssp(Sa,sint(1),M,n,V)
    #         b=regint(w.reveal()-1)
    #
    #         @while_do(lambda:b>=a+1)
    #         def _():
    #             @if_(b>pre_w.reveal())
    #             def _():
    #                 S=sint.Array(1)
    #                 S[0]=W[b]
    #                 Sb=Sa.concat(S)
    #                 del_up_b=sint(0)
    #                 del_down_b=sint(999)
    #                 fb,Db,Dbn,fsb_=del_mssp(Sb,sint(2),Sa,fa,Da,Dan,M,n,V)
    #                 alphab=regint(3)
    #
    #                 @if_(centrality(Dbn+alphab*del_up_b,fb+alphab*del_down_b,k,n).reveal()>C_star.reveal())
    #                 def _():
    #                     c=regint(w.reveal()-2)
    #
    #                     @while_do(lambda:c>=b+1)
    #                     def _():
    #                         @if_(c>pre_w.reveal())
    #                         def _():
    #                             S=sint.Array(1)
    #                             S[0]=W[c]
    #                             Sc=Sb.concat(S)
    #                             del_up_c=sint(0)
    #                             del_down_c=sint(999)
    #                             fc,Dc,Dcn,fsc_=del_mssp(Sc,sint(3),Sb,fb,Db,Dbn,M,n,V)
    #                             alphac=regint(2)
    #
    #                             @if_(centrality(Dcn+alphac*del_up_c,fc+alphac*del_down_c,k,n).reveal()>C_star.reveal())
    #                             def _():
    #                                 d=regint(w.reveal()-3)
    #
    #                                 @while_do(lambda:d>=c+1)
    #                                 def _():
    #                                     S=sint.Array(1)
    #                                     S[0]=W[d]
    #                                     Sd=Sc.concat(S)
    #                                     del_up_d=sint(0)
    #                                     del_down_d=sint(999)
    #                                     fd,Dd,Ddn,fsd_=del_mssp(Sd,sint(4,Sc,fc,Dc,Dcn,M,n,V))
    #                                     alphad=regint(1)
    #                                     @if_(centrality(Ddn+alphad*del_up_d,fd+alphad*del_down_d,k,n).reveal()>C_star.reveal())
    #                                     def _():
    #                                         e=regint(w.reveal()-4)
    #
    #                                         @while_do(lambda:e>=d+1)
    #                                         def _():
    #                                             S_=sint.Array(1)
    #                                             S_[0]=W[e]
    #                                             Se=Sd.concat(S_)
    #                                             fe,De,Den=mssp(Se,sint(5),M,n,V)
    #                                             C_=centrality(fe,Den,k,n)
    #
    #                                             @if_(C_.reveal()>C_star.reveal())
    #                                             def _():
    #                                                 C_star.update(C_)
    #
    #                                             e.update(e-1)
    #                                     del_up_d.update(del_up_c.max(Ddn-Dcn))
    #                                     del_down_d.update(del_down_d.min(fsd_-fc))
    #                                     d.update(d-1)
    #                             del_up_c.update(del_up_c.max(Dcn-Dbn))
    #                             del_down_c.update(del_down_c.min(fsc_-fb))
    #                         c.update(c-1)
    #                 del_up_b.update(del_up_b.max(Dbn-Dan))
    #                 del_down_b.update(del_down_b.min(fsb_-fa))
    #             b.update(b-1)
    #
    # print_ln('k=5 cen=%s',C_star.reveal())

