from UPISAS.strategy import Strategy

# This is a dummy strat for dingnet, with this it should be able to run,
# when you are ready to implement your own strategy do it here.


class EmptyStrategy(Strategy):

    def analyze(self):
        return True

# If this plan section is empty it will give an error:
# ERROR:root:No complete JSON Schema provided for validation Keys misaligned
    def plan(self):
        self.knowledge.plan_data = {
            "items": [
                {
                    'id': 0,
                    'adaptations': [
                        {
                            'name': 'sampling_rate',
                            'value': 10
                        }
                    ]
                }
            ]
        }
        return True
