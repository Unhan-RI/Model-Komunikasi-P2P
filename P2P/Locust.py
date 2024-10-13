from locust import User, task, between
import socket
import time
import os

class FileTransferUser(User):
    wait_time = between(1, 3)

    @task
    def send_file_task(self):
        host = "192.168.137.182"  # Ganti dengan alamat IP server
        port = 5221             # Ganti dengan port server
        filename = "coba.txt" # Ganti dengan nama file yang ingin dikirim
        
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(30)  # Mengatur timeout menjadi 30 detik
            client_socket.connect((host, port))

            start_time = time.time()
            file_size = os.path.getsize(filename)
            file_info = f"{filename}|{file_size}"
            client_socket.send(file_info.encode())

            with open(filename, 'rb') as file:
                bytes_sent = 0
                while bytes_sent < file_size:
                    chunk = file.read(4096)
                    if not chunk:
                        break
                    client_socket.send(chunk)
                    bytes_sent += len(chunk)

            end_time = time.time()
            response_time = end_time - start_time
            print(f"File {filename} berhasil dikirim ke {host}:{port}.")
            print(f"Waktu respon: {response_time:.2f} detik")

        except (socket.timeout, ConnectionRefusedError) as e:
            print(f"Gagal menghubungkan ke {host}:{port}: {e}")
        finally:
            client_socket.close()
