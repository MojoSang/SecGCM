# 导入 MP-SPDZ 库
from Compiler.library import *
from oram import OptimalORAM
from Compiler.types import sfix, sint, Array


'''
# Dijkstra算法函数，接收节点数量n、边集edges和源点source作为输入，返回各节点的最短路径数组
def dijkstra(n, m, edges, source):
    INF = 999999  # 用一个较大的数表示无穷大

    # 初始化距离数组和访问状态数组，所有的节点距离初始为无穷大
    dist = OptimalORAM(n)
    visited = OptimalORAM(n)
    for i in range(n):
        dist[i] = sint(INF)
        visited[i] = sint(0)

    # 根据指定的源点设置距离，源点到自身的距离为0
    dist[source] = sfix(0)

    # Dijkstra算法的主体
    for _ in range(n):
        # 寻找未访问的节点中距离最近的节点
        u = -1
        min_dist = sint(INF)
        for i in range(n):
            cond = (visited[i] == sint(0)) & (dist[i] < min_dist)
            u = sint.if_else(cond, i, u)
            min_dist = sint.if_else(cond, dist[i], min_dist)

        # 标记该节点为已访问
        visited[u] = sint(1)

        # 遍历所有边，更新距离
        for i in range(m):
            u_edge = edges[i][0]
            v_edge = edges[i][1]
            weight = edges[i][2]

            # 判断边的起点是否是 u，且终点是否未访问
            cond = (u_edge == u) & (visited[v_edge] == sint(0))
            new_dist = dist[u_edge] + weight
            update_cond = cond & (new_dist < dist[v_edge])
            dist[v_edge] = sint.if_else(update_cond, new_dist, dist[v_edge])

    # 返回所有节点的最短距离
    return dist
'''

# Dijkstra算法函数，接收节点数量n、边集edges和源点source作为输入，返回各节点的最短路径数组
def dijkstra(n, m, edges, source):
    INF = 999999  # 设置为一个较大的整数来表示无穷大

    # 初始化距离数组和访问状态数组，所有的节点距离初始为无穷大
    dist = Array(n, sint)
    visited = Array(n, sint)
    for i in range(n):
        dist[i] = sint(INF)
        visited[i] = sint(0)

    # 根据指定的源点设置距离，源点到自身的距离为0
    dist[source] = sint(0)

    # Dijkstra算法的主体
    for _ in range(n):
        # 寻找未访问的节点中距离最近的节点
        u = sint(-1)
        min_dist = sint(INF)
        for i in range(n):
            # 使用加密域中的条件选择来更新最小距离
            cond = (visited[i] == sint(0)) & (dist[i] < min_dist)
            u = sint.if_else(cond, i, u)
            min_dist = sint.if_else(cond, dist[i], min_dist)

        # 标记该节点为已访问
        visited[u.reveal()] = sint(1)

        # 遍历所有边，更新距离
        for i in range(m):
            u_edge = edges[i][0].reveal()
            v_edge = edges[i][1].reveal()
            weight = edges[i][2]

            # 判断边的起点是否是 u，且终点是否未访问
            cond = (u_edge == u) & (visited[v_edge] == sint(0))
            new_dist = dist[u_edge] + weight
            update_cond = cond & (new_dist < dist[v_edge])

            # 通过sint.if_else来更新sint类型的dist值
            dist[v_edge] = sint.if_else(update_cond, new_dist, dist[v_edge])

    # 返回所有节点的最短距离
    return dist
