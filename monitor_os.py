import os
import time

def recheck_hashes():
    print("recheck_hashes() triggered: Change detected in /etc/shadow. Re-extracting and re-cracking hashes...")
    
    # Define the path for formatted_hashes.txt on the Desktop
    output_path = os.path.expanduser("/home/sai/Desktop/formatted_hashes.txt")
    
    try:
        # Open /etc/shadow for reading and formatted_hashes.txt for writing
        with open('/etc/shadow', 'r') as shadow_file, open(output_path, 'w') as outfile:
            print("Opened /etc/shadow and formatted_hashes.txt successfully.")
            
            # Extract SHA-512 hashes from /etc/shadow and save them to formatted_hashes.txt
            for line in shadow_file:
                parts = line.strip().split(':')
                username = parts[0]
                hash_value = parts[1]
                
                # Only include users with SHA-512 hashes (those starting with "$6$")
                if hash_value.startswith("$6$"):
                    outfile.write(f"{username}:{hash_value}\n")
                    print(f"Extracted hash for user: {username}")

        print(f"Hashes successfully extracted to '{output_path}'.")

    except PermissionError as e:
        print("Permission denied. Ensure you have the necessary permissions:", e)
    except Exception as e:
        print("An error occurred while extracting hashes:", e)

def monitor_shadow_file():
    shadow_path = '/etc/shadow'
    last_modified_time = os.path.getmtime(shadow_path)
    
    print("Monitoring /etc/shadow for changes...")

    try:
        while True:
            current_modified_time = os.path.getmtime(shadow_path)
            if current_modified_time != last_modified_time:
                print("Change detected in /etc/shadow, calling recheck_hashes()")
                last_modified_time = current_modified_time
                recheck_hashes()
            time.sleep(2)  # Check every 2 seconds
    except KeyboardInterrupt:
        print("Monitoring stopped.")
  
# Run the monitoring function
monitor_shadow_file()
