import pandas as pd
import random


class SensorDataSimulator:
    def __init__(self, data_path):
        self.data = self._load_data(data_path)
        self.engines = self.data['engine_id'].unique()
        self.engine_cycle_pointers = {eid: 1 for eid in self.engines}
        self.finished_engines = set()

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

    def get_sensor_data(self):
        # All engines finished
        available_engines = [
            eid for eid in self.engines if eid not in self.finished_engines
        ]
        if not available_engines:
            return None
        # Pick a random engine that still has data
        engine_id = random.choice(available_engines)
        current_cycle = self.engine_cycle_pointers[engine_id]

        engine_data = self.data[self.data['engine_id'] == engine_id]
        cycle_data = engine_data[engine_data['cycle'] == current_cycle]

        if cycle_data.empty:
            # No more data for this engine
            self.finished_engines.add(engine_id)
            return self.get_sensor_data()  # Try again with another engine

        self.engine_cycle_pointers[engine_id] += 1

        sensor_data = cycle_data.drop(['engine_id'], axis=1).iloc[0].to_dict()
        return engine_id, sensor_data


# Example usage
if __name__ == "__main__":
    simulator = SensorDataSimulator("../CMAPSSData/train_FD001.txt")

    for _ in range(10):  # Simulate 10 random sensor reads
        data = simulator.get_sensor_data()
        if data is None:
            print("Simulation complete")
            break
        print(data)
