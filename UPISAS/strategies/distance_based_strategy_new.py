from UPISAS.strategy import Strategy
import logging

class DistanceBasedStrategy(Strategy):

    def analyze(self):
        # Extract mote states from monitored data
        mote_states = self.knowledge.monitored_data.get("moteStates", [])
        self.knowledge.analysis_data = {}

        for mote in mote_states:
            # Use get() to safely access dictionary elements
            mote_id = mote["eui"]  # Unique ID for each mote
            distance_to_gateway = mote.get("shortestDistanceToGateway", float('inf'))
            transmission_power = mote.get("transmissionPower", 0)

            # Define the distance intervals and adjust transmission power
            if distance_to_gateway > 100:
                new_power = min(transmission_power + 1, 15)  # Max power is 15
            elif distance_to_gateway < 50:
                new_power = max(transmission_power - 1, -1)  # Min power is -1
            else:
                new_power = transmission_power

            # Store analyzed result for this mote by eui (unique ID)
            self.knowledge.analysis_data[mote_id] = {
                "distance_to_gateway": distance_to_gateway,
                "recommended_power": new_power
            }

        return True

    def plan(self):
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

    # def execute(self):
    #     # Send the planned adaptations to the execute endpoint
    #     adaptation_plan = self.knowledge.plan_data
    #     self.execute(adaptation=adaptation_plan)
    #     return True
