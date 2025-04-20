import pandas as pd
import random


class SensorDataSimulator:
    def __init__(self, data_path):
        self.data = self._load_data(data_path)
        self.engines = self.data['engine_id'].unique()
        self.choose_from_a_max_of = 5  # Max number of engines to choose from
        self.engine_cycle_pointers = {eid: 1 for eid in self.engines}
        self.finished_engines = set()
        self.currently_chosen_engines = set()

    def _load_data(self, path):
        # Load raw training data (FD001)
        col_names = ['engine_id', 'cycle'] + \
                    [f'op_setting_{i}' for i in range(1, 4)] + \
                    [f'sensor_{i}' for i in range(1, 22)]
        df = pd.read_csv(path, sep=' ', header=None)
        df.drop(
            columns=[col for col in df.columns if col not in range(26)], inplace=True)
        df.columns = col_names
        return df

    def _select_new_engines(self):
        # Select a new set of engines once the current set is exhausted
        if len(self.currently_chosen_engines) == 0:
            available_engines = set(self.engines) - self.finished_engines
            if len(available_engines) == 0:
                return None
            if len(available_engines) <= self.choose_from_a_max_of:
                self.currently_chosen_engines = list(available_engines)
            else:
                self.currently_chosen_engines = list(random.sample(
                    sorted(available_engines), self.choose_from_a_max_of))

        # If we still have engines in the current set, return them
        return self.currently_chosen_engines

    def get_sensor_data(self):
        # All engines finished
        available_engines = self._select_new_engines()
        if available_engines is None:
            return None

        # Pick a random engine that still has data
        engine_id = random.choice(available_engines)
        current_cycle = self.engine_cycle_pointers[engine_id]

        engine_data = self.data[self.data['engine_id'] == engine_id]
        cycle_data = engine_data[engine_data['cycle'] == current_cycle]

        if cycle_data.empty:
            # No more data for this engine
            self.finished_engines.add(engine_id)
            self.currently_chosen_engines.remove(engine_id)
            return self.get_sensor_data()  # Try again with another engine

        self.engine_cycle_pointers[engine_id] += 1

        sensor_data = cycle_data.drop(['engine_id'], axis=1).iloc[0].to_dict()
        return engine_id, sensor_data


# Example usage
if __name__ == "__main__":
    simulator = SensorDataSimulator("./CMAPSSData/train_FD001.txt")

    for _ in range(5000):  # Simulate 10 random sensor reads
        data = simulator.get_sensor_data()
        if _ % 50 == 0:
            if data is None:
                print("Simulation complete")
                break
            print(f"{_} Current Engines: {simulator.currently_chosen_engines}")
            print(f"Engine ID: {data[0]}, Sensor Data: {str(data[1])[:50]}...")
