import os
import sys

# Thư viện để bắt phím theo thời gian thực trên Windows
try:
    import msvcrt
    HAS_MSVCRT = True
except ImportError:
    HAS_MSVCRT = False

def passwordHandler(prompt="Enter seed number: "): #passwordHandler
    """Replaces real password with stars"""
    print(prompt, end="", flush=True)
    seed_chars = []
    
    if HAS_MSVCRT and sys.platform == 'win32':
        while True:
            ch = msvcrt.getch()
            if ch in b'\r' or ch in b'\n':
                print()
                break
            elif ch == b'\x08':
                if seed_chars:
                    seed_chars.pop()
                    # Xóa dấu sao trên màn hình terminal
                    sys.stdout.write('\b \b')
                    sys.stdout.flush()
            elif ch in b'\x00' or ch in b'\xe0':
                msvcrt.getch() # Đọc bỏ mã phụ
            else:
                try:
                    char_str = ch.decode('utf-8')
                    seed_chars.append(char_str)
                    sys.stdout.write('*')
                    sys.stdout.flush()
                except UnicodeDecodeError:
                    pass
        return "".join(seed_chars)
    else:
        # Fallback for others Oses when no msvcrt
        import getpass
        pwd = getpass.getpass("")
        print("*" * len(pwd))
        return pwd

def encoding(message, passcode):
    encrypted = []
    for i, char in enumerate(message):
        key_char = passcode[i % len(passcode)]
        encrypted.append(chr(ord(char) ^ ord(key_char)))
    return ''.join(encrypted).encode('utf-8').hex()

def decoding(hex_message, passcode): 
    try:
        decoded_bytes = bytes.fromhex(hex_message.strip())
        decoded_str = decoded_bytes.decode('utf-8')
        decrypted = []
        for i, char in enumerate(decoded_str):
            key_char = passcode[i % len(passcode)]
            decrypted.append(chr(ord(char) ^ ord(key_char)))
        return ''.join(decrypted)
    except Exception:
        return None

def binaryEncoding(file_path, passcode):
    ext = os.path.splitext(file_path)[1].lower()
    header = f"[EXT:{ext}]".encode('utf-8')
    
    with open(file_path, 'rb') as f:
        file_bytes = f.read()
    
    full_data = header + file_bytes
    passcode_bytes = passcode.encode('utf-8')
    encrypted_bytes = bytearray()
    
    for i, b in enumerate(full_data):
        key_byte = passcode_bytes[i % len(passcode_bytes)]
        encrypted_bytes.append(b ^ key_byte)
        
    return encrypted_bytes.hex()

def binaryDecoding(hex_data, passcode): 
    try:
        file_bytes = bytes.fromhex(hex_data.strip())
        passcode_bytes = passcode.encode('utf-8')
        decrypted_bytes = bytearray()
        
        for i, b in enumerate(file_bytes):
            key_byte = passcode_bytes[i % len(passcode_bytes)]
            decrypted_bytes.append(b ^ key_byte)
            
        try:
            header_end = decrypted_bytes.index(b']') + 1
            header = decrypted_bytes[:header_end].decode('utf-8')
            actual_content = decrypted_bytes[header_end:]
            
            if header.startswith('[EXT:') and header.endswith(']'):
                ext = header[5:-1]
            else:
                ext = ".bin"
        except Exception:
            ext = ".bin"
            actual_content = decrypted_bytes
            
        return actual_content, ext
    except Exception:
        return None, None

def main():
    print("-" * 50)
    
    while True:
        try:
            user_input = input("> ").strip()
            if not user_input:
                continue
                
            parts = user_input.split()
            command = parts[0].lower()
            
            if command == 'exit':
                break
                
            elif command == 'help':
                print("""
Available commands:")
encode [<seed> <message>]     | Encrypt text
decode [<seed> <hex>]         | Decrypt text
encode-file [<seed> <path>]   | Encrypt file
decode-file [<seed> <path>]   | Decrypt file
exit                          | Quit terminal")

NOTE: Seed containing space is not recommended when not running as standalone

""")
                continue
                
            elif command == 'encode':
                if len(parts) >= 3:
                    seed = parts[1]
                    message = ' '.join(parts[2:])
                else:
                    seed = passwordHandler("Seed number: ")
                    message = input("Message: ")
                
                result = encoding(message, seed)
                print(f"\n[RESULT HERE]\n{result}\n")
                
            elif command == 'decode':
                if len(parts) >= 3:
                    seed = parts[1]
                    encoded_msg = parts[2]
                else:
                    seed = passwordHandler("Seed: ")
                    encoded_msg = input("Message: ")
                
                result = decoding(encoded_msg, seed)
                print("\n[RESULT HERE]")
                if result is not None:
                    print(f"{result}\n")
                else:
                    print("Wrong seed or file is already corrupted\n")
                    
            elif command in ['encode-file', 'file-encode']:
                if len(parts) >= 3:
                    seed = parts[1]
                    file_path = parts[2].strip('"')
                else:
                    seed = passwordHandler("Seed: ")
                    file_path = input("You can drag a file here, as terminal will translate it into path: ").strip('"')
                
                if not os.path.exists(file_path):
                    print(f"Error: File not found\n")
                    continue
                
                encoded_hex = binaryEncoding(file_path, seed)
                
                dir_name = os.path.dirname(file_path)
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                output_path = os.path.join(dir_name, f"{base_name}_encoded.txt")
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(encoded_hex)
                    
                print(f"\n[RESULT HERE]\nSaved to:\n{output_path}\n")
                
            elif command in ['decode-file', 'file-decode']:
                if len(parts) >= 3:
                    seed = parts[1]
                    file_path = parts[2].strip('"')
                else:
                    seed = passwordHandler("Seed: ")
                    file_path = input("You can drag a file here, as terminal will translate it into path: ").strip('"')
                
                if not os.path.exists(file_path):
                    print(f"Error: File not found\n")
                    continue
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    hex_data = f.read()
                
                decrypted_bytes, ext = binaryDecoding(hex_data, seed)
                if decrypted_bytes is None:
                    print("\n[RESULT HERE]\nError: Wrong seed or file is already corrupted\n")
                    continue
                
                dir_name = os.path.dirname(file_path)
                base_name = os.path.basename(file_path).replace('_encoded', '')
                base_name = os.path.splitext(base_name)[0]
                output_path = os.path.join(dir_name, f"{base_name}_restored{ext}")
                
                with open(output_path, 'wb') as f:
                    f.write(decrypted_bytes)
                    
                print(f"\n[RESULT HERE]\nDecoded and saved as '{ext}' at:\n{output_path}\n")
                
            else:
                print(f"command not supported\n")
                
        except (KeyboardInterrupt, EOFError):
            breaks

if __name__ == "__main__":
    main()