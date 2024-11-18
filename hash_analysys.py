import os
import platform
import subprocess
import time

def recheck_hashes():
    print("recheck_hashes() has been called.")

    # Detect the OS
    os_type = platform.system()
    output_path = os.path.expanduser("/home/formatted_hashes.txt") if os_type == "Linux" else os.path.expanduser("~\\Desktop\\windows_hashes.txt")

    # Step 1: OS-specific Hash Extraction
    if os_type == "Linux":
        try:
            # Extract hashes from /etc/shadow
            with open('/etc/shadow', 'r') as shadow_file, open(output_path, 'w') as outfile:
                for line in shadow_file:
                    parts = line.strip().split(':')
                    username = parts[0]
                    hash_value = parts[1]
                    if hash_value.startswith("$6$"):  # SHA-512 hashes
                        outfile.write(f"{username}:{hash_value}\n")
                        print(f"Extracted hash for user: {username}")
            print(f"Hashes successfully extracted to '{output_path}'.")

            crack_format = "sha512crypt"

        except PermissionError as e:
            print("Permission denied. Run the script with sudo:", e)
            return
        except Exception as e:
            print("An unexpected error occurred while extracting hashes:", e)
            return


    elif os_type == "Windows":
        try:
            # Use Mimikatz to extract NTLM hashes
            mimikatz_path = r"C:\Tools\Mimikatz\x64\mimikatz.exe"
            mimikatz_command = f'"{mimikatz_path}" "privilege::debug" "token::elevate" "lsadump::sam" "exit"'

            # Run Mimikatz and save output to a file
            result = subprocess.run(mimikatz_command, capture_output=True, text=True, shell=True)

            print("mimikatz output:\n", result.stdout)
           
            with open(output_path, 'w') as outfile:
                for line in result.stdout.splitlines():
                    if "Hash NTLM" in line:  # Extract NTLM hashes
                        parts = line.split(":")
                        if len(parts) >=2:
                            username = line.split("user : ")[-1].strip() if "user : " in line else "Unknown"
                            hash_value = parts[-1].strip()
                            outfile.write(f"{username}:{hash_value}\n")
                            print(f"Extracted NTLM hash for user: {username}")
                        else:
                            print("unexpected line format: ", line)
            print(f"Hashes successfully extracted to '{output_path}'.")

            crack_format = "NT"

        except FileNotFoundError:
            print("Mimikatz is not installed or accessible. Please ensure it's installed.")
            return
        except Exception as e:
            print("An unexpected error occurred while running Mimikatz:", e)
            return

    else:
        print("Unsupported OS.")
        return
    # Step 2: Run John the Ripper to crack the hashes
    try:
        print("Starting password cracking with John the Ripper...")
        start_time = time.time()
        subprocess.run([
            "john",
            f"--format={crack_format}",
            "--wordlist=/usr/share/wordlists/rockyou.txt" if os_type == "Linux" else "C:\\Tools\\john-1.9.0-jumbo-1-win64\\john-1.9.0-jumbo-1-win64\\run\\rockyou.txt",
            output_path
        ], timeout=60)  # Limit cracking to 60 seconds
        print("Password cracking completed.")

    except subprocess.TimeoutExpired:
        print("Password cracking timed out. Consider using a smaller wordlist.")
    except FileNotFoundError:
        print("John the Ripper is not installed or accessible. Please ensure it's installed.")
    except Exception as e:
        print("An unexpected error occurred while running John the Ripper:", e)
        return

    # Step 3: Check and Display Weak Passwords
    print("Checking for cracked (weak) passwords...")
    try:
        result = subprocess.run(["john", "--show", output_path], capture_output=True, text=True)
        cracked_passwords = result.stdout.strip()

        if cracked_passwords:
            print("Weak passwords detected:")
            print(cracked_passwords)
            print(" warning!!! weak passwords...update and include alphanumeric, special characters! for strong password.")
        else:
            print("No weak passwords detected.")

    except Exception as e:
        print("An unexpected error occurred while displaying cracked passwords:", e)

# Run the function
recheck_hashes()




