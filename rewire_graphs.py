import sys
import importlib
import subprocess
import os
import argparse

def check_module(module_name):
    try:
        module = importlib.import_module(module_name)
        version = getattr(module, "__version__", "unknown")
        print(f"✓ {module_name} is installed (version: {version})")
        return True
    except ImportError:
        print(f"✗ {module_name} is not installed")
        return False

def check_r_package(package_name):
    """Check if an R package is installed using rpy2"""
    try:
        import rpy2.robjects as robjects
        check_cmd = f'is.element("{package_name}", installed.packages()[,"Package"])'
        result = robjects.r(check_cmd)[0]
        if result:
            print(f"✓ R package {package_name} is installed")
            return True
        else:
            print(f"✗ R package {package_name} is not installed")
            return False
    except Exception as e:
        print(f"✗ Error checking R package {package_name}: {str(e)}")
        return False

def check_directory(dir_name):
    if os.path.exists(dir_name):
        print(f"✓ Directory '{dir_name}' exists")
        return True
    else:
        print(f"✗ Directory '{dir_name}' does not exist")
        return False

def parse_arguments():
    parser = argparse.ArgumentParser(description='Check environment for Network Communities Randomization.')
    
    parser.add_argument('--input-dir', '-i', 
                        dest='base_dir',
                        default='communities_graphs',
                        help='Directory containing input GML files (default: communities_graphs)')
    
    return parser.parse_args()

def main():
    args = parse_arguments()
    base_dir = args.base_dir
    
    print("Checking environment for Network Communities Randomization...")
    print("\nPython version:")
    print(f"Python {sys.version.split()[0]}")
    
    print("\nChecking required Python packages:")
    python_modules = [
        "networkx",
        "numpy",
        "pandas",
        "rpy2",
        "tqdm",
        "concurrent.futures",
        "argparse"
    ]
    
    all_modules_installed = all(check_module(module) for module in python_modules)
    
    print("\nChecking R integration:")
    try:
        import rpy2.robjects as robjects
        r_version = robjects.r('R.version.string')[0]
        print(f"✓ R is accessible through rpy2 ({r_version})")
        r_accessible = True
    except Exception as e:
        print(f"✗ Error accessing R through rpy2: {str(e)}")
        r_accessible = False
    
    if r_accessible:
        print("\nChecking required R packages:")
        check_r_package("BiRewire")
    
    print("\nChecking directories:")
    check_directory(base_dir)
    
    print("\nEnvironment check complete!")
    
    if not all_modules_installed:
        print("\nSome Python modules are missing. Install them with:")
        print("pip install -r requirements.txt")
    
    if not r_accessible:
        print("\nR is not accessible. Make sure R is installed and properly configured with rpy2.")
        print("Run the following command to install required R packages:")
        print("Rscript install_r_dependencies.R")
    
    if not check_directory(base_dir):
        print(f"\nThe '{base_dir}' directory is missing. Create it and add your GML files before running the program.")
        print(f"You can create it with: mkdir -p {base_dir}")

if __name__ == "__main__":
    main()