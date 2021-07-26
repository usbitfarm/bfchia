
<p align="center">
  <a href="https://usbitfarm.com/">
    <img width="200" src="https://usbitfarm.com/app/images/logos.png">
  </a>
</p>

<h1 align="center">BFChia</h1>

<div align="center">

Chia 集群P图管理程序

</div>

![](https://usbitfarm.com/images/bfchia.png)

## ✨ 特性

- 🌈 企业级中后台产品的交互语言和视觉风格。
- 📦 开箱即用的高质量代码。
- 🛡 使用 Python 开发。
- ⚙️ 全链路开发和设计体系。
- 🌍 国际化语言支持。
- 🎨 深入每个细节的定制能力。

## 🖥 兼容环境

- Linux
- Windows


## 📦 安装(Ubuntu20.04)

```bash
git clone https://github.com/usbitfarm/bfchia.git
cd bfchia
pip3 install -r requirements.txt

# 一键安装并编译 madMAx chia-plotter(https://github.com/madMAx43v3r/chia-plotter) 脚本
sh make_linux.sh
```


## 📦 安装(Windows)
```bash
# 安装Python3
https://www.python.org/downloads/
# 安装Git
https://git-scm.com/downloads

# 下载Windows版本[madMAx]chia-plotter
https://github.com/stotiks/chia-plotter/releases

# 复制chia_plot.exe文件到 
bfchia\plugins\plotters
```


## 🔨 配置config.ini
```bash
# 复制P图配置 config.sample.ini 并重命名为 config.ini
# 到 https://usbitfarm.com 注册账号并复制个人令牌
[https://usbitfarm.com/member/profile](https://usbitfarm.com/member/profile)
找到 Mining rig token
例如：ABCXXXXX
```
### 示例
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
```

说明：

```jsx
farms[] =  #需要监视的存储盘的地址
active = #1为开启P图模式 0为监视模式不P图
threads =  #使用线程数
buckets =  #桶的数量 128 \ 256 \ 512
contract_address =  #矿池合约地址
pool_key =  #OG矿池密匙
farmer_key =  #farmer密匙
dir_temp =  #P盘1 30%读取写入 完成文件从这里复制去存储盘
dir_temp2 =  #P盘2 70%读取写入
dir_dest[] =  #存储盘地址
```

## 执行程序
```bash
执行程序
python3 main.py
```
到[https://usbitfarm.com/member/xch](https://usbitfarm.com/member/xch) 查看进度

## ⌨️ 小技巧

Ubuntu下设置P图硬盘格式xfs
```bash
sudo apt install xfsprogs -y
sudo mkfs.xfs /dev/nvme0n1p1 /media/bitfarm/temp1  #nvme0n1p1 请替换自己的实际P盘地址
```
设置共享于Windows或其他机器共享
```bash
sudo apt-get install samba
# 分享本地文件给其他机器
sudo nautilus
# 打开窗口后选择FileSystem找到要分享的文件夹右键选择本地网络共享
```
网络硬盘映射
```bash
# 先在 /mnt 创建文件夹 例如
cd /mnt
sudo mkdir 10.10.10.10
# 挂载网络主机 //10.10.10.XXX/farm/到本地 mnt/10.10.10.10/farm/
sudo mount -t cifs -o username=XXXXXX,password=XXXXXX,uid=$(id -u),gid=$(id -g) //10.10.10.XXX/farm/  mnt/10.10.10.10/farm/
# 卸载所有网络映射盘
sudo umount -a -t cifs -l 
```
编译完成后如果遇见权限问题
```bash
chmod +x plugins/plotters/chia_plot
```