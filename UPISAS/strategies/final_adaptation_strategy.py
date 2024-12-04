from UPISAS.strategy import Strategy
import logging
# Configure basic logging
logging.basicConfig(level=logging.INFO)

# Initialization
import random
def initialize_q_table():
    print("enter q table initialise")
    # Define state bins for signal strength and packet loss
    signal_bins = [-60, -40, 2] # Discretize signalStrength into bins // TASK - FIND THE VALUES 
    # low_signal_threshold = -48.0  # dBm
    # high_signal_threshold = -42.0  # dBm
    packet_loss_bins = [0, 0.1, 0.2, 0.3, 0.5]  #  Discretize packetLoss into bins

    # Define actions
    actions = ["Increase", "Decrease", "Maintain"]

    # Initialize Q-table as a dictionary
    q_table = {}
    for signal in signal_bins:
        print("logging signal", signal)
        for packet_loss in packet_loss_bins:
            print("logging packet_loss", packet_loss)
            state = (signal, packet_loss)
            print("logging state", state)
            q_table[state] = {action: 0.0 for action in actions}  # Initializes as floats
            print("qtable", q_table)
 # Initialize Q-values to 0

    return q_table

def map_to_state(signal_strength, packet_loss):
    print("enter map to state")
    # Map continuous values to discrete bins
    signal_bins = [-60, -40, 2]
    packet_loss_bins = [0, 0.1, 0.2, 0.3, 0.5]
    
    signal_state = min(signal_bins, key=lambda x: abs(x - signal_strength))
    packet_loss_state = min(packet_loss_bins, key=lambda x: abs(x - packet_loss))
    
    return (signal_state, packet_loss_state)


def simulation_running():
    print("enter simulation running")
    # Placeholder for simulation's termination condition
    return random.random() > 0.05

def need_to_adjust_thresholds(signal_strength, packet_loss, performance_goal):
    # Placeholder for threshold adjustment logic
    print("enter need_to_adjust_thresholds")
    return False

def random_action():
    return random.choice(["Increase", "Decrease", "Maintain"])

def increase_power(transmission_power):
    transmission_power = min(transmission_power + 1, 15)  # Max power is 15
    #should be added to knowledge in plan 

def decrease_power(transmission_power):
    transmission_power = max(transmission_power - 1, -1)  # Min power is -1

def maintain_power():
    pass  # Placeholder for maintaining power logic

def check_performance_goal(q_table, performance_goal):
    # Placeholder for checking if performance goal is met
    return False


def best_action(q_table, state):
    return max(q_table[state], key=q_table[state].get)

class QBasedStrategy(Strategy):
    def analyze(self):
        print("enter analyse")
        Q_table = initialize_q_table()  # Q-table with states (signalStrength, packetLoss) and actions
        print("Q table", Q_table)
        alpha = 0.1  # Learning rate
        gamma = 0.9  # Discount factor
        epsilon = 1.0  # Exploration rate (start with full exploration)
        epsilon_decay = 0.99  # Decay factor for epsilon
        min_epsilon = 0.1  # Minimum exploration rate
        max_episodes = 1000  # Maximum number of episodes
        convergence_threshold = 0.01  # Threshold for Q-value changes
        performance_goal = {"maxPacketLoss": 0.05, "signalRange": (-48, -42)}  # Goal for stopping

        # Signal strength and packet loss thresholds
        minSignal = -48
        maxSignal = -42
        maxPacketLoss = 0.05

        # Training Loop
        for episode in range(max_episodes):
            print("enter episode for loop", episode)
            # Step 1: Initialize the environment
            # Extract mote states from monitored data
            mote_states = self.knowledge.monitored_data.get("moteStates", [])
            self.knowledge.analysis_data = {}
            initial_mote_id = 0

            for mote_state in mote_states:
                mote = mote_state[0]
                mote_id = initial_mote_id  # Unique ID for each mote
                initial_mote_id += 1
                signalStrength = mote["highestReceivedSignal"]
                packetLoss = mote["packetLoss"]
                transmission_power = mote["transmissionPower"]

            # Get current signal strength and packet loss
            state = map_to_state(signalStrength, packetLoss)  # Map to a discrete state

            # Initialize variables for convergence check
            max_q_change = 0

            while simulation_running():  # Continue simulation until episode ends
                # Step 2: Choose an action using epsilon-greedy
                print("enter simulation")
                if random.random() < epsilon:
                    action = random_action()  # Explore
                else:
                    action = best_action(Q_table, state)  # Exploit

                # Step 3: Perform the chosen action
                if action == "Increase":
                    increase_power(transmission_power)
                elif action == "Decrease":
                    decrease_power(transmission_power)
                elif action == "Maintain":
                    maintain_power()

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
                # Get new signal  packet loss
                new_state = map_to_state(newSignalStrength, newPacketLoss)

                # Calculate reward based on signal and packet loss
                if minSignal <= newSignalStrength <= maxSignal and newPacketLoss <= maxPacketLoss:
                    reward = 1  # Positive reward
                else:
                    reward = -1  # Negative reward
                
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
            if need_to_adjust_thresholds(signalStrength, packetLoss, performance_goal):
                minSignal, maxSignal, 
                maxPacketLoss = adjust_thresholds(minSignal, maxSignal, maxPacketLoss)
                print("thresholds adjusted", state)

            # Step 7: Check stopping criteria
            if max_q_change < convergence_threshold:
                print("Convergence achieved. Stopping training.")
                break

            # Decay epsilon to reduce exploration over time
            epsilon = max(min_epsilon, epsilon * epsilon_decay)
            print("calculated epsilon")
            # Check if performance goal is met
            if check_performance_goal(Q_table, performance_goal):
                print("Performance goal achieved. Stopping training.")
                break

        # End of training
        print("Training completed.")

    def plan(self):

            return True


