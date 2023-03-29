from specklepy.objects.geometry import Mesh
from trimesh.primitives import Sphere as trimesh_sphere

class Sphere():

    def Create(radius, center):
                 
            sphere = trimesh_sphere(radius = radius, center = center)
            
            vertices = [item for sublist in sphere.vertices for item in sublist]

            faces = []
            for face in sphere.faces:
                faces.append(3)
                for vertex in face:
                    faces.append(int(vertex))

            return Mesh.create(vertices, faces)