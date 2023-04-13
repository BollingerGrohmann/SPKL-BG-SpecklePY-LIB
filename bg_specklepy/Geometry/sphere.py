from specklepy.objects.geometry import Mesh
from trimesh.primitives import Sphere as trimesh_sphere

class Sphere():

    '''
    A general placeholder for methods pertaining to a sphere object.
    '''

    def create(radius: float  = 1,
               center: list = [0, 0, 0]):
            
        '''
        Appropriately formatted sphere mesh for speckle_py.

        Args:
            radius (float): Radius of sphere (given in m).
            center (list): Center of sphere [x, y, z](given in m).

        Returns:
            speckle.objects.geometry.Mesh: A speckle mesh object.
        '''

        sphere = trimesh_sphere(radius = radius, center = center)

        vertices = [item for sublist in sphere.vertices for item in sublist]

        faces = []
        for face in sphere.faces:
            faces.append(3)
            for vertex in face:
                faces.append(int(vertex))

        return Mesh.create(vertices, faces)
    