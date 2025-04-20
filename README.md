# Predictive Maintenance

Submission for the course "Industrial Internet of Things" at Chaitanya Bharathi Institute of Technology, 2025.

![sample](assets/sample.png)

## Team Members

| Name | Roll No |
| ---- | ------- |
| C. Rithesh Reddy | 160122771034 |
| G. Jayanth | 160122771041 |

## Introduction

This project is a predictive maintenance system that uses machine learning to predict equipment failures based on sensor data. The system consists of several components that work together to collect, process, and analyze sensor data in real-time.
The system uses a Kafka broker to handle the data stream and an MQTT broker to collect data from sensors. The machine learning model is used to predict equipment failures based on the sensor data. The predictions are then sent to a Streamlit dashboard for visualization.

## Architecture

![architecture](assets/architecture.png)

## Instructions to run the code

### Requirements

- Python 3.8 or higher
- Kafka (3.3 or higher recommended)
- MQTT broker - Eclipse Mosquitto (2.0 or higher recommended)

### Running the code

1. Clone the repository:

    ```bash
    git clone https://github.com/gjaynir0508/iiot-project.git
    ```

    This creates a directory named `iiot-project` in your current working directory.

    ```bash
    cd iiot-project
    ```

    Open this directory in your favorite code editor.

    ```bash
    code .
    ```

    Then open a terminal in the code editor or continue using the terminal you have open.

    The root directory of the project is the directory where the `README.md` file is located. All commands in this README file should be run from this directory.

2. Install the required packages:
    - Navigate to the project directory:

    - [Optional] Create a virtual environment:

    ```bash
    python -m venv venv
    ```

    - Activate the virtual environment:
        - On Windows: Run the following command in the terminal:

        ```bash
        venv\Scripts\activate
        ```

    - Install the required packages from the `requirements.txt` file:

    ```bash
    pip install -r requirements.txt
    ```

3. Start Kafka server

   - Follow the instructions in the [Kafka Quickstart](https://kafka.apache.org/quickstart) to start the Kafka server.

   - Create a topic named `sensor_data`:

    ```bash
    kafka-topics.sh --create --topic sensor_data --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
    ```

   - Create a topic named `predictions`:

    ```bash
    kafka-topics.sh --create --topic predictions --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
    ```

4. Start the MQTT broker
    - Add the mosquitto binaries to your PATH and run the following command in a terminal:

    ```bash
    mosquitto
    ```

    - There will be no output in the terminal, but the broker will be running in the background. You can check if the broker is running by opening a new terminal and running the following command:

    ```bash
    mosquitto_sub -h localhost -t test
    ```

    - If the broker is running, you will see no output in the terminal. You can stop the broker by pressing `Ctrl + C`.
5. Now we start running the project's components. Run the following commands in separate terminals in the same order, all in the _root directory_ of the project:

    - Start the MQTT-Kafka bridge:

    ```bash
    python mqtt_kafka_bridge/bridge.py
    ```

    - Start the Inference server:

    ```bash
    python model/model_server.py
    ```

    - Start the Inference server:

    ```bash
    python model/model_server.py
    ```

    - Start the Prediction service that writes to the `predictions` topic:

    ```bash
    python model/predictor_kafka.py
    ```

    - Start the streamlit dashboard:

    ```bash
    streamlit run dashboard/streamlit_dashboard.py
    ```

### Stopping the services

- To stop the services, press `Ctrl + C` in each terminal where the services are running. This will stop the services and close the terminals.
- Follow the reverse order in which they were started to stop the services. First, stop the streamlit dashboard, then the prediction service, then the inference server, and finally the MQTT-Kafka bridge.
- Finally, stop the Kafka server and the MQTT broker.
