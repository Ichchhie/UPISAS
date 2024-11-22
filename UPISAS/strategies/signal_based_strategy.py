from UPISAS.strategy import Strategy
import logging
# Configure basic logging
logging.basicConfig(level=logging.INFO)


class SignalBasedStrategy(Strategy):
    def analyze(self):
        print("analyze class")
        # Extract mote states from monitored data
        mote_states = self.knowledge.monitored_data.get("moteStates", [])
        self.knowledge.analysis_data = {}

        # Define signal strength thresholds
        low_signal_threshold = -48.0  # dBm
        high_signal_threshold = -42.0  # dBm
        initial_mote_id = 0

        for mote_state in mote_states:

            mote = mote_state[0]
            mote_id = initial_mote_id  # Unique ID for each mote
            initial_mote_id += 1
            highest_signal = mote["highestReceivedSignal"]
            transmission_power = mote["transmissionPower"]
            logging.debug("transmissionPower {transmission_power}")

            # Adapt power based on received signal strength
            if highest_signal < low_signal_threshold:
                # Increase power if signal is too low
                new_power = min(transmission_power + 1, 15)  # Max power is 15
                logging.debug("here in first case ")

            elif highest_signal > high_signal_threshold:
                # Decrease power if signal is too high
                new_power = max(transmission_power - 1, -1)  # Min power is -1
                logging.debug("here in second case ")

            else:
                # Maintain current power if signal is within acceptable range
                new_power = transmission_power
                logging.debug("here in third case ")

            # Store analyzed result for this mote
            self.knowledge.analysis_data[mote_id] = {
                "highest_signal": highest_signal,
                "recommended_power": new_power
            }

        return True

    def plan(self):
        print("plan class")

        # Use analysis data to create a plan for adapting each mote's transmission power
        adaptations = []
        for mote_id, analysis in self.knowledge.analysis_data.items():
            new_power = analysis["recommended_power"]

            # Create adaptation action for the mote's power setting
            adaptations.append({
                "id": mote_id,
                "adaptations": [
                    {
                        "name": "power",
                        "value": new_power
                    }
                ]
            })

        # Store the plan in knowledge plan_data
        self.knowledge.plan_data = {
            "items": adaptations
        }

        return True


