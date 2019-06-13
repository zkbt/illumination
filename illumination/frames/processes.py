'''
Define some Processes, which can be applied to Image_Sequence objects.
'''
#def get_processing_step(x):
#    if type(x) == 'str':




class Process:
    '''
    The Process class can perform basic image processing steps
    on a sequence of images. Every Process will take at least
    (1) an unprocessed `image` and possibly (2) the image
    `sequence` from which that raw image came, if it's needed.

    Some processes take additional keywords, like a `timestep`.
    '''

    def __repr__(self):
        '''
        How should this be represented as a string?
        '''
        return self.__class__.name

    def __add__(self, other):
        '''
        Create a multi-step process.
        '''
        return CompositeProcess(self, other)

class CompositeProcess:
    '''
    The CompositeProcess combines two Processes together, in order.
    '''

    def __repr__(self):
        '''
        How should this be represented as a string?
        '''
        return '{}|{}'.format(self.first, self.next)

    def __init__(self, first, next):
        '''
        Initialize by storing the processing step that should be
        done first, and the one that should be done afterward.
        '''

        # store both processes
        self.first = first
        self.next = next

    def __call__(self, image, sequence=None, **kwargs):
        return self.next(image=self.first(image=image,
                                          sequence=sequence,
                                          **kwargs),
                         sequence=sequence,
                         **kwargs)


class Unmodify(Process):
    '''
    Don't modify the image.
    '''
    def __call__(self, image, sequence=None, **kwargs):
        return image

class SubtractMedian(Process):
    '''
    Subtract the median image.
    '''
    def __call__(self, image, sequence, **kwargs):
        return image - sequence.median()

class SubtractMean(Process):
    '''
    Subtract the median image.
    '''
    def __call__(self, image, sequence, **kwargs):
        return image - sequence.mean()

class SubtractPrevious(Process):
    '''
    Subtract the previous image from the current image.
    '''
    def __call__(self, image, sequence, timestep):
        comparison = timestep - 1 #this wraps at the end
        return image - sequence[comparison]

class SubtractBeforeAndAfter(Process):
    '''
    Subtract the previous image from the current image.
    '''
    def __call__(self, image, sequence, timestep):
        before = timestep - 1
        after = (timestep + 1)%len(sequence)
        return rawimage - 0.5*(sequence[before] + sequence[after])

processes = [   'Process',
                'CompositeProcess',
                'SubtractMedian',
                'SubtractMean',
                'SubtractPrevious',
                'SubtractBeforeAndAfter']

# create a dictionary
string2processes = {}
for k in processes:
    string2processes[k.lower()] = vars()[k]

def make_process(x):
    if isinstance(x, Process):
        return x
    elif type(x) is list:
        return sum([string2processes[p.lower() for p in x])

# THIS GETS MOVED INTO IMSHOW FRAME (OR MAYBE EVEN IMAGE_SEQUENCE?)
def get_processed_image(self, timestep):
    '''
    Get the image, and apply any extra processing
    steps to it (subtract differences, normalize,
    subtract smooth backgrounds, etc...?)
    '''

    # pull out the raw image
    rawimage = self.data[timestep]
    assert(rawimage is not None)

    process = ??? # we need to have defined make_process when we made the frame (or sequence?)
    return process(image=rawimage, sequence=self.data, timestep=timestep)
