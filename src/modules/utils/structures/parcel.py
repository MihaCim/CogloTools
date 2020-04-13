class Parcel:
    """
    Stores parcel information for single delivery
    Target is a destination Node
    Default package volume for poc is 1, for easier UUID unpacking
    """
    def __init__(self, uuid, target, volume):
        self.volume = volume
        self.target = target
        self.uuid = uuid
