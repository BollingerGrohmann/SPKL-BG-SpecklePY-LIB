import os
import sys
import specklepy

root_folder = os.path.abspath(os.path.join(os.path.dirname(__file__),os.pardir))
sys.path.append(root_folder)

from bg_specklepy.Geometry.sphere import Sphere

def test_geometry_sphere():

    sphere = Sphere.create()

    assert isinstance(sphere, specklepy.objects.geometry.Mesh)
