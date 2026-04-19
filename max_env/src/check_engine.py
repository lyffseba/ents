from max import engine
from max import driver

def main():
    print("Welcome to the Ents inference engine.")
    print("Initializing MAX Inference Session...")
    
    # We must pass actual device objects to the session.
    # Scan for available devices and grab the first one (for Apple Silicon, this shows as 'gpu')
    available_devices = driver.scan_available_devices()
    print(f"Detected devices: {available_devices}")
    
    # Load the devices from their specs
    loaded_devices = driver.load_devices(available_devices)
    
    if not loaded_devices:
        print("Error: Could not load devices!")
        return

    session = engine.InferenceSession(devices=loaded_devices)
    
    print(f"Session successfully created using loaded devices: {loaded_devices}")
    print(f"Ready to compile and load models.")

if __name__ == "__main__":
    main()
