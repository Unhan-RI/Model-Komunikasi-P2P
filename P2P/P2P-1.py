import socket
import threading
import os
import time
import random

# Fungsi untuk menjalankan server yang menerima file
def run_file_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen(5)
    print(f"Node P2P berjalan sebagai server di port {port}")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Terhubung dengan {addr}")
        threading.Thread(target=receive_file, args=(client_socket,)).start()

# Fungsi untuk menerima file dari node lain
def receive_file(client_socket):
    try:
        start_time = time.time()
        file_info = client_socket.recv(1024).decode()
        if not file_info:
            print("Gagal menerima informasi file, koneksi mungkin terputus.")
            return
        
        try:
            filename, file_size = file_info.split('|')
            file_size = int(file_size)
        except ValueError:
            print(f"Data yang diterima tidak valid untuk informasi file: {file_info}")
            return

        print(f"Menerima file: {filename}")
        print(f"Ukuran file: {file_size} bytes")

        with open(filename, 'wb') as file:
            bytes_received = 0
            while bytes_received < file_size:
                chunk = client_socket.recv(4096)
                if not chunk:
                    print("Koneksi terputus sebelum menerima seluruh file.")
                    break
                file.write(chunk)
                bytes_received += len(chunk)

        end_time = time.time()
        latency = end_time - start_time
        print(f"File {filename} berhasil diterima.")
        print(f"Latency penerimaan: {latency:.2f} detik")

    finally:
        client_socket.close()

# Fungsi untuk mengirim file ke node lain dengan percobaan ulang
def send_file(host, port, filename, retry_attempts=3):
    for attempt in range(retry_attempts):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(30)  # Mengatur timeout menjadi 30 detik
            print(f"Mencoba menghubungkan ke {host}:{port}, Percobaan ke-{attempt + 1}")
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
            throughput = file_size / response_time if response_time > 0 else float('inf')

            print(f"File {filename} berhasil dikirim ke {host}:{port}.")
            print(f"Waktu respon: {response_time:.2f} detik")
            print(f"Throughput: {throughput / 1024:.2f} KB/s")
            return  # Jika berhasil, keluar dari fungsi
        except (socket.timeout, ConnectionRefusedError) as e:
            print(f"Gagal menghubungkan ke {host}:{port}, percobaan ke-{attempt + 1} gagal: {e}")
        finally:
            client_socket.close()

    print(f"Gagal menghubungkan ke {host}:{port} setelah {retry_attempts} percobaan.")

# Fungsi untuk menguji beberapa node secara serentak
def test_multiple_nodes(node_addresses, filename):
    threads = []
    for address in node_addresses:
        host, port = address
        thread = threading.Thread(target=send_file, args=(host, port, filename))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    port = 5000 + random.randint(0, 1000)  # Port unik untuk setiap node
    threading.Thread(target=run_file_server, args=(port,)).start()

    while True:
        command = input("Masukkan perintah ('kirim' untuk mengirim file atau 'uji' untuk uji banyak node, 'exit' untuk keluar): ").strip()
        if command == 'kirim':
            host_tujuan = input("Masukkan alamat IP tujuan: ").strip()
            port_tujuan = int(input("Masukkan port tujuan: ").strip())
            nama_file = input("Masukkan nama file yang akan dikirim: ").strip()
            send_file(host_tujuan, port_tujuan, nama_file)
        elif command == 'uji':
            jumlah_node = int(input("Masukkan jumlah node untuk uji (misalnya 5, 10, 20): ").strip())
            nama_file = input("Masukkan nama file yang akan dikirim ke semua node: ").strip()

            # Membuat daftar alamat IP dan port untuk uji
            node_addresses = [("192.168.0.112", 5000 + i) for i in range(jumlah_node)] #Untuk IP dan Port diganti sesuai dengan IP dan Port tujuan
            test_multiple_nodes(node_addresses, nama_file)
        elif command == 'exit':
            break
