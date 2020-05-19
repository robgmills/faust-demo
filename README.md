## Kafka Streams + Faust POC

### Overview
This project serves as a POC for using [Kafka Streams](https://kafka.apache.org/documentation/streams/) and [Faust](https://faust.readthedocs.io/en/latest/) to aggregate API request metrics segmented by high-cardinality client attributes (e.g. user ID).

### Getting Setup
#### Prerequisites
* Python 3.6+
* [Zookeeper instance and Kafka server](https://kafka.apache.org/quickstart) running on `localhost:9092`


### Usage
1. Install Faust: `pip install faust`
2. Start the Faust worker: `faust -A windowed_requests worker -l info`
3. In a new terminal window, produce a message to the topic: `faust -A windowed_requests send windowed_requests '{"user_id": "7", "path": "/api/v1/data"}'`
4. Fetch the current usage metrics for a given user: `curl localhost:6066/metrics/users/7`

### FAQ
#### Why not just use Prometheus?
[Prometheus](https://prometheus.io/) is a poor fit for storing high cardinality metrics as discussed in their [own documentation](https://prometheus.io/docs/practices/naming/#labels) and [this more in-depth article](https://www.robustperception.io/cardinality-is-key).
