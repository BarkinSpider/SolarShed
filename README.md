# SolarShed
Goal - Realtime data monitoring and control of solar equipment.
(this is an active project - im updating this page regularly - Mar 2022)
If you have any suggestions or see errors, please create an Issue, the link to do that is up above (Issues in the GitHub menubar)

Read the discussion of this project here: https://diysolarforum.com/threads/off-grid-solar-battery-monitoring-and-control-freeware.6662/
You can contact me by posting to the forum above. 

Most of the projects here are based around using a Raspberry Pi Zero or Pi 4 hardware to read the serial output of compatible devices like charge controllers and display the information using Grafana. This allows you to monitor your solar system from any location using any device with a web browser, like your smartphone.

For development Pi I choose this Pi4 model with 4GB. https://www.amazon.com/gp/product/B07VYC6S56/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1
Get a 32GB card (2 for $20), this makes for a fast development machine that can do anything.

For deployment get the Pi Zero, way cheaper and much smaller. https://www.amazon.com/gp/product/B0748MPQT4/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1

For storage, use the 32GB SD card, just a few dollars more than 16GB, and allows for future expansion and other projects.
https://www.amazon.com/PNY-Elite-microSDHC-Memory-P-SDU32GU185GW-GE/dp/B01MY8WGV7/ref=sr_1_12?crid=2L2CRB2OOAP4X&dchild=1&keywords=32gb%2Bmicro%2Bsd%2Bcard&qid=1587993513&s=electronics&sprefix=32GB%2Bmicro%2Celectronics%2C214&sr=1-12&th=1

Use this neat USB adapter to power your Pi Zero, it plugs right into any USB slot like on the Epever Triton series... https://www.amazon.com/gp/product/B07NKNBZYG/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1
 
Then you run a usb/rs485 or RS232 cable (depending on what your connecting to) from the Pi, straight into the data port of the device you want to monitor. 

To connect the full size USB cable to a Pi Zero, you will need an USB->microUSB adapter.

Only use a quality RS232 cable to avoid problems.

https://www.amazon.com/DTECH-Serial-Adapter-Supports-Windows/dp/B079LZSF32/ref=dp_prsubs_1?pd_rd_i=B079LZSF32&psc=1

To break out a DB5 port using the cable above use

https://www.amazon.com/gp/aw/d/B073H9B6ZZ?psc=1&ref=ppx_pop_mob_b_asin_title

For Modbus and RS485 connections, use these cables.
https://www.amazon.com/JBtek-Converter-Adapter-ch340T-Supported/dp/B00NKAJGZM/ref=sr_1_24?dchild=1&keywords=modbus+485+cable&qid=1607638123&sr=8-24

Once Raspian light OS (no GUI) is installed, and the OS updates in my cheat sheet are done, 
the monitoring suite of Grafana, Prometheus and node_exporter will be installed on your Pi and be configured ready for use.

Important: Before installing any extra monitoring programs, you need to have node_exporter collecting and showing all your system metrics in Grafana. For example, memory, disk and CPU usage, load and network thoughput, errors etc. This is easy to achieve and very well documented as node_exporter is the #1 use of Grafana. My cheat sheet should provide all the information you need.

Once Grafana is working, its easy to add additional metrics and make your own dashboards.

My cheat sheet to configure a Raspberry PI for this purpose.
https://github.com/BarkinSpider/SolarShed/blob/master/Pi%20Setup%20Cheat%20Sheet

If you want more info or get stuck, here is additonal information and a graphical 
guide to setting up node_exporter on any system.
https://devconnected.com/complete-node-exporter-mastery-with-prometheus/

Once working, all my monitoring scripts output data to the folder /ramdisk
/ramdisk is a memory based temporary filesystem folder I custom configure to increase performance and avoid read/write issues with SSD cards.

Only data written to /ramdisk will be available for monitoring with Grafana when using my system, as that is where node_exporter is configured to find it. node_exporter is the service that loads data into the Prometheus database so that Grafana can find it, and display the information graphically. 

If you want to contact me or have any questions please post them at https://diysolarforum.com/threads/off-grid-solar-battery-monitoring-and-control-freeware.6662/

Joe

