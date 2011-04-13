class Filter(object):
    name = None

    def __init__(self):
        self.init_model()
    
    def init_model(self):
        None
    
    def train(self, message, is_spam):
        pass
    
    def predict(self, message):
        return False, 0
