def init_prism(face_to_extrude,axis_to_extrude,start,end):
    # parse arguments
    try:
        face_to_extrude = face_to_extrude.rstrip(";").split(";")
        face = list(list(float(s) for s in t.split(",") + [0,0]) for t in face_to_extrude)
        if face[0]!=face[-1]:
            raise Exception("prism: first and last vertex of face_to_extrude must coincide")
        face = face[0:-1]
        if axis_to_extrude not in ["x","y","z"]:
            raise Exception("prism: invalid axis to extrude")
        axis_to_extrude = ["x","y","z"].index(axis_to_extrude)
        start = float(start)
        end = float(end)
    except Exception as e:
        raise Exception("prism: error parsing arguments: %s" % (str(e)))
    face_axis = [0,1,2]
    face_axis.remove(axis_to_extrude)
    coords = [None]*3
    coords[face_axis[0]] = list(face[t][0] for t in range(len(face)))
    coords[face_axis[1]] = list(face[t][1] for t in range(len(face)))
    volume = {}
    volume["axis_to_extrude"] = axis_to_extrude
    volume["max_%d"%(axis_to_extrude)] = max(start,end)
    volume["min_%d"%(axis_to_extrude)] = min(start,end)
    for i in face_axis:
        volume["max_%d"%(i)] = max(coords[i])
        volume["min_%d"%(i)] = min(coords[i])
    volume["face"] = face
    # volume["face"][i][0]: face_axis[0] coordinate of side i
    # volume["face"][i][1]: face_axis[1] coordinate of side i
    # volume["face"][i][2]: face_axis[0] coordinate of side i-1 - face_axis[0] coord of side i
    # volume["face"][i][3]: face_axis[1] coordinate of side i-1 - face_axis[1] coord of side i
    volume["sides"] = range(len(volume["face"]))
    for i in volume["sides"]:
        j = volume["sides"][i-1]
        volume["face"][i][2]=volume["face"][j][0]-volume["face"][i][0]
        volume["face"][i][3]=volume["face"][j][1]-volume["face"][i][1]
    return volume

def prism(volume,errors,point):
    "Determine if *point* is inside the volume of the prism result of the extrusion of *face_to_extrude* from z_start to z_end. *face_to_extrude* is a semi-colon separated list of 2D coordinates, each of them comma-separated. *point* is a comma-separated list of the 3D coordinates of the point to probe."
    # parse arguments
    if (type(point) is not list and type(point) is not tuple) or len(point)!=3:
        raise Exception("prism: point must be a list or tuple of three floats")
    # fast solving of points outside bounding box
    if point[0]>volume["max_0"] or point[0]<volume["min_0"] or \
       point[1]>volume["max_1"] or point[1]<volume["min_1"] or \
       point[2]>volume["max_2"] or point[2]<volume["min_2"]:
        return False
    cpoint = list(point)
    del cpoint[volume["axis_to_extrude"]]
    intersect = False
    for i in volume["sides"]:
        j = volume["sides"][i-1]
        dy=cpoint[1]-volume["face"][i][1]
        if (abs(volume["face"][i][2])<errors[0] and abs(volume["face"][j][0]-cpoint[0])<errors[0]) and min(volume["face"][i][1],volume["face"][j][1])<=cpoint[1]<=max(volume["face"][i][1],volume["face"][j][1]):
            return 1,"%f %f %f"%(point[0],point[1],point[2])
        if (abs(volume["face"][i][3])<errors[1] and abs(dy)<errors[1]) and min(volume["face"][i][0],volume["face"][j][0])<=cpoint[0]<=max(volume["face"][i][0],volume["face"][j][0]):
            return 1,"%f %f %f"%(point[0],point[1],point[2])
        if (((volume["face"][i][1]>cpoint[1]) != (volume["face"][j][1]>cpoint[1])) and \
            (cpoint[0] < volume["face"][i][2]/volume["face"][i][3]*dy + volume["face"][i][0])):
           intersect = not intersect
    return intersect
