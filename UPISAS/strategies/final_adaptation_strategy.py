from UPISAS.strategy import Strategy
import logging
# Configure basic logging
logging.basicConfig(level=logging.INFO)

# Initialization
import random

def get_dynamic_state(signal_strength, packet_loss):
    # Introduce some randomness to simulate more varied states
    noise_signal = random.uniform(-5, 5)  # Random noise for signal strength
    noise_packet_loss = random.uniform(-0.05, 0.05)  # Random noise for packet loss
    
    # Apply the noise to the current signal and packet loss
    dynamic_signal = signal_strength + noise_signal
    dynamic_packet_loss = packet_loss + noise_packet_loss

    # Ensure the signal is within the expected range
    dynamic_signal = max(min(dynamic_signal, 0), -100)
    dynamic_packet_loss = max(min(dynamic_packet_loss, 1.0), 0)

    return dynamic_signal, dynamic_packet_loss

# Define state bins for signal strength and packet loss
class QBasedStrategy(Strategy):
    signal_bins = [-100, -90, -80, -70, -60, -50, -43, -42] # Discretize signalStrength into bins // TASK - FIND THE VALUES 
    # low_signal_threshold = -48.0  # dBm
    # high_signal_threshold = -42.0  # dBm
    packet_loss_bins = [0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5, 1.0]  #  Discretize packetLoss into bins

    # Define actions
    actions = ["Increase", "Decrease", "Maintain"]
    # Signal strength and packet loss thresholds
    minSignal = -48
    maxSignal = -42
    maxPacketLoss = 0.05

    def initialize_q_table(self):
        print("enter q table initialise")

        # Initialize Q-table as a dictionary
        q_table = {}
        for signal in self.signal_bins:
            print("logging signal", signal)
            for packet_loss in self.packet_loss_bins:
                print("logging packet_loss", packet_loss)
                state = (signal, packet_loss)
                print("logging state", state)
                q_table[state] = {action: 0.0 for action in self.actions}  # Initializes as floats
                print("qtable", q_table)
        # Initialize Q-values to 0

        return q_table

    def map_to_state(self, signal_strength, packet_loss):
        print("enter map to state")
        # Map continuous values to discrete bins
        # signal_bins = [-48, -42, 2]
        # packet_loss_bins = [0, 0.1, 0.2, 0.3, 0.5]
        
        signal_state = min(self.signal_bins, key=lambda x: abs(x - signal_strength))
        packet_loss_state = min(self.packet_loss_bins, key=lambda x: abs(x - packet_loss))
        
        return (signal_state, packet_loss_state)


    def simulation_running(self):
        print("enter simulation running")
        # Placeholder for simulation's termination condition
        return random.random() > 0.05

    def adjust_thresholds(self, signal_strength, packet_loss, performance_goal):
        # Placeholder for threshold adjustment logic
        print("enter need_to_adjust_thresholds")
        adjustment_step = 1

        observed_packet_loss = packet_loss
        max_allowed_packet_loss = self.maxPacketLoss #max packet loss set as 5 for now

        # Adjust thresholds based on packet loss
        if observed_packet_loss > max_allowed_packet_loss:
            # Relax thresholds to improve reliability
            self.minSignal -= adjustment_step  # Allow weaker signals
            self.maxSignal += adjustment_step  # Allow stronger signals
        elif observed_packet_loss < max_allowed_packet_loss / 2:
            # Tighten thresholds to improve energy efficiency
            self.minSignal += adjustment_step  # Require stronger signals
            self.maxSignal -= adjustment_step  # Constrain power usage

        # Ensure thresholds remain within logical boundaries
        print("printing minSignal before max",self.minSignal,self.maxSignal)
        self.minSignal = max(self.minSignal, -100)  # Avoid excessive relaxation
        self.maxSignal = min(self.maxSignal, 0)     # Avoid excessive tightening

        print("printing minSignal, maxSignal",self.minSignal, self.maxSignal, self.maxPacketLoss)
        return self.minSignal, self.maxSignal, self.maxPacketLoss

    def random_action(self):
        return random.choice(["Increase", "Decrease", "Maintain"])

    def increase_power(self, transmission_power):
        transmission_power = min(transmission_power + 1, 15)  # Max power is 15
        #should be added to knowledge in plan 

    def decrease_power(self, transmission_power):
        transmission_power = max(transmission_power - 1, -1)  # Min power is -1

    def maintain_power(self):
        pass  # Placeholder for maintaining power logic

    def check_performance_goal(self, q_table, performance_goal):
        print("enter check performance goal", performance_goal)
        print("performance_goal:", performance_goal, "Type:", type(performance_goal))
        # Extract performance goal thresholds
        max_packet_loss = performance_goal["maxPacketLoss"]
        print("printing values", max_packet_loss)
        min_signal = performance_goal["signalRange"][0]
        max_signal = performance_goal["signalRange"][1]
        print("printing min and max signal", min_signal, max_signal)

        
        
        # Track the number of states meeting performance criteria
        successful_states = 0
        total_states = 0

        for state, actions in q_table.items():
            print("enter for loop", state, actions)
            signal_strength, packet_loss = state
            # Check if the state meets performance goals
            if min_signal <= signal_strength <= max_signal and packet_loss <= max_packet_loss:
                total_states += 1
                # Check if the preferred action ("Maintain") has the highest Q-value
                best_action = max(actions, key=actions.get)
                if best_action == "Maintain":
                    successful_states += 1

        # Define success criteria (e.g., 80% of valid states must prefer "Maintain")
        success_ratio = successful_states / total_states if total_states > 0 else 0
        required_ratio = 0.8  # Example threshold
        
        return success_ratio >= required_ratio

    def best_action(self, q_table, state):
        return max(q_table[state], key=q_table[state].get)

    def analyze_state(self, mote_state):

        # Extract mote parameters
        signal_strength = mote_state["highestReceivedSignal"]
        packet_loss = mote_state["packetLoss"]
        transmission_power = mote_state["transmissionPower"]

        # Map the current state to discrete bins
        current_state = self.map_to_state(signal_strength, packet_loss)

        # Select the best action based on the Q-table
        best_action = self.best_action(self.knowledge.analysis_data["QTable"], current_state)

        # Determine the new transmission power based on the selected action
        if best_action == "Increase":
            transmission_power = min(transmission_power + 1, 15)  # Max power is 15
        elif best_action == "Decrease":
            transmission_power = max(transmission_power - 1, -1)  # Min power is -1
        # If "Maintain", keep the current transmission power

        return transmission_power

    def train(self):
        print("enter train")
        Q_table = self.initialize_q_table()  # Q-table with states (signalStrength, packetLoss) and actions
        print("Q table", Q_table)
        alpha = 0.2  # Learning rate
        gamma = 0.9  # Discount factor
        epsilon = 1.0  # Exploration rate (start with full exploration)
        epsilon_decay = 0.995  # Decay factor for epsilon
        min_epsilon = 0.1  # Minimum exploration rate
        max_episodes = 10  # Maximum number of episodes
        convergence_threshold = 0.01  # Threshold for Q-value changes
        performance_goal = {"maxPacketLoss": 0.05, "signalRange": (-48, -42)}  # Goal for stopping

        # Training Loop
        for episode in range(max_episodes):
            print("enter episode for loop", episode)
            # Step 1: Initialize the environment
            # Extract mote states from monitored data
            mote_states = self.knowledge.monitored_data.get("moteStates", [])
            self.knowledge.analysis_data = {}
            initial_mote_id = 0
            print("check mote state values", mote_states)

            for mote_state in mote_states:
                mote = mote_state[0]
                mote_id = initial_mote_id  # Unique ID for each mote
                initial_mote_id += 1
                signalStrength = mote["highestReceivedSignal"]
                packetLoss = mote["packetLoss"]
                transmission_power = mote["transmissionPower"]
 
            print("check teh values", self.minSignal)
            dynamic_signal, dynamic_packet_loss = get_dynamic_state(signalStrength, packetLoss)
            # Get current signal strength and packet loss
            state = self.map_to_state(dynamic_signal, dynamic_packet_loss)  # Map to a discrete state

            # Initialize variables for convergence check
            max_q_change = 0

            while self.simulation_running():  # Continue simulation until episode ends
                # Step 2: Choose an action using epsilon-greedy
                print("enter simulation")
                if random.random() < epsilon:
                    action = self.random_action()  # Explore
                else:
                    action = self.best_action(Q_table, state)  # Exploit

                # Step 3: Perform the chosen action
                if action == "Increase":
                    self.increase_power(transmission_power)
                elif action == "Decrease":
                    self.decrease_power(transmission_power)
                elif action == "Maintain":
                    self.maintain_power()

                # Step 4: Observe the new state and reward
                mote_states = self.knowledge.monitored_data.get("moteStates", [])
                self.knowledge.analysis_data = {}
                initial_mote_id = 0

                for mote_state in mote_states:
                    mote = mote_state[0]
                    mote_id = initial_mote_id  # Unique ID for each mote
                    initial_mote_id += 1
                    newSignalStrength = mote["highestReceivedSignal"]
                    newPacketLoss = mote["packetLoss"]

                print()


                # Get new signal  packet loss
                new_state = self.map_to_state(newSignalStrength, newPacketLoss)

                # Calculate reward based on signal and packet loss
                #if self.minSignal <= newSignalStrength <= self.maxSignal and newPacketLoss <= self.maxPacketLoss:
                #    reward = 1  # Positive reward
                #else:
                #    reward = -1  # Negative reward

                # Signal Strength Reward
                signal_reward = 0
                if self.minSignal <= newSignalStrength <= self.maxSignal:
                    signal_reward = 1  # Full reward for acceptable signal strength
                else:
                    # Penalty for weak or too strong signal
                    signal_reward = -0.5 * abs(newSignalStrength - self.maxSignal)  # Gradual penalty based on deviation

                # Packet Loss Reward
                packet_loss_reward = 0
                if newPacketLoss <= self.maxPacketLoss:
                    packet_loss_reward = 1  # Full reward for acceptable packet loss
                else:
                    # Gradual penalty based on deviation
                    packet_loss_reward = -0.5 * (newPacketLoss - self.maxPacketLoss)

                # Total Reward
                reward = signal_reward + packet_loss_reward

                
                print("reward calculated", reward)
                print("Q table", Q_table)
                print("state and action", state, action)

                # Step 5: Update the Q-table
                old_q_value = Q_table[state][action]  # Should be a float
                print("old q value", old_q_value)
                max_future_q = max(Q_table[new_state].values())  # Should also be a float
                print("future q value", max_future_q)
                Q_table[state][action] = old_q_value + alpha * (reward + gamma * max_future_q - old_q_value)
                print("updated q table", Q_table)

                # Track the maximum Q-value change for convergence check
                max_q_change = max(max_q_change, abs(Q_table[state][action] - old_q_value))
                print("max q change", max_q_change)

                # Update the current state
                state = new_state
                print("updated q table", state)

            # Step 6: Adjust thresholds (optional)
            print("need to adjust reached")
            self.minSignal, self.maxSignal, self.maxPacketLoss = self.adjust_thresholds(self.minSignal, self.maxSignal, self.maxPacketLoss)

            # Step 7: Check stopping criteria
            #if max_q_change < convergence_threshold:
            #    print("Convergence achieved. Stopping training.")
            #    break

            # Decay epsilon to reduce exploration over time
            epsilon = max(min_epsilon, epsilon * epsilon_decay)
            print("calculated epsilon")
            # Check if performance goal is met
            if self.check_performance_goal(Q_table, performance_goal):
                print("Performance goal achieved. Stopping training.")
                #break

            #training is completed so putting the qtable in knowledge here
            # Save the updated Q-table to the knowledge base
            print("after training q table", Q_table)

            self.knowledge.analysis_data["QTable"] = Q_table
         # End of training
        print("Training completed.")
    
    def analyze(self):
        print("enter analyze")
        # Initialize the output
        mote_transmission_updates = {}
        # Retrieve the Q-table and mote states
        Final_Q_table = self.knowledge.analysis_data.get("QTable", {})
        mote_states = self.knowledge.monitored_data.get("moteStates", [])

        initial_mote_id = 0

        for mote_state in mote_states:

            mote = mote_state[0]
            mote_id = initial_mote_id  # Unique ID for each mote
            initial_mote_id += 1
    
            # Analyze the state and determine the new transmission power
            new_transmission_power = self.analyze_state(mote)

            # Store the result
            mote_transmission_updates[mote_id] = new_transmission_power
                # Store analyzed result for this mote
            self.knowledge.analysis_data[mote_id] = {
                "recommended_power": new_transmission_power
            }
            print("new transmission power", self.knowledge.analysis_data)
             

    def plan(self):
        print("plan class")

        # Use analysis data to create a plan for adapting each mote's transmission power
        adaptations = []
        for mote_id, analysis in self.knowledge.analysis_data.items():
            new_power = analysis["recommended_power"]
            print("the values in plan", mote_id, new_power)
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




