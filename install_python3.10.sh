# Update system packages
echo "Updating system packages..."
sudo yum update -y

# Enable the Software Collections (SCL) repository and install dependencies
echo "Installing required dependencies..."
sudo yum install -y centos-release-scl
sudo yum groupinstall -y "Development Tools"
sudo yum install -y openssl-devel bzip2-devel libffi-devel zlib-devel wget

# Download Python 3.10 source code
echo "Downloading Python 3.10..."
cd /usr/src
sudo wget https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tgz

# Extract the downloaded file
echo "Extracting Python 3.10 files..."
sudo tar xzf Python-3.10.0.tgz
cd Python-3.10.0

# Compile and install Python 3.10
echo "Configuring and installing Python 3.10..."
sudo ./configure --enable-optimizations
sudo make altinstall

# Verify the installation
echo "Verifying Python 3.10 installation..."
python3.10 --version

# Install pip for Python 3.10 if not included
echo "Ensuring pip is installed for Python 3.10..."
sudo python3.10 -m ensurepip --upgrade

# Check pip installation
echo "Verifying pip installation..."
pip3.10 --version

# Optionally set Python 3.10 as default python3
echo "Setting Python 3.10 as default for python3 command..."
sudo ln -sf /usr/local/bin/python3.10 /usr/bin/python3

# Confirm python3 points to Python 3.10
echo "Checking python3 version..."
python3 --version

echo "Python 3.10 installation complete!"
