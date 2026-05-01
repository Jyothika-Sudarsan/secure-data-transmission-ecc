import base64
import time
import tracemalloc
from app import TextSteganography  # app.py must define TextSteganography

# Fixed test text (same for both curves)
TEXT = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor "
    "incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis "
    "nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. "
    "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore "
    "eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt "
    "in culpa qui officia deserunt mollit anim id est laborum."
)

# Fixed cover image (same for both curves)
COVER = r"C:\Users\jyoth\OneDrive\Desktop\New folder\lotus .jpg"

# Number of repetitions to average
ITER = 10


def run_tests(curve_name):
    print(f"\nRunning tests for {curve_name} ...")
    steg = TextSteganography(curve_name)

    # Generate receiver key pair once
    priv, pub = steg.generate_key_pair()
    pub_bytes = steg.serialize_public_key(pub)
    pub_b64 = base64.b64encode(pub_bytes)
    key_size = len(pub_bytes)

    enc_times = []
    dec_times = []
    enc_cpu_times = []
    dec_cpu_times = []
    enc_peak_memory = []
    dec_peak_memory = []

    for i in range(ITER):
        # --- Encryption + hide text ---
        tracemalloc.start()
        cpu_start = time.process_time()
        enc_t = steg.hide_text_in_image(
            COVER,
            TEXT,
            base64.b64decode(pub_b64),
            "tmp_stego.png"          # temporary stego image
        )
        cpu_end = time.process_time()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        enc_times.append(enc_t)
        enc_cpu_times.append(cpu_end - cpu_start)
        enc_peak_memory.append(peak / 1024)  # convert bytes -> KB

        # --- Decryption + extract text ---
        tracemalloc.start()
        cpu_start = time.process_time()
        text_out, dec_t = steg.extract_text_from_image("tmp_stego.png", priv)
        cpu_end = time.process_time()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        assert text_out == TEXT, "Decrypted text does not match original!"

        dec_times.append(dec_t)
        dec_cpu_times.append(cpu_end - cpu_start)
        dec_peak_memory.append(peak / 1024)  # KB

        print(f"  Iter {i+1}: enc_time={enc_t:.6f}s cpu={enc_cpu_times[-1]:.6f}s "
              f"mem={enc_peak_memory[-1]:.1f}KB | "
              f"dec_time={dec_t:.6f}s cpu={dec_cpu_times[-1]:.6f}s "
              f"mem={dec_peak_memory[-1]:.1f}KB")

    # --- Compute averages ---
    avg_enc_time = sum(enc_times) / ITER
    avg_dec_time = sum(dec_times) / ITER
    avg_total_time = avg_enc_time + avg_dec_time

    avg_enc_cpu = sum(enc_cpu_times) / ITER
    avg_dec_cpu = sum(dec_cpu_times) / ITER
    avg_total_cpu = avg_enc_cpu + avg_dec_cpu

    avg_enc_mem = sum(enc_peak_memory) / ITER
    avg_dec_mem = sum(dec_peak_memory) / ITER
    avg_total_mem = avg_enc_mem + avg_dec_mem

    print(f"\n{curve_name} averages over {ITER} runs:")
    print(f"  Avg enc wall time : {avg_enc_time:.6f} s")
    print(f"  Avg dec wall time : {avg_dec_time:.6f} s")
    print(f"  Avg total wall time: {avg_total_time:.6f} s")
    print(f"  Avg enc CPU time  : {avg_enc_cpu:.6f} s")
    print(f"  Avg dec CPU time  : {avg_dec_cpu:.6f} s")
    print(f"  Avg total CPU time: {avg_total_cpu:.6f} s")
    print(f"  Avg enc peak mem  : {avg_enc_mem:.1f} KB")
    print(f"  Avg dec peak mem  : {avg_dec_mem:.1f} KB")
    print(f"  Avg total peak mem: {avg_total_mem:.1f} KB")
    print(f"  Public key size   : {key_size} bytes")

    return {
        "enc_time": avg_enc_time,
        "dec_time": avg_dec_time,
        "total_time": avg_total_time,
        "enc_cpu": avg_enc_cpu,
        "dec_cpu": avg_dec_cpu,
        "total_cpu": avg_total_cpu,
        "enc_mem": avg_enc_mem,
        "dec_mem": avg_dec_mem,
        "total_mem": avg_total_mem,
        "pub_key_size": key_size
    }


if __name__ == "__main__":
    curve_stats = run_tests("curve25519")
    secp_stats = run_tests("secp256r1")

    print("\n===== FINAL SUMMARY =====")
    print("Curve25519:")
    for k, v in curve_stats.items():
        if "mem" in k:
            print(f"  {k} : {v:.1f} KB")
        elif "size" in k:
            print(f"  {k} : {v} bytes")
        else:
            print(f"  {k} : {v:.6f} s")

    print("\nsecp256r1:")
    for k, v in secp_stats.items():
        if "mem" in k:
            print(f"  {k} : {v:.1f} KB")
        elif "size" in k:
            print(f"  {k} : {v} bytes")
        else:
            print(f"  {k} : {v:.6f} s")
