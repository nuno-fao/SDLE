Firstly, to install the packages needed to run the project just run the following command in the project's root:
pip install -r ../requirements.txt

To run the project just run the following commands inside the src folder:

Bootstrap node:
sudo python3 peer.py -p PORT                e.g. PORT=8000

Other nodes:
sudo python3 peer.py -p PORT -b BOOTSTRAP_ADDRESS:BOOTSTRAP_PORT     e.g. PORT=8001 BOOTSTRAP_ADDRESS=127.0.0.1 BOOTSTRAP_PORT=8000

The commands need to be run in a linux distribution since the python's implementation of kademlia has some problems on Windows.
We need to run with root privileges in order to update the peers' local time.