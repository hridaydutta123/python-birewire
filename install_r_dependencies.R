# R script to install required R dependencies

# Check if BiRewire is installed, if not, install it
if (!require("BiRewire", quietly = TRUE)) {
  message("Installing BiRewire package...")
  install.packages("BiRewire")
}

# Load and check the installation
library(BiRewire)
message("BiRewire package installed successfully!")