import base64
import time
import tracemalloc
from app import ImageSteganography  # app.py must define ImageSteganography

SECRET_IMG = r"C:\Users\jyoth\OneDrive\Desktop\PROJECT\car_imresizer.jpg"
COVER_IMG  = r"C:\Users\jyoth\OneDrive\Desktop\PROJECT\final-image.jpg"
ITER = 5

def run_tests(curve_name):
    print(f"\nRunning IMAGE tests for {curve_name} ...")
    steg = ImageSteganography(curve_name)

    priv, pub = steg.generate_key_pair()
    pub_bytes = steg.serialize_public_key(pub)
    pub_b64 = base64.b64encode(pub_bytes)

    enc_times, dec_times = [], []
    enc_cpu_times, dec_cpu_times = [], []
    enc_mems, dec_mems = [], []

    for i in range(ITER):
        # Encrypt
        tracemalloc.start()
        start_cpu = time.process_time()
        start_wall = time.time()

        enc_t = steg.hide_image_in_image(
            COVER_IMG,
            SECRET_IMG,
            base64.b64decode(pub_b64),
            "tmp_image_stego.png",
        )

        enc_wall = time.time() - start_wall
        enc_cpu = time.process_time() - start_cpu
        enc_mem = tracemalloc.get_traced_memory()[1] / 1024
        tracemalloc.stop()

        enc_times.append(enc_wall)
        enc_cpu_times.append(enc_cpu)
        enc_mems.append(enc_mem)

        # Decrypt
        tracemalloc.start()
        start_cpu = time.process_time()
        start_wall = time.time()

        _, dec_t = steg.extract_image_from_image("tmp_image_stego.png", priv)

        dec_wall = time.time() - start_wall
        dec_cpu = time.process_time() - start_cpu
        dec_mem = tracemalloc.get_traced_memory()[1] / 1024
        tracemalloc.stop()

        dec_times.append(dec_wall)
        dec_cpu_times.append(dec_cpu)
        dec_mems.append(dec_mem)

        print(f"Iter {i+1}: enc={enc_wall:.6f}s cpu={enc_cpu:.6f}s mem={enc_mem:.1f}KB | "
              f"dec={dec_wall:.6f}s cpu={dec_cpu:.6f}s mem={dec_mem:.1f}KB")

    # Averages
    avg_enc = sum(enc_times)/ITER
    avg_dec = sum(dec_times)/ITER
    avg_total = avg_enc + avg_dec

    avg_enc_cpu = sum(enc_cpu_times)/ITER
    avg_dec_cpu = sum(dec_cpu_times)/ITER
    avg_total_cpu = avg_enc_cpu + avg_dec_cpu

    avg_enc_mem = sum(enc_mems)/ITER
    avg_dec_mem = sum(dec_mems)/ITER
    avg_total_mem = avg_enc_mem + avg_dec_mem

    pub_key_size = len(pub_bytes)

    print(f"\n{curve_name} IMAGE averages over {ITER} runs:")
    print(f"  Avg enc wall time : {avg_enc:.6f} s")
    print(f"  Avg dec wall time : {avg_dec:.6f} s")
    print(f"  Avg total wall time: {avg_total:.6f} s")
    print(f"  Avg enc CPU time  : {avg_enc_cpu:.6f} s")
    print(f"  Avg dec CPU time  : {avg_dec_cpu:.6f} s")
    print(f"  Avg total CPU time: {avg_total_cpu:.6f} s")
    print(f"  Avg enc peak mem  : {avg_enc_mem:.1f} KB")
    print(f"  Avg dec peak mem  : {avg_dec_mem:.1f} KB")
    print(f"  Avg total peak mem: {avg_total_mem:.1f} KB")
    print(f"  Public key size   : {pub_key_size} bytes")

    return avg_enc, avg_dec, avg_total

if __name__ == "__main__":
    curve_enc, curve_dec, curve_total = run_tests("curve25519")
    secp_enc, secp_dec, secp_total = run_tests("secp256r1")

    print("\n===== FINAL IMAGE SUMMARY (same secret & cover) =====")
    print(f"Curve25519  -> enc={curve_enc:.6f}s  dec={curve_dec:.6f}s  total={curve_total:.6f}s")
    print(f"secp256r1   -> enc={secp_enc:.6f}s  dec={secp_dec:.6f}s  total={secp_total:.6f}s")
