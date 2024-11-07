# Update system packages
echo "Updating system packages..."
sudo yum update -y

# Enable the Software Collections (SCL) repository and install dependencies
echo "Installing required dependencies..."
sudo yum install -y centos-release-scl
sudo yum groupinstall -y "Development Tools"
sudo yum install -y openssl-devel bzip2-devel libffi-devel zlib-devel wget

# Download Python 3.9 source code
echo "Downloading Python 3.9..."
cd /usr/src
sudo wget https://www.python.org/ftp/python/3.9.10/Python-3.9.10.tgz

# Extract the downloaded file
echo "Extracting Python 3.9 files..."
sudo tar xzf Python-3.9.10.tgz
cd Python-3.9.10

# Compile and install Python 3.9
echo "Configuring and installing Python 3.9..."
sudo ./configure --enable-optimizations
sudo make altinstall

# Verify the installation
echo "Verifying Python 3.9 installation..."
python3.9 --version

# Install pip for Python 3.9 if not included
echo "Ensuring pip is installed for Python 3.9..."
sudo python3.9 -m ensurepip --upgrade

# Check pip installation
echo "Verifying pip installation..."
pip3.9 --version

# Set Python 3.9 as default for python command
echo "Setting Python 3.9 as default for python command..."
sudo ln -sf /usr/local/bin/python3.9 /usr/bin/python

# Confirm python points to Python 3.9
echo "Checking python version..."
python --version

echo "Python 3.9 installation complete!"
