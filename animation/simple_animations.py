import numpy as np
import itertools as it

from helpers import *

from animation import Animation
from meta_animations import DelayByOrder
from transform import Transform


class Rotating(Animation):
    DEFAULT_CONFIG = {
        "axes"       : [RIGHT, UP],
        "axis"       : None,
        "radians"    : 2*np.pi,
        "run_time"   : 20.0,
        "rate_func" : None,
        "in_place"   : True,
    }
    def update_mobject(self, alpha):
        axes = [self.axis] if self.axis is not None else self.axes
        families = [
            self.mobject.submobject_family(),
            self.starting_mobject.submobject_family()
        ]
        for mob, start in zip(*families):
            mob.points = np.array(start.points)
        if self.in_place:
            method = self.mobject.rotate_in_place
        else:
            method = self.mobject.rotate           
        method(alpha*self.radians, axes = axes)      


class FadeOut(Animation):
    def update_mobject(self, alpha):
        self.mobject.rgbs = self.starting_mobject.rgbs * (1 - alpha)

class FadeIn(Animation):
    def update_mobject(self, alpha):
        self.mobject.rgbs = self.starting_mobject.rgbs * alpha
        if self.mobject.points.shape != self.starting_mobject.points.shape:
            self.mobject.points = self.starting_mobject.points
            #TODO, Why do you need to do this? Shouldn't points always align?

class ShimmerIn(DelayByOrder):
    def __init__(self, mobject, **kwargs):
        mobject.sort_points(lambda p : np.dot(p, DOWN+RIGHT))
        DelayByOrder.__init__(self, FadeIn(mobject, **kwargs))


class ShowCreation(Animation):
    def update_mobject(self, alpha):
        pairs = zip(
            self.starting_mobject.submobject_family(),
            self.mobject.submobject_family()
        )
        for start, mob in pairs:
            new_num_points = int(alpha * start.get_num_points())
            for attr in mob.get_array_attrs():
                full_array = getattr(start, attr)
                partial_array = full_array[:new_num_points]
                setattr(mob, attr, partial_array)


class Flash(Animation):
    DEFAULT_CONFIG = {
        "color" : "white",
        "slow_factor" : 0.01,
        "run_time" : 0.1,
        "rate_func" : None,
    }
    def __init__(self, mobject, **kwargs):
        self.intermediate = Mobject(color = self.color)
        self.intermediate.add_points([
            point + (x, y, 0)
            for point in self.mobject.points
            for x in [-1, 1]
            for y in [-1, 1]
        ])
        Animation.__init__(self, mobject, **kwargs)        

    def update_mobject(self, alpha):
        #Makes alpha go from 0 to slow_factor to 0 instead of 0 to 1
        alpha = self.slow_factor * (1.0 - 4 * (alpha - 0.5)**2)
        self.mobject.interpolate(
            self.starting_mobject, 
            self.intermediate, 
            alpha
        )

class Homotopy(Animation):
    def __init__(self, homotopy, mobject, **kwargs):
        """
        Homotopy a function from (x, y, z, t) to (x', y', z')
        """
        digest_locals(self)
        Animation.__init__(self, mobject, **kwargs)

    def update_mobject(self, alpha):
        self.mobject.points = np.array([
            self.homotopy((x, y, z, alpha))
            for x, y, z in self.starting_mobject.points
        ])






