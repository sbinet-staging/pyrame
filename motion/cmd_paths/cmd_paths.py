#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# 
# Copyright 2012-2015 Frédéric Magniette, Miguel Rubio-Roy
# This file is part of Pyrame.
# 
# Pyrame is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Pyrame is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with Pyrame.  If not, see <http://www.gnu.org/licenses/>

import pools, getapi
import heapq

paths_pool=pools.pool()
volume_pool=pools.pool()
matrix_pool=pools.pool()

def check_param(param,valid_list,default_param,map_func,unique=True):
    if param=="undef" or param=="":
        param = default_param
    if len(param)!=len(default_param) or any(c not in valid_list for c in param):
        return 0,"invalid param"
    result = map(map_func,param)
    if unique and len(set(result))!=len(result):
        return 0,"repeated characters"
    return 1,result

# first neighbors of point p
def neighbors(paths,p,order):
    # example for order=1,2,3
    #results = [(x+dx,y,z),(x-dx,y,z),(x,y+dy,z),(x,y-dy,z),(x,y,z+dz),(x,y,z-dz)]
    r = paths["r"]
    results = [None]*6
    for i in [0,1,2]:
        e = 2*i
        a = order[i]-1
        k = list(p)
        k[a] = round((k[a] + r[a])/r[a])*r[a]
        results[e] = tuple(k)
        k = list(p)
        k[a] = round((k[a] - r[a])/r[a])*r[a]
        results[e+1] = tuple(k)
    results = filter(lambda x: x[0]<=paths["maxs"][0] and x[0]>=paths["mins"][0], results)
    results = filter(lambda x: x[1]<=paths["maxs"][1] and x[1]>=paths["mins"][1], results)
    results = filter(lambda x: x[2]<=paths["maxs"][2] and x[2]>=paths["mins"][2], results)
    # make error half of the resolution
    errors = map(lambda x: x/2,r)
    # check forbidden volumes
    for forb_vol in paths["forbidden"]:
        results = filter(lambda x: not forb_vol["func"](forb_vol,errors,x), results)
    return results

# cost from current to next is the distance in the axis that changes
def cost(c,n,r,order):
    for i,j,k in [[1,2,0],[0,2,1],[0,1,2]]:
        if c[i]==n[i] and c[j]==n[j]:
            return r[k]

# check if to points are the same to a certain resolution *r*
def eq_point(p1,p2,e):
    return all((abs(p1[0]-p2[0])<e[0],abs(p1[1]-p2[1])<e[1],abs(p1[2]-p2[2])<e[2]))

def search_path(paths,start,goal,order):
    # A* algorithm
    start = tuple(start)
    goal = tuple(goal)
    if start==goal:
        return []
    # make error half of the resolution
    errors = map(lambda x: x/2,paths["r"])
    # if goal and start differ only in one coordinate, return direct path
    for i,j,k in [[1,2,0],[0,2,1],[0,1,2]]:
        if start[i]==goal[i] and start[j]==goal[j]:
            direct_path = True
            step = 1 if goal[k]>start[k] else -1
            for n in range(step,step+int((goal[k]-start[k])/paths["r"][k]),step):
                for forb_vol in paths["forbidden"]:
                    point = list(start)
                    point[k] += n*paths["r"][k]
                    if forb_vol["func"](forb_vol,errors,point):
                        direct_path = False
                        break
                if not direct_path:
                    break
            if direct_path:
                return [start,goal]
    frontier = []
    heapq.heappush(frontier,(0,start))
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0
    while len(frontier):
        current = heapq.heappop(frontier)[1]
        # current == goal ?
        if eq_point(current,goal,errors):
            break
        for next in neighbors(paths,current,order):
            new_cost = cost_so_far[current] + cost(current,next,paths["r"],order)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                heuristic = abs(goal[0]-next[0]) + abs(goal[1]-next[1]) + abs(goal[2]-next[2])
                priority = new_cost + heuristic
                heapq.heappush(frontier,(priority,next))
                cost_so_far[next] = new_cost
                came_from[next] = current
    if goal not in came_from:
        raise Exception("No valid path was found")
    path = [goal,came_from[goal]]
    while path[-1]!=start:
        path.append(came_from[path[-1]])
        for i,j in [[1,2],[0,2],[0,1]]:
            if path[-3][i]==path[-2][i]==path[-1][i] and path[-3][j]==path[-2][j]==path[-1][j]:
                del path[-2]
                break
    print path[::-1]
    return path[::-1]

def init_paths(motion_id,r1,r2,r3):
    "Initialize paths space with id of motion system *motion_id* and minimal steps for each axis *rn*"
    r = map(float,[r1,r2,r3])
    paths_id = paths_pool.new({"r": r, "motion_id": motion_id})
    submod.setres(1,paths_id)

def deinit_paths(paths_id):
    "Deinitialize paths space"
    try:
        paths = paths_pool.get(paths_id)
    except Exception as e:
        submod.setres(1,"paths: paths_%s"%(str(e)))
        return
    matrix_list = []
    for _,matrix in matrix_pool.get_all():
        if matrix["paths_id"]==paths_id:
            matrix_list.append(matrix["id"])
    for matrix_id in matrix_list:
        matrix_pool.remove(matrix_id)
    volume_list = []
    for _,volume in volume_pool.get_all():
        if volume["paths_id"]==paths_id:
            volume_list.append(volume["id"])
    for volume_id in volume_list:
        volume_pool.remove(volume_id)
    paths_pool.remove(paths_id)
    submod.setres(1,"ok")

def add_limits_paths(paths_id,volume_id):
    "Add *volume_id* to the forbidden regions of space"
    try:
        paths = paths_pool.get(paths_id)
    except Exception as e:
        submod.setres(0,"paths: paths_%s"%(str(e)))
        return
    try:
        volume = volume_pool.get(volume_id)
    except Exception as e:
        submod.setres(0,"paths: volume_%s"%(str(e)))
        return
    if "forbidden" not in paths:
        paths["forbidden"] = []
    paths["forbidden"].append(volume)
    submod.setres(1,"ok")

def get_pos(paths):
    retcode,res = submod.execcmd("get_pos_motion",paths["motion_id"])
    if retcode==0:
        return 0,"error getting position <- %s"%(res)
    return 1,map(float,res.split(","))

def move(paths_id,d,s,a,strategy="undef"):
    try:
        paths = paths_pool.get(paths_id)
    except Exception as e:
        return 0,"paths_%s"%(str(e))
    retcode,order = check_param(strategy,["1","2","3"],"123",int)
    if retcode==0:
        return 0,"invalid strategy: %s" % (order)
    # check if d is multiple of r
    for i in order:
        d[i-1] = float(d[i-1])
        m = d[i-1]/paths["r"][i-1]
        if abs(m-round(m))>1e-12:
            return 0,"destination must be multiple of the minimum step %f (axis %d)"%(paths["r"][i-1],i)
    # check if we are trying to go to a forbidden point
    forbidden = False
    if "forbidden" in paths:
        # make error half of the resolution
        errors = map(lambda x: x/2,paths["r"])
        for forb_vol in paths["forbidden"]:
            try:
                forbidden = forb_vol["func"](forb_vol,errors,d)
            except Exception as e:
                return 0,"Error while checking point in forbidden volume: %s"%(str(e))
            if forbidden:
                break
    if forbidden:
        return 0,"destination out of limits"
    # get current position
    _,c = get_pos(paths)
    # round c to the closest node
    for i in order:
        c[i-1] = round(c[i-1]/paths["r"][i-1])*paths["r"][i-1]
    if "forbidden" in paths:
        # search safe path surrounding forbidden regions
        try:
            safe_path = search_path(paths,c,d,order)
        except Exception as e:
            return 0,"error searching path: %s"%(str(e))
    else:
        safe_path = [d]
    for step in safe_path:
        step = map(str,step)
        retcode,res = submod.execcmd("move_motion",paths["motion_id"],step[0],step[1],step[2],s[0],s[1],s[2],a[0],a[1],a[2],"".join(map(str,order)))
        if retcode==0:
            return 0,"error moving <- %s"%(res)
    return 1,"ok"

def move_paths(paths_id,d1,d2,d3,s1,s2,s3,a1,a2,a3,strategy="undef"):
    "Move on *paths_id* space to *dn* destination at *sn* speed, with *an* acceleration (for n=1,2,3). strategy is the preferential order of axis movement (e.g. 213 to move first axis 2, then axis 1 finally axis 3)"
    d = [d1,d2,d3]
    s = [s1,s2,s3]
    a = [a1,a2,a3]
    retcode,res = move(paths_id,d,s,a,strategy)
    if retcode==0:
        submod.setres(0,"paths: %s"%(res))
        return
    submod.setres(1,"ok")

def init_volume_paths(paths_id,module,function,*params):
    "Create volume by specifying the Python module and function that will determine inside/outside of volume"
    try:
        paths = paths_pool.get(paths_id)
    except Exception as e:
        submod.setres(0,"paths: paths_%s"%(str(e)))
        return
    try:
        module = __import__(module)
        init_func = getattr(module,"init_"+function)
        func = getattr(module,function)
    except Exception as e:
        submod.setres(0,"paths: Error loading module and function: %s"%(str(e)))
        return
    try:
        volume = init_func(*params)
    except Exception as e:
        submod.setres(0,"paths: Error initializing volume: %s"%(str(e)))
        return
    volume["paths_id"] = paths_id
    volume["func"] = func
    volume_id = volume_pool.new(volume)
    submod.setres(1,volume_id)

def deinit_volume_paths(volume_id):
    "Deinitialize *volume_id*"
    try:
        volume = volume_pool.remove(volume_id)
    except Exception as e:
        submod.setres(1,"paths: volume_%s"%(str(e)))
        return
    submod.setres(1,"ok")

def init_matrix_paths(paths_id,volume_id,p1d,p2d,p3d,order,path_type,directions):
    """Create matrix path to scan volume *volume_id* with *pnd* steps (for n=1,2,3). The matrix is associated to *paths_id*

    *order* is a three character string. Its first character is the number of the fastest axis, and the third one is the slowest.
    
    *path_type* is a two character string indicating: the type of scan ('r' for raster, 'm' for meander) of the fastest and middle axis (first character), and middle and slowest axis (second character).
    
    *directions* is a three character string with either 'p' or 'n' for positive or negative for the fastest, middle and slowest axis."""
    try:
        paths = paths_pool.get(paths_id)
    except Exception as e:
        submod.setres(0,"paths: paths_%s"%(str(e)))
        return
    if "r" not in paths:
        submod.setres(0,"paths: not configured")
        return
    retcode,res = submod.execcmd("get_limits_motion",paths["motion_id"])
    if retcode==0:
        submod.setres(0,"Error getting motion system limits <- %s"%(res))
        return
    paths["maxs"] = map(float,res.split(";")[0].split(","))
    paths["mins"] = map(float,res.split(";")[1].split(","))
    matrix = {"paths_id": paths_id}
    try:
        volume = volume_pool.get(volume_id)
    except Exception as e:
        submod.setres(0,"paths: volume_%s"%(str(e)))
        return
    matrix["volume_id"] = volume_id
    pd = [float(p1d),float(p2d),float(p3d)]
    for i in [1,2,3]:
        print i
        if abs(pd[i-1]/paths["r"][i-1] - round(pd[i-1]/paths["r"][i-1]))>1e-12:
            print pd[i-1]/paths["r"][i-1],round(pd[i-1]/paths["r"][i-1])
            print abs(pd[i-1]/paths["r"][i-1] - round(pd[i-1]/paths["r"][i-1]))
            submod.setres(0,"paths: p%dd must be multiple of the minimum step for axis %d (%.2e)"%(i,i,paths["r"][i-1]))
            return
    retcode,order = check_param(order,["1","2","3"],"123",lambda x: str(int(x)-1))
    if retcode==0:
        submod.setres(0,"paths: invalid order: %s" % (order))
        return
    retcode,path_type = check_param(path_type,["r","m"],"rr",lambda x: 0 if x=="r" else 1,False)
    if retcode==0:
        submod.setres(0,"paths: invalid path_type: %s" % (path_type))
        return
    retcode,directions = check_param(directions,["p","n"],"ppp",lambda x: 1 if x=="p" else -1,False)
    if retcode==0:
        submod.setres(0,"paths: invalid directions: %s" % (directions))
        return
    ff = volume[("max" if directions[0]==1 else "min") + "_" + order[0]]
    fi = volume[("min" if directions[0]==1 else "max") + "_" + order[0]]
    fd = pd[int(order[0])]*directions[0]
    mf = volume[("max" if directions[1]==1 else "min") + "_" + order[1]]
    mi = volume[("min" if directions[1]==1 else "max") + "_" + order[1]]
    md = pd[int(order[1])]*directions[1]
    sf = volume[("max" if directions[2]==1 else "min") + "_" + order[2]]
    si = volume[("min" if directions[2]==1 else "max") + "_" + order[2]]
    sd = pd[int(order[2])]*directions[2]
    # make error half of the resolution
    errors = map(lambda x: x/2,paths["r"])
    matrix["points"] = []
    mc = 0
    fc = 0
    # slowest axis
    for s in range(abs(int((sf-si)/sd))+1):
        # middle axis
        for m in range(abs(int((mf-mi)/md))+1)[::1 - 2 * (mc&1) * path_type[1]]:
            # fastest axis
            for f in range(abs(int((ff-fi)/fd))+1)[::1 - 2 * (fc&1) * path_type[0]]:
                point = [None]*3
                point[int(order[0])]=fi+f*fd
                point[int(order[1])]=mi+m*md
                point[int(order[2])]=si+s*sd
                forbidden = False
                if point[0]>paths["maxs"][0] or point[0]<paths["mins"][0] or \
                   point[1]>paths["maxs"][1] or point[1]<paths["mins"][1] or \
                   point[2]>paths["maxs"][2] or point[2]<paths["mins"][2]:
                    forbidden = True
                elif "forbidden" in paths:
                    for forb_vol in paths["forbidden"]:
                        try:
                            forbidden = forb_vol["func"](forb_vol,errors,point)
                        except Exception as e:
                            submod.setres(0,"paths: Error while checking point in forbidden volume: %s"%(str(e)))
                            return
                        if forbidden:
                            break
                if forbidden:
                    continue
                try:
                    to_probe = volume["func"](volume,errors,point)
                except Exception as e:
                    submod.setres(0,"paths: Error while checking point in volume: %s"%(str(e)))
                    return
                if to_probe:
                    matrix["points"].append(point)
            fc += 1
        mc += 1
    if len(matrix["points"])==0:
        submod.setres(0,"paths: No points in matrix")
        return
    matrix["current"] = -1
    matrix_id = matrix_pool.new(matrix)
    submod.setres(1,matrix_id)

def deinit_matrix_paths(matrix_id):
    "Deinitialize *matrix_id*"
    try:
        matrix = matrix_pool.remove(matrix_id)
    except Exception as e:
        submod.setres(1,"paths: matrix_%s"%(str(e)))
        return
    submod.setres(1,"ok")

def get_matrix_paths(matrix_id):
    "Returns the path (sequence of 3D points) described by *matrix_id*"
    try:
        matrix = matrix_pool.get(matrix_id)
    except Exception as e:
        submod.setres(0,"paths: matrix_%s"%(str(e)))
        return
    res = ";".join(map(lambda x: ",".join(map(str,x)),matrix["points"]))
    submod.setres(1,res)

def next_matrix_paths(matrix_id,s1,s2,s3,a1,a2,a3,strategy="undef"):
    "Go to next point in matrix. The first time after initialization of the matrix, next goes to the first point. It moves with speed *sn* and acceleration *an* (for axis number n: 1,2,3)"
    try:
        matrix = matrix_pool.get(matrix_id)
    except Exception as e:
        submod.setres(0,"paths: matrix_%s"%(str(e)))
        return
    d = matrix["points"][matrix["current"]+1]
    s = [s1,s2,s3]
    a = [a1,a2,a3]
    retcode,res = move(matrix["paths_id"],d,s,a,strategy)
    if retcode==0:
        submod.setres(0,"paths: %s"%(res))
        return
    matrix["current"] += 1
    if matrix["current"]+1==len(matrix["points"]):
        matrix["current"] = -1
        submod.setres(1,"finished")
    else:
        submod.setres(1,"ok")

def reset_matrix_paths(matrix_id):
    "Reset matrix current position. Next call to next_matrix_paths will go to the first point in the matrix."
    try:
        matrix = matrix_pool.get(matrix_id)
    except Exception as e:
        submod.setres(0,"paths: matrix_%s"%(str(e)))
        return
    matrix["current"] = -1
    submod.setres(1,"ok")
