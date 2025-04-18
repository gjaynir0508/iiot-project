import pandas as pd


class SensorDataSimulator:
    def __init__(self, data_path):
        self.data = self._load_data(data_path)
        self.engines = self.data['engine_id'].unique()
        self.current_engine_idx = 0
        self.current_cycle = 1

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
        if self.current_engine_idx >= len(self.engines):
            return None  # No more data

        engine_id = self.engines[self.current_engine_idx]
        engine_data = self.data[self.data['engine_id'] == engine_id]

        cycle_data = engine_data[engine_data['cycle'] == self.current_cycle]
        if cycle_data.empty:
            # Move to next engine
            self.current_engine_idx += 1
            self.current_cycle = 1
            return self.get_sensor_data()  # Recursive call for next engine

        self.current_cycle += 1

        return cycle_data.drop(['engine_id', 'cycle'], axis=1).iloc[0].to_dict()


# Example usage
if __name__ == "__main__":
    simulator = SensorDataSimulator("../CMAPSSData/train_FD001.txt")

    for _ in range(5):  # Simulate 5 sensor reads
        data = simulator.get_sensor_data()
        print(data)
