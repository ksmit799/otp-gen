class GeneratorInterface:
    def __init__(self, dc_loader, out_dir):
        self.dc_loader = dc_loader
        self.outDir = out_dir

    def start(self):
        pass
