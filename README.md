

<p align="center">
  <a href="https://usbitfarm.com/">
    <img width="200" src="https://usbitfarm.com/app/images/logos.png">
  </a>
</p>

<h1 align="center">BFChia</h1>

<div align="center">

Chia mass plotting management system

</div>

![](https://usbitfarm.com/images/bfchia.png)

English | [简体中文](./README-zh_CN.md)

## ✨ Features

- 🌈 Enterprise-class UI designed for web applications
- 📦 A set of high-quality code out of the box.
- 🛡 Written in Python.
- ⚙️ Whole package of design resources and development tools.
- 🌍 Internationalization support for dozens of languages.
- 🎨 Powerful theme customization in every detail.

## 🖥 Environment Support

- Linux
- Windows


## 📦 Installation(Ubuntu20.04)

```bash
git clone https://github.com/usbitfarm/bfchia.git
```
```bash
cd bfchia
```
```bash
pip3 install -r requirements.txt
```
# Installation(Compiler Environment)
```bash
sudo apt install -y libsodium-dev cmake
```
# Compile madMAx chia-plotter(https://github.com/madMAx43v3r/chia-plotter) script
```bash
sh make_linux.sh
```
## 📦 Installation(Windows)
```bash
# Download and install python3
https://www.python.org/downloads/
# Download and install git
https://git-scm.com/downloads
# Download (Windows)[madMAx]chia-plotter
https://github.com/stotiks/chia-plotter/releases
# Copy chia_plot.exe to 
bfchia\plugins\plotters
```


## 🔨 Configure config.ini
```bash
# Copy plotting setting 'config.sample.ini' and rename to 'config.ini'
# Create an account on https://usbitfarm.com and copy your personal token
https://usbitfarm.com/member/profile
Find 'Mining rig token'
Example：ABCXXXXX
```
### Example
```jsx
[bitfarm]
token = ABCxxxxx

[bfchia]
farms[] =
  /media/bitfarm/farm1
  /media/bitfarm/farm2

[chiaplotter]
active = 1
threads = 60
buckets = 512
contract_address = xchxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
pool_key = 
farmer_key = 87cf63a9xxxxxxxxxxxxxxxxxxxxxec9f214c12a529f
dir_temp = /media/bitfarm/tmp1
dir_temp2 = /media/bitfarm/ramdisk
dir_dest[] =
  /media/bitfarm/farm1
  /media/bitfarm/farm2

[harvester]
active = 1
init = 1
chia_path = /home/yourusername/chia-blockchain/venv/bin/chia
certs_dir = /home/yourusername/ca-cpoy/
farmer_host = 127.0.0.1
farmer_port = 8447

```

Explain：

```jsx
farms[] =  #Farm's token
active = #1=Plotting 0=Monitoring(not plotting)
threads =  #Number of threads
buckets =  #Number of buckets 128 \ 256 \ 512
contract_address =  #Pool address
pool_key =  #OG pool key
farmer_key =  #Farmer key
dir_temp =  #Temporary plotting directory 1 30%Read/Write (Plot copied to destination from here)
dir_temp2 =  #Temporary plotting directory 2 70%Read/Write
dir_dest[] =  #Plot destination directory
[harvester] Remote harvester options
active = 1=Running  0=Stopped
init = 1=Initialize newly added harvester  0=Not initializing，(Usually require only once hostmachine verification)
chia_path = /chia filepath
certs_dir = /chia private key filepath
farmer_host = Farmer IP (Default 127.0.0.1)
farmer_port = Farmer port (Default 8447)
```

## Usage

Run command
```bash
python3 main.py
```
Check farmer status at [https://usbitfarm.com/member/xch](https://usbitfarm.com/member/xch) 

## ⌨️ Tips

Set up xfs disk format for Ubuntu plotting
```bash
sudo apt install xfsprogs -y
sudo mkfs.xfs /dev/nvme0n1p1 /media/bitfarm/temp1  #nvme0n1p1 Replace with plotter filepath
```
Set up for sharing across multiple Windows machines
```bash
sudo apt-get install samba
# Share local folders to other machines
sudo nautilus
# In the popup windows, select FileSystem then right click on folder you want to share and select local network sharing
```
Network drives mapping
```bash
# Create a folder in /mnt
cd /mnt
sudo mkdir 10.10.10.10
# Mount network drives //10.10.10.XXX/farm/ to local mnt/10.10.10.10/farm/
sudo mount -t cifs -o username=XXXXXX,password=XXXXXX,uid=$(id -u),gid=$(id -g) //10.10.10.XXX/farm/  mnt/10.10.10.10/farm/
# Unmount all network drives
sudo umount -a -t cifs -l 
```
If you encounter permission problems after compiling
```bash
chmod +x plugins/plotters/chia_plot
```
## ⌨️ **Ubuntu set up Chia harvester node**
Update and make sure git is installed
```bash
sudo apt-get update
sudo apt-get upgrade -y
sudo apt install git -y
```
Clone Chia repository
```bash
git clone https://github.com/Chia-Network/chia-blockchain.git -b latest --recurse-submodules
```
Enter Chia-blockchain directory
```bash
cd chia-blockchain
```
Run
```bash
. ./activate
```
Install Chia GUI
```bash
sh install-gui.sh
```
Copy \.chia\mainnet\config\ssl\ca folder from main machine to harvester machine and initialize it.
```bash
chia init -c ~/ca
```
Stop all Chia programs
```bash
chia stop all
```
Configure harvester ip and port number according to machine
```bash
chia configure --set-farmer-peer 192.168.1.88:8447
```
Disable UPNP
```bash
chia configure --enable-upnp false
```
Add new directories for plots
```bash
chia plots add -d /media/bitfarm/farm1
chia plots add -d /media/bitfarm/farm2
chia plots add -d /media/bitfarm/more
```
Command to start harvester
```bash
chia start harvester -r
```
Command to stop harvester
```bash
chia stop harvester
```
