import bpy 
import numpy as np
import math 
import random
import string
import datetime
from mathutils import Vector

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 160

start = datetime.datetime.now()
k = 0
num_centers = 3
colours = [np.random.uniform(.1, 1, 3) for i in range(num_centers)]
for i in range(len(colours)):
    colours[i] = np.append(colours[i], 1)
print(colours)

def get_data(num_centers, num_points):
    
    obs = []
    loc = [i for i in range(1, math.ceil((1.5 * num_centers)))]
    mu = [random.choice(loc)]; loc.remove(mu[0])
    sigma = np.random.uniform(.25, .85, 1)
    blobs = np.random.normal(mu[0], sigma, (3, num_points)) 
    for i in range(1, num_centers):
        mu.append(random.choice(loc)); loc.remove(mu[i])
        sigma = np.random.uniform(.25, .85, 1)
        blobs0 = np.random.normal(mu[i], sigma, (3, num_points))
        blobs = np.concatenate((blobs, blobs0), axis=1)

    for j, i in enumerate(zip(*blobs)):
        if j == 0:
            
            bpy.ops.mesh.primitive_cube_add(size=1.2, 
                                                  location=i, 
                                                  scale=(.1, .1, .1))  
            ob = bpy.context.object
            
        else:
            copy = ob.copy()
            copy.location = Vector(i)
            copy.data = copy.data.copy() # also duplicate mesh, remove for linked duplicate
            obs.append(copy)
            
    for ob in obs:
        bpy.context.collection.objects.link(ob)

    dg = bpy.context.evaluated_depsgraph_get() 
    dg.update()        
    return blobs

def distance(data, centers):
    return np.sqrt(np.sum((data-centers)**2, axis=1))

def set_material(ob, mat):
    me = ob.data
    me.materials.append(mat)

def separate(distances, data):
    global colours, k
    
    ds = [[] for i in range(len(distances))]
    for j, i in enumerate(zip(*distances)):
        idx = np.argmin(i)
        ds[idx].append(data.T[j])
        
    dss = np.array([np.array(j) for j in ds])
    new_centers = [i.mean(axis=0) for i in dss] # thats what i mean
    selected_colors = []
    selected_names = []  
    colors = [np.random.uniform(.1, 1, 4) for i in range(num_centers)]
    material_names = string.ascii_letters  
    
    print(len(bpy.context.scene.objects))
    
    print(type(random.choice(colors)))
    
    for j, i in enumerate(bpy.context.scene.objects):
        j %= (len(colours))
        if len(bpy.context.scene.objects) != len(selected_names):
            mat_names = random.sample(material_names, 3)
            mat_names = ''.join(mat_names)
            mat = bpy.data.materials.new(mat_names)
            mat.diffuse_color = colours[j]
            mat.keyframe_ingirtsert(data_path='diffuse_color', frame=k*30)
            
            if mat.diffuse_color[:] not in selected_colors:
                selected_colors.append(mat.diffuse_color[:])
                
            
            if i.name.startswith("Cube") and len(i.data.materials) == 0:
                set_material(i, mat)
            if i.name.startswith("Suzanne") and len(i.data.materials) == 0:
                suzannesburger = bpy.data.materials.get("suzannesburger")
                if suzannesburger is not None:
                    suzannesburger = bpy.data.materials.new("suzannesburger")
                    suzannesburger.diffuse_color((0.,0.,0.,1.))
                i.data.materials.append(suzannesburger)
    print(selected_colors) 

    for i in range(len(dss)):
        if len(dss[i]) != 0: 
            e = np.around(dss[i], decimals=4)  
            for j in bpy.context.scene.objects:
                locs = np.around(np.array(j.location[:]), decimals=4)
                if locs in e:
                    names = bpy.data.objects[str(j.name)].active_material.name
                    mat = bpy.data.materials.get(names)
                    mat.diffuse_color = selected_colors[i]
                    mat.keyframe_insert(data_path='diffuse_color', frame=k*30)
                
                
                #print(e, j, locs)
    k += 1         
    return np.array(dss), new_centers

def fit(num_centers, num_points, iterations=20):
    
    data = get_data(num_centers, num_points)
    centers = np.array([np.random.uniform(data.min(),data.max(), 3) 
                        for i in range(num_centers)])
    
    for i in centers:
        bpy.ops.mesh.primitive_monkey_add(size=.2, location=i, scale=(1.2, 1.2, 1.2))

    for k in range(iterations):
        distances = [distance(data.T, i) for i in centers]
        separated, centers = separate(distances, data)
    
        suzannes = [ob for ob in scene.objects if ob.name[:7] == "Suzanne"]
        for f, suzanne in enumerate(suzannes):
            #bpy.ops.transform.translate(value=centers[f])
            suzanne.location = centers[f]
            suzanne.keyframe_insert(data_path='location', frame=k*30)
            
fit(num_centers, 42, 5) # this is the main function call
end = datetime.datetime.now()
print(end - start)

