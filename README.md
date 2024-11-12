# How to install python 3.9 on ubuntu and windows


## How to install python 3.9 on ubuntu
- Install packages
- Download python3.9
- Build and install python binaries

## Install packages
```bash
> sudo apt update
> sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev
```
## Download python3.9
```bash
> wget https://www.python.org/ftp/python/3.9.1/Python-3.9.1.tgz
```
## Extract python
```bash
> tar -xf Python-3.9.1.tgz
```
## Check dependencies and test
```bash
> cd Python-3.9.1 && ./configure --enable-optimizations
```
## Build using make file
```bash
> make -j 12
```
## Install python
```bash
> sudo make altinstall
```
## Check version and location
```bash
> python3.9 --version
Python 3.9.1

> which python3.9
/usr/local/bin/python3.9
```
## Change default python
```bash
> sudo update-alternatives --install /usr/bin/python python /usr/local/bin/python3.9 3

> sudo update-alternatives --config python
There are 3 choices for the alternative python (providing /usr/bin/python).

  Selection    Path                      Priority   Status
------------------------------------------------------------
  0            /usr/local/bin/python3.9   3         auto mode
  1            /usr/bin/python2.7         1         manual mode
* 2            /usr/bin/python3.6         2         manual mode
  3            /usr/local/bin/python3.9   3         manual mode

Press <enter> to keep the current choice[*], or type selection number: 3
update-alternatives: using /usr/local/bin/python3.9 to provide /usr/bin/python (python) in manual mode

```
**If you got a warning like this:**
```bash
WARNING: The script pip3.8 is installed in /usr/local/bin(EXAMPLE) which is not on PATH.
```
You need to add the following line to your `~/.bash_profile` or `~/.bashrc` or `~/.zshrc` file.
```bash
> echo 'export PATH="$HOME/usr/local/bin(EXAMPLE):$PATH"' >> ~/.bashrc
```



# How to install python 3.9 on windows
- Install with links
- https://www.tutorials24x7.com/python/how-to-install-python-39-on-windows


# Hướng dẫn chạy:
## cd đường dẫn thư mục pdf_classifier run:
```bash
> pip install -r requirements.txt
```
## cd đường dẫn thư mục pdf_classifier run:
```bash
> python/python3/python3.9  main.py <type> <code> <path>
```
## ví dụ: 
```bash
> python main.py invoice rolls_royce /Users/hieuthanh/Desktop/OCR/pdf/invoice_rr.pdf
```
## hoặc có thể chạy: 
```bash
> python/python3/python3.9 <path>/main.py <type> <code> <path>
```
