from numpy import asarray, arange

from neuroimaging.core.api import ImageList, Image

from neuroimaging.core.reference.coordinate_map import CoordinateMap
from neuroimaging.core.reference.coordinate_system import VoxelCoordinateSystem
from neuroimaging.core.reference.mapping import Affine

class FmriImageList(ImageList):
    """
    Class to implement image list interface for FMRI time series

    Allows metadata such as volume and slice times
    """

    def __init__(self, images=None, TR=0., slicetimes=None,
                 frametimes=None):
        """
        A lightweight implementation of an fMRI image as in ImageList
        
        Parameters
        ----------
        images: a sliceable object whose items are meant to be images,
                this is checked by asserting that each has a `coordmap` attribute
        TR:     time between frames in fMRI acquisition
        slicetimes: ndarray specifying offset for each slice of each frame
        frametimes: optional way of overriding TR if frames are not evenly
                    sampled in time
        See Also
        --------
        neuroimaging.core.image_list.ImageList

        >>> from numpy import asarray
        >>> from neuroimaging.testing import funcfile
        >>> from neuroimaging.modalities.fmri.api import FmriImageList, fromimage
        >>> from neuroimaging.core.api import load_image
        
        >>> # fmrilist and ilist represent the same data

        >>> funcim = load_image(funcfile)
        >>> fmrilist = fromimage(funcim)
        >>> ilist = FmriImageList(funcim)
        >>> print asarray(ilist).shape
        (20, 2, 20, 20)
        >>> print asarray(ilist[4]).shape
        (2, 20, 20)

        """

        ImageList.__init__(self, images=images)
        self.TR = TR
        self.slicetimes = slicetimes

    def __getitem__(self, index):
        """
        If index is an index, return self.list[index], an Image
        else return an FmriImageList with images=self.list[index].
        
        """
        if type(index) is type(1):
            return self.list[index]
        else:
            return FmriImageList(images=self.list[index], TR=self.TR,
                             slicetimes=self.slicetimes)

    def __setitem__(self, index, value):
        self.list[index] = value
        
    def __array__(self):
        return asarray([asarray(i) for i in self.list])

    def emptycopy(self):
        return FmriImageList(images=[], TR=self.TR, slicetimes=self.slicetimes)

    def _getframetimes(self):
        if hasattr(self, "_frametimes"):
            return self._frametimes
        else:
            return arange(len(self.list)) * self.TR

    frametimes = property(_getframetimes)

def fmri_generator(data, iterable=None):
    """
    This function takes an iterable object and returns a generator for

    [numpy.asarray(data)[:,item] for item in iterator]

    This is used to get time series out of a 4d fMRI image.

    Note that if data is an FmriImageList instance, there is more 
    overhead involved in calling numpy.asarray(data) than if
    data is in Image instance.

    If iterables is None, it defaults to range(data.shape[0])
    """
    data = asarray(data)
    if iterable is None:
        iterable = range(data.shape[1])
    for item in iterable:
        yield item, data[:,item]


def fromimage(fourdimage, TR=None, slicetimes=None):
    """Create an FmriImageList from a 4D Image.

    Load an image from the file specified by ``url`` and ``datasource``.

    Note this assumes that the 4d Affine mapping is such that it
    can be made into a list of 3d Affine mappings

    Parameters
    ----------
    fourdimage: a 4D Image 
    TR:     time between frames in fMRI acquisition, defaults to
            the diagonal entry of slowest moving dimension
            of Affine transform
    slicetimes: ndarray specifying offset for each slice of each frame


    """
    images = []
    if not isinstance(fourdimage.coordmap.mapping, Affine):
        raise ValueError, 'fourdimage must have an Affine mapping'
    
    for im in [fourdimage[i] for i in range(fourdimage.shape[0])]:
        g = im.coordmap
        oa = g.output_coords.axes()[1:]
        oc = VoxelCoordinateSystem("world", oa)
        t = im.coordmap.mapping.transform[1:]
        a = Affine(t)
        newg = CoordinateMap(a, im.coordmap.input_coords, oc)
        images.append(Image(asarray(im), newg))

    if TR is None:
        TR = fourdimage.coordmap.mapping.transform[0,0]
        
    return FmriImageList(images=images, TR=TR, slicetimes=slicetimes)