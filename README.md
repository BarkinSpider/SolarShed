# SolarShed
Goal - Realtime data monitoring and control of solar equipment.
(this is an active project - im updating this page regularly - Jun 2020)

Most of the projects here are based around using a Raspberry Pi Zero or Pi 4 hardware.
Once Raspian light OS (no GUI) is installed, the monitoring suite of
Grafana, Prometheus and node_exporter are installed and configured.

Before continuing you need to have node_exporter showing all your system metrics in Grafana.
For example, memory, disk and CPU usage. Load and nwtork thoughput, errors etc.
This is easy to achieve and very well documented as node_exporter is the #1 use of Grafana

Once working, its easy to add additional metrics and make your own dashboards.

See my cheat sheet to see how I configure my own PI for this purpose.
https://github.com/BarkinSpider/SolarShed/blob/master/Pi%20Setup%20Cheat%20Sheet

If you want more info or get stuck, here is additonal information and graphical 
guide to setting up node_exporter on any system.

https://devconnected.com/complete-node-exporter-mastery-with-prometheus/
