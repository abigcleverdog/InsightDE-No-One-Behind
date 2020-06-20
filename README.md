<h1 align="center">
  <br>
  No one behind
  <br>
</h1>


<h4 align="center">Monitering engagement level of an large size online classroom using <a href="https://opencv.org/" target="_blank">OpenCV</a> and <a href="https://www.rabbitmq.com/" target="_blank">RabbitMQ</a> </h4>

<p align="center">
    <img src="https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000"
         alt="License">

</p>

<p align="center">
  <a href="#-key-features">Key Features</a> •
  <a href="#-technical-architecture">Technical Architecture</a> •
  <a href="#-how-to-use">How To Use</a> •
  <a href="#-configuration">Configuration</a> •
  <a href="#-demo">Demo</a> •
  <a href="#-scaling-performance">Scaling Performance</a> •
  <a href="#-credits">Credits</a> •
  <a href="#-contact">Contact</a>

</p>


## 🎨 Key Features

-   **Scalable** - The system is designed to distribute work load over a processing cluster.  The amount of nodes in the processing cluster is adjustable.  No perfomance loss has been observed when scaling up horizontally via adding nodes to the cluster.

-   **High throughput** - Current tests have demonstrated capacity of streaming up to 400 videos spontaneously with just two (2) m5.24xlarge nodes. With ten (10) cheaper m5.large nodes, tests have been carried out at the capacity of 200 videos.

-   **Low latency** - Using m5.large nodes, each node can deliver 1 video with about 0.6 s delay (from frame extraction to report generation); 5 videos, 0.9 s; 10 videos, 1.4 s; 20 videos, 2.1 s. Using m5.24xlarge nodes, 1 video 0.6; 5 videos, 0.7 s; 10 videos, 0.7 s; 20 videos, 1.0 s.

-   **Stability** - The delay is stable over time if input streams stay steady. When there is a sudden change, such as increase in the number of streams input, the delay can re-establish stability over 1 second.

-   **Modular approach** - Replace Face recognition model with desired Image processing model to detect entities as per your use case.

## 🔨 Technical Architecture

![architecture](/pic/arch.jpg)

## ▶️ How To Use

-   Setup RabbitMQ cluster
-   Launch receiver
`python3 feeder.py <number of streams>`
-   Launch feeder(s)
`python3 main.py <threshold>`
-   Launch dashboard to visualize the result
`python3 flaskapp.py`
or config apache service to server the app


## ⚙️ Configuration

1.  **FRAME_EX_RATE**

    -   The ratio of frames are extracted. Default is 10, set to low for high accuracy, set to high for high performance.

2.  **VID_THROUGHPUT_SIZE**

    -   The frames are compressed before analyzing. Large size can lead to higher accuracy and small size can lead to high performance.

3.  **VID_ROLLING**

    -   When set as 'True'. the stream will keep rolling till interruption.


## 🐾 Demo

![screenshot](/data/3_1.gif)

## 🚀 Scaling Performance

![latency](/pic/latency.jpg)

## ❤️ Credits

This software uses following open source packages.

-   [OpenCV](https://opencv.org)
-   [RabbitMQ](https://www.rabbitmq.com)
-   [MySQL](https://www.mysql.com)

* * *

## ✏️ Contact

> [Linkedin](http://www.linkedin.com/in/xiaofZ) · 
> [GitHub](github.com/abigcleverdog)  · 
> [Kaggle](https://www.kaggle.com/abigcleverdog)  · 