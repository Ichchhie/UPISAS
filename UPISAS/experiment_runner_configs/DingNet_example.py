import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from EventManager.Models.RunnerEvents import RunnerEvents
from EventManager.EventSubscriptionController import EventSubscriptionController
from ConfigValidator.Config.Models.RunTableModel import RunTableModel
from ConfigValidator.Config.Models.FactorModel import FactorModel
from ConfigValidator.Config.Models.RunnerContext import RunnerContext
from ConfigValidator.Config.Models.OperationType import OperationType
from ExtendedTyping.Typing import SupportsStr
from ProgressManager.Output.OutputProcedure import OutputProcedure as output

from typing import Dict, List, Any, Optional
from pathlib import Path
from os.path import dirname, realpath
import time
import statistics

from UPISAS.strategies.signal_based_strategy import SignalBasedStrategy
from UPISAS.exemplars.dingnet import DINGNET


class RunnerConfig:
    ROOT_DIR = Path(dirname(realpath(__file__)))

    # ================================ USER SPECIFIC CONFIG ================================
    """The name of the experiment."""
    name: str = "new_runner_experiment"

    """The path to output results."""
    results_output_path: Path = ROOT_DIR / 'experiments'

    """Operation type: Use `OperationType.AUTO` for automatic runs."""
    operation_type: OperationType = OperationType.AUTO

    """Wait time between runs."""
    time_between_runs_in_ms: int = 1000

    exemplar = None
    strategy = None

    def __init__(self):
        """Executes immediately after program start, on config load."""
        EventSubscriptionController.subscribe_to_multiple_events([
            (RunnerEvents.BEFORE_EXPERIMENT, self.before_experiment),
            (RunnerEvents.BEFORE_RUN, self.before_run),
            (RunnerEvents.START_RUN, self.start_run),
            (RunnerEvents.START_MEASUREMENT, self.start_measurement),
            (RunnerEvents.INTERACT, self.interact),
            (RunnerEvents.STOP_MEASUREMENT, self.stop_measurement),
            (RunnerEvents.STOP_RUN, self.stop_run),
            (RunnerEvents.POPULATE_RUN_DATA, self.populate_run_data),
            (RunnerEvents.AFTER_EXPERIMENT, self.after_experiment),
        ])
        self.run_table_model = None  # Initialized later
        self.transmissionPowerList = []
        self.highestReceivedSignalList = []
        self.energyEfficiencyList = []
        self.packetlossPercentageList = []
        output.console_log("Custom config loaded")

    def create_run_table_model(self) -> RunTableModel:
        """Define the factors and data columns for the experiment."""
        factor1 = FactorModel("adaptation_strategy", ["provoost"])
        self.run_table_model = RunTableModel(
            factors=[factor1],
            repetitions=30,
            exclude_variations=[],
            data_columns=['highest_received_signal','transmission_power','packet_loss','total_energy_consumption']

        )
        return self.run_table_model

    def before_experiment(self) -> None:
        """Perform any activity required before starting the experiment."""
        output.console_log("Config.before_experiment() called!")

    def before_run(self) -> None:
        """Set up the exemplar and strategy before a run starts."""
        self.exemplar = DINGNET(auto_start=True)
        time.sleep(30)
        self.exemplar.start_run()
        time.sleep(3)
        self.strategy = SignalBasedStrategy(self.exemplar)
        time.sleep(3)
        output.console_log("Config.before_run() called!")

    def start_run(self, context: RunnerContext) -> None:
        """Start the target system and set up run-specific parameters."""
        time.sleep(3)
        output.console_log("Config.start_run() called!")

    def start_measurement(self, context: RunnerContext) -> None:
        """Prepare for measurement during the run."""
        output.console_log("Config.start_measurement() called!")

    def interact(self, context: RunnerContext) -> None:
        """Interact with the system or block until the run completes."""
        mon_data = self.strategy.knowledge.monitored_data

        for x in range(50):

            self.strategy.get_monitor_schema()
            self.strategy.get_adaptation_options_schema()
            self.strategy.get_execute_schema()

            self.strategy.monitor(verbose=True)
            if self.strategy.analyze():
                if self.strategy.plan():
                    self.strategy.execute()

            for mote_state in mon_data.get("moteStates", []):
                mote = mote_state[0]
                highest_received_signal = mote["highestReceivedSignal"]  
                transmission_power = mote["transmissionPower"]
                packets_sent = mote["packetsSent"]
                packet_loss_percentage = mote["packetLoss"]
                sampling_rate = mote["samplingRate"]  

                energy_efficiency = self.calculate_energy_consumption(transmission_power, packets_sent, sampling_rate)
                self.energyEfficiencyList.append(energy_efficiency)
                self.packetlossPercentageList.append(packet_loss_percentage)
                self.transmissionPowerList.append(transmission_power)
                self.highestReceivedSignalList.append(highest_received_signal)

        output.console_log(f"Config.interact() called")

    def calculate_energy_consumption(self,transmission_power_dbm, packets_sent, sampling_rate):
        # Convert transmission power from dBm to Watts
        power_mw = 10 ** (transmission_power_dbm / 10)
        power_watts = power_mw / 1000  # Convert mW to Watts

        # Calculate transmission time
        transmission_time = packets_sent / sampling_rate  # in seconds

        # Compute energy consumption
        energy_consumed = power_watts * transmission_time  # in Joules
        print(f"Energy Consumption: {energy_consumed:.3f} Joules")

        return energy_consumed

 
    def stop_measurement(self, context: RunnerContext) -> None:
        """Stop any measurements after the run."""
        output.console_log("Config.stop_measurement() called!")

    def stop_run(self, context: RunnerContext) -> None:
        """Stop the exemplar container."""
        self.exemplar.stop_container()
        output.console_log("Config.stop_run() called!")

    def populate_run_data(self, context: RunnerContext) -> Optional[Dict[str, SupportsStr]]:
        """Parse and process measurement data into a results dictionary."""
        output.console_log("Config.populate_run_data() called!")

      
        print("statistics", statistics)
        return {"highest_received_signal": statistics.mean(self.highestReceivedSignalList), 
        "transmission_power": statistics.mean(self.transmissionPowerList),
        "packet_loss": f"{statistics.mean(self.packetlossPercentageList)*100:.2f}%",
        "total_energy_consumption": f"{statistics.mean(self.energyEfficiencyList)*1000:.2f}mJ"}

    def after_experiment(self) -> None:
        """Perform any cleanup after the experiment."""
        output.console_log("Config.after_experiment() called!")

    # ================================ DO NOT ALTER BELOW THIS LINE ================================
    experiment_path: Path = None