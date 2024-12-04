from UPISAS.strategies.final_adaptation_strategy import QBasedStrategy
# from UPISAS.strategies.empty_strategy import EmptyStrategy

from UPISAS.exemplar import Exemplar
from UPISAS.exemplars.dingnet import DINGNET
import signal
import sys
import time

if __name__ == '__main__':
    
    exemplar = DINGNET(auto_start=True)
    time.sleep(30)
    exemplar.start_run()
    time.sleep(3)

    try:
        strategy = QBasedStrategy(exemplar)

        strategy.get_monitor_schema()
        strategy.get_adaptation_options_schema()
        strategy.get_execute_schema()

        while True:
            input("Try to adapt?")
            strategy.monitor(verbose=True)
            strategy.analyze()
                #if strategy.plan():
                #    strategy.execute()
            
    except (Exception, KeyboardInterrupt) as e:
        print(str(e))
        input("something went wrong")
        exemplar.stop_container()
        sys.exit(0)